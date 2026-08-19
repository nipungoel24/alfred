import { useEffect, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Sparkles, RefreshCw } from 'lucide-react';
import { health } from '../api/emails';

type GateState = 'starting' | 'error' | 'ready';

/**
 * Blocks the workspace until the local backend answers health.
 * Under Tauri, Retry re-asks the shell to (re)spawn the sidecar.
 */
export function StartupGate({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<GateState>('starting');
  const [attempt, setAttempt] = useState(0);

  const healthQuery = useQuery({
    queryKey: ['health', 'gate'],
    queryFn: health,
    retry: false,
    refetchInterval: state === 'starting' ? 800 : false,
    staleTime: 0,
  });

  useEffect(() => {
    if (healthQuery.isSuccess) {
      setState('ready');
      return;
    }
    if (healthQuery.isError && state === 'starting' && attempt < 12) {
      const t = setTimeout(() => setAttempt(a => a + 1), 700);
      return () => clearTimeout(t);
    }
    if (healthQuery.isError && state === 'starting' && attempt >= 12) {
      setState('error');
    }
  }, [healthQuery.isSuccess, healthQuery.isError, state, attempt]);

  if (state === 'ready') return <>{children}</>;

  const retry = async () => {
    if ('__TAURI_INTERNALS__' in window) {
      try {
        const { invoke } = await import('@tauri-apps/api/core');
        await invoke('retry_backend');
      } catch {
        /* fall through to refetch */
      }
    }
    setAttempt(0);
    setState('starting');
    void queryClient.invalidateQueries({ queryKey: ['health'] });
  };

  return (
    <div className="startup-gate" role="status" aria-live="polite">
      <div className="startup-gate-inner">
        <div className="startup-mark" aria-hidden="true">
          <Sparkles size={22} />
        </div>
        {state === 'starting' ? (
          <>
            <h1 className="startup-title">Starting Alfred…</h1>
            <p className="startup-sub">Waking the local inbox service.</p>
            <div className="startup-progress"><span className="startup-bar" /></div>
          </>
        ) : (
          <>
            <h1 className="startup-title">Alfred couldn't start its local service.</h1>
            <p className="startup-sub">
              The local backend didn't become ready. Your data is untouched — retry to try again.
            </p>
            <button type="button" className="btn btn-primary" onClick={retry}>
              <RefreshCw size={14} aria-hidden="true" />
              Retry
            </button>
          </>
        )}
      </div>
    </div>
  );
}
