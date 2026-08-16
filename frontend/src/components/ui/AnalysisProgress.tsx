import { useEffect, useState, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';

type ProgressEvent = 
  | { type: 'status'; pending: number }
  | { type: 'analysis_complete'; email_id: string; cached: boolean; pending: number; total_ms?: number }
  | { type: 'analysis_error'; email_id: string; error: string; pending: number }
  | { type: 'worker_paused'; reason: string; pending: number }
  | { type: 'heartbeat'; pending: number }
  | { type: 'jobs_enqueued'; count: number; pending: number };

export function AnalysisProgress() {
  const [pending, setPending] = useState(0);
  const [latestEvent, setLatestEvent] = useState<ProgressEvent | null>(null);
  const queryClient = useQueryClient();
  const invalidationTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const eventSource = new EventSource('http://127.0.0.1:8765/api/analysis/progress');

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressEvent = JSON.parse(event.data);
        setPending(data.pending);
        if (data.type !== 'heartbeat' && data.type !== 'status' && data.type !== 'jobs_enqueued') {
          setLatestEvent(data);
          
          // Debounce invalidations to prevent backend request storms during fast processing
          if (!invalidationTimer.current) {
            invalidationTimer.current = setTimeout(() => {
              queryClient.invalidateQueries({ queryKey: ['emails'] });
              queryClient.invalidateQueries({ queryKey: ['tasks'] });
              queryClient.invalidateQueries({ queryKey: ['briefing'] });
              invalidationTimer.current = null;
            }, 1000);
          }
        }
      } catch (err) {
        console.error('Failed to parse SSE event', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [queryClient]);

  if (pending === 0) return null;

  return (
    <div className="analysis-progress-bar">
      <div className="progress-spinner"></div>
      <div className="progress-text">
        <strong>Analyzing {pending} emails in background...</strong>
        {latestEvent?.type === 'analysis_complete' && (
          <span className="text-muted"> (Last: {latestEvent.total_ms}ms)</span>
        )}
        {latestEvent?.type === 'analysis_error' && (
          <span className="text-danger"> (Error: {latestEvent.error})</span>
        )}
      </div>
    </div>
  );
}
