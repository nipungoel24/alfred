import { useEffect, useState } from 'react';
import { Sparkles, RefreshCw, FileText } from 'lucide-react';

type GateState = 'starting' | 'error' | 'ready';

/**
 * Blocks the workspace until the local backend answers health.
 *
 * Under Tauri, `initApi()` calls the durable `await_backend_ready` Rust
 * command which blocks until the BackendSupervisor confirms the sidecar
 * is healthy or fails. No polling, no events, no retry loops.
 */
export function StartupGate({
  initPromise,
  children,
}: {
  initPromise: Promise<void>;
  children: React.ReactNode;
}) {
  const [state, setState] = useState<GateState>('starting');
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    initPromise
      .then(() => {
        if (!cancelled) setState('ready');
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : String(err);
        setErrorMsg(msg);
        setState('error');
      });
    return () => {
      cancelled = true;
    };
  }, [initPromise]);

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
              Diagnostic code: <span className="startup-code">{errorMsg}</span>
            </p>
            <p className="startup-logs">
              <FileText size={12} aria-hidden="true" />
              Logs: %LOCALAPPDATA%\AlfredData\logs
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setState('starting');
                setErrorMsg('');
                // Retry: re-invoke await_backend_ready
                void (async () => {
                  try {
                    const { invoke } = await import('@tauri-apps/api/core');
                    await invoke('restart_backend');
                    const { invoke: invoke2 } = await import('@tauri-apps/api/core');
                    const info = await invoke2<{ port: number; token: string }>('await_backend_ready');
                    const { setApiCredentials } = await import('../api/client');
                    setApiCredentials(info.port, info.token);
                    setState('ready');
                  } catch (err: unknown) {
                    const msg = err instanceof Error ? err.message : String(err);
                    setErrorMsg(msg);
                    setState('error');
                  }
                })();
              }}
            >
              <RefreshCw size={14} aria-hidden="true" />
              Retry
            </button>
          </>
        )}
      </div>
    </div>
  );
}
