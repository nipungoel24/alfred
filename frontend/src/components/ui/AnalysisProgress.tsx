import { useEffect, useRef } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { sseUrl } from '../../api/client';
import { analysisStatus, analysisRetry } from '../../api/emails';

type ProgressEvent =
  | { type: 'status'; pending: number }
  | { type: 'analysis_complete'; email_id: string; cached: boolean; pending: number; total_ms?: number }
  | { type: 'analysis_error'; email_id: string; error: string; pending: number }
  | { type: 'analysis_cancelled'; email_id: string; pending: number }
  | { type: 'ai_state'; state: string; pending: number }
  | { type: 'heartbeat'; pending: number }
  | { type: 'jobs_enqueued'; count: number; pending: number };

export function AnalysisProgress() {
  const queryClient = useQueryClient();
  const invalidationTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: status } = useQuery({
    queryKey: ['analysisStatus'],
    queryFn: analysisStatus,
    refetchInterval: 10_000,
    staleTime: 5_000,
  });

  const retryMutation = useMutation({
    mutationFn: analysisRetry,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['analysisStatus'] });
    },
  });

  useEffect(() => {
    const eventSource = new EventSource(sseUrl('/api/analysis/progress'));

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressEvent = JSON.parse(event.data);
        if (data.type === 'ai_state') {
          void queryClient.invalidateQueries({ queryKey: ['analysisStatus'] });
          void queryClient.invalidateQueries({ queryKey: ['health'] });
          return;
        }
        if (data.type !== 'heartbeat' && data.type !== 'status' && data.type !== 'jobs_enqueued') {
          void queryClient.invalidateQueries({ queryKey: ['analysisStatus'] });

          // Debounce invalidations to prevent backend request storms during fast processing
          if (!invalidationTimer.current) {
            invalidationTimer.current = setTimeout(() => {
              queryClient.invalidateQueries({ queryKey: ['emails'] });
              queryClient.invalidateQueries({ queryKey: ['emailCounts'] });
              queryClient.invalidateQueries({ queryKey: ['tasks'] });
              queryClient.invalidateQueries({ queryKey: ['briefing'] });
              invalidationTimer.current = null;
            }, 1000);
          }
        }
      } catch {
        /* malformed SSE payload — ignore */
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [queryClient]);

  if (!status) return null;

  const { state, pending } = status;

  // Ready with nothing to do — stay out of the way entirely.
  if (state === 'ready' && pending === 0) return null;

  const showSpinner = state === 'ready' && pending > 0;

  let label: string;
  let tone: 'working' | 'paused' | 'error' = 'paused';
  let showRetry = false;

  switch (state) {
    case 'ready':
      label = `Analyzing ${pending} messages · Local AI ready`;
      tone = 'working';
      break;
    case 'initializing':
      label = 'Local AI starting…';
      break;
    case 'ollama_not_running':
      label = `Local AI offline${pending > 0 ? ` · ${pending} analyses queued` : ''}`;
      showRetry = true;
      break;
    case 'model_missing':
      label = `${status.model} needs to be installed${pending > 0 ? ` · ${pending} analyses queued` : ''}`;
      showRetry = true;
      break;
    case 'temporarily_unavailable':
      label = `Local AI temporarily unavailable${pending > 0 ? ` · ${pending} analyses queued` : ''}`;
      showRetry = true;
      break;
    case 'recovering':
      label = 'Local AI recovering…';
      break;
    case 'error':
      label = `Local AI error${pending > 0 ? ` · ${pending} analyses queued` : ''}`;
      tone = 'error';
      showRetry = true;
      break;
    default:
      label = `Local AI starting…`;
  }

  return (
    <div className={`analysis-progress-bar tone-${tone}`} role="status" aria-live="polite">
      {showSpinner && <div className="progress-spinner" aria-hidden="true" />}
      {!showSpinner && <span className="status-dot offline" aria-hidden="true" />}
      <div>
        <strong>{label}</strong>
        {status.detail && <span className="text-muted"> ({status.detail})</span>}
      </div>
      {showRetry && (
        <button
          type="button"
          className="progress-retry"
          onClick={() => retryMutation.mutate()}
          disabled={retryMutation.isPending}
        >
          Retry
        </button>
      )}
    </div>
  );
}
