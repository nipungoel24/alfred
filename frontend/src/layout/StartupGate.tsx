import { useCallback, useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Sparkles, RefreshCw, FileText } from 'lucide-react';
import { health } from '../api/emails';
import { initApi } from '../api/client';

type GateState = 'starting' | 'error' | 'ready';

/** Aligned with the desktop shell's own readiness budget (45s). */
const POLL_MS = 800;
const MAX_FAILED_POLLS = Math.ceil(45_000 / POLL_MS);

/**
 * Blocks the workspace until the local backend answers health.
 * Under Tauri, Retry re-resolves the runtime endpoint (which the shell
 * may have (re)spawned) and then re-polls — never killing a healthy
 * backend, never requiring a full app restart.
 */
export function StartupGate({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<GateState>('starting');
  const [lastError, setLastError] = useState<string>('BACKEND_STARTING');
  const failedPolls = useRef<number>(0);

  useEffect(() => {
    if (state !== 'starting') return;
    const timer = setInterval(() => {
      void queryClient
        .fetchQuery({
          queryKey: ['health', 'gate'],
          queryFn: health,
          retry: false,
          staleTime: 0,
        })
        .then(() => {
          failedPolls.current = 0;
          setState('ready');
        })
        .catch((err: unknown) => {
          const msg = err instanceof Error ? err.message : '';
          if (/401|session token/i.test(msg)) setLastError('BACKEND_UNAUTHORIZED');
          failedPolls.current += 1;
          if (failedPolls.current >= MAX_FAILED_POLLS) {
            setLastError(prev =>
              prev === 'BACKEND_UNAUTHORIZED' ? prev : 'BACKEND_TIMEOUT');
            setState('error');
          }
        });
    }, POLL_MS);
    return () => clearInterval(timer);
  }, [state, queryClient]);

  const retry = useCallback(async () => {
    failedPolls.current = 0;
    setLastError('BACKEND_STARTING');
    if ('__TAURI_INTERNALS__' in window) {
      try {
        const { invoke } = await import('@tauri-apps/api/core');
        await invoke('retry_backend');
      } catch {
        /* shell will log; fall through to re-init + refetch */
      }
    }
    await initApi(20, 400);
    setState('starting');
  }, []);

  if (state === 'ready') return <>{children}</>;

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
            <p className="startup-diagnostic">
              Diagnostic code: <span className="startup-code">{lastError}</span>
            </p>
            <p className="startup-logs">
              <FileText size={12} aria-hidden="true" />
              Logs: %LOCALAPPDATA%\AlfredData\logs
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
