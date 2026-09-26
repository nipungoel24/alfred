import { useCallback, useEffect, useState } from 'react';
import { RefreshCw, FileText, AlertTriangle } from 'lucide-react';
import {
  STARTUP_PHASE_EVENT,
  StartupError,
  fetchStartupDiagnostics,
  fetchStartupStatus,
  isTauriRuntime,
  retryStartup,
  type StartupPhase,
  type StartupStatus,
} from '../api/client';

/** Human sentence per startup phase. Never a raw exception string. */
const PHASE_COPY: Record<StartupPhase, { title: string; body: string }> = {
  BOOT: { title: 'Starting Alfred', body: 'Preparing to launch.' },
  INITIALIZING: { title: 'Starting Alfred', body: 'Preparing your workspace.' },
  STARTING_BACKEND: { title: 'Starting Alfred', body: 'Launching the local inbox service.' },
  WAITING_FOR_BACKEND: {
    title: 'Starting Alfred',
    body: 'Waiting for the local inbox service to respond.',
  },
  CHECKING_DATABASE: { title: 'Starting Alfred', body: 'Opening your local mailbox.' },
  CHECKING_AI_RUNTIME: { title: 'Starting Alfred', body: 'Checking your local AI runtime.' },
  CHECKING_MODEL: { title: 'Starting Alfred', body: 'Checking the local model.' },
  RESTORING_SESSION: { title: 'Starting Alfred', body: 'Restoring your connected accounts.' },
  READY: { title: 'Starting Alfred', body: 'Finishing up.' },
  RECOVERY: { title: 'Starting Alfred', body: 'Finishing up.' },
  FATAL_ERROR: { title: "Alfred couldn't start", body: '' },
};

/** Phases shown as completed steps in the progress list. */
const STEP_ORDER: StartupPhase[] = [
  'INITIALIZING',
  'STARTING_BACKEND',
  'WAITING_FOR_BACKEND',
  'CHECKING_DATABASE',
  'CHECKING_AI_RUNTIME',
  'CHECKING_MODEL',
  'RESTORING_SESSION',
];

const STEP_LABELS: Record<string, string> = {
  INITIALIZING: 'Preparing workspace',
  STARTING_BACKEND: 'Starting local service',
  WAITING_FOR_BACKEND: 'Waiting for local service',
  CHECKING_DATABASE: 'Opening mailbox',
  CHECKING_AI_RUNTIME: 'Checking local AI',
  CHECKING_MODEL: 'Checking local model',
  RESTORING_SESSION: 'Restoring accounts',
};

type GateState = 'starting' | 'error' | 'ready';

export interface StartupGateProps {
  initPromise: Promise<void>;
  children: React.ReactNode;
  /** Injectable for tests. Defaults to the Tauri runtime. */
  tauri?: boolean;
}

/**
 * Turn any thrown value into a user-facing failure.
 *
 * A raw exception string is never used as the message. If the shell did not
 * send a structured envelope, the user gets a fixed, honest sentence and the
 * diagnostic code; the raw detail belongs in the log file, not on screen.
 */
function toStartupError(err: unknown): StartupError {
  if (err instanceof StartupError) return err;
  return new StartupError(
    'UNEXPECTED_STARTUP_FAILURE',
    'Alfred could not finish starting, and did not report a specific reason. ' +
      'Your mail and settings are untouched. Try again, and if it keeps happening, ' +
      'reinstall Alfred or report the diagnostic code with the contents of the log file.',
    true,
  );
}

/**
 * Blocks the workspace until the local backend is genuinely serving.
 *
 * Under Tauri, `initApi()` calls the durable `await_backend_ready` Rust
 * command, which resolves only on a real protocol-level handshake. This
 * component additionally follows the shell's `alfred://startup-phase` events
 * so the user sees which step is actually running, and renders the shell's
 * diagnostic code and guidance on failure.
 *
 * Retry is bounded and cancellable. It is never an unbounded loop.
 */
export function StartupGate({ initPromise, children, tauri }: StartupGateProps) {
  const isTauri = tauri ?? isTauriRuntime();
  const [state, setState] = useState<GateState>('starting');
  const [error, setError] = useState<StartupError | null>(null);
  const [status, setStatus] = useState<StartupStatus | null>(null);
  const [logPath, setLogPath] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let unlisten: (() => void) | undefined;
    let cancelledLocal = false;

    if (isTauri) {
      // Authoritative snapshot first, so a fast transition is never missed.
      void fetchStartupStatus()
        .then((snapshot) => {
          if (!cancelledLocal && snapshot) setStatus(snapshot);
        })
        .catch(() => {
          /* the gate promise is the source of truth for pass/fail */
        });

      void (async () => {
        try {
          const { listen } = await import('@tauri-apps/api/event');
          const stop = await listen<StartupStatus>(STARTUP_PHASE_EVENT, (event) => {
            if (!cancelledLocal) setStatus(event.payload);
          });
          if (cancelledLocal) {
            stop();
          } else {
            unlisten = stop;
          }
        } catch {
          /* events are an enhancement; the gate promise still resolves */
        }
      })();

      void fetchStartupDiagnostics()
        .then((diag) => {
          if (!cancelledLocal && diag) setLogPath(diag.log_path);
        })
        .catch(() => {
          /* the log path has a documented default below */
        });
    }

    initPromise
      .then(() => {
        if (!cancelledLocal) setState('ready');
      })
      .catch((err: unknown) => {
        if (cancelledLocal) return;
        setError(toStartupError(err));
        setState('error');
      });

    return () => {
      cancelledLocal = true;
      unlisten?.();
    };
  }, [initPromise, isTauri]);

  /**
   * Bounded, cancellable retry. One attempt per click: never an automatic
   * loop, so a permanently broken backend cannot spin.
   */
  const retry = useCallback(() => {
    setState('starting');
    setError(null);
    setStatus(null);
    setAttempt((n) => n + 1);
    if (!isTauri) return;
    void retryStartup()
      .then(() => {
        setState('ready');
      })
      .catch((err: unknown) => {
        setError(toStartupError(err));
        setState('error');
      });
  }, [isTauri]);

  if (state === 'ready') return <>{children}</>;

  if (state === 'error') {
    const code = error?.code ?? 'UNKNOWN';
    const guidance =
      error?.guidance ||
      'Alfred could not finish starting. Your mail and settings are untouched.';
    const logLocation = logPath ?? '%LOCALAPPDATA%\\AlfredData\\logs\\desktop.log';
    return (
      <div className="startup-gate" role="alert">
        <div className="startup-gate-inner startup-gate-inner--error">
          <div className="startup-mark startup-mark--error" aria-hidden="true">
            <AlertTriangle size={22} />
          </div>
          <h1 className="startup-title">Alfred couldn&apos;t start</h1>
          <p className="startup-sub">{guidance}</p>
          <p className="startup-diagnostic">
            Diagnostic code: <span className="startup-code">{code}</span>
          </p>
          <p className="startup-logs">
            <FileText size={12} aria-hidden="true" />
            Log file: <span className="startup-logpath">{logLocation}</span>
          </p>
          {attempt > 0 && (
            <p className="startup-sub startup-sub--muted">
              Retried {attempt} {attempt === 1 ? 'time' : 'times'}. If this keeps
              happening, reinstall Alfred or report the diagnostic code above.
            </p>
          )}
          <div className="startup-actions">
            <button type="button" className="btn btn-primary" onClick={retry}>
              <RefreshCw size={14} aria-hidden="true" />
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const phase = status?.phase ?? 'INITIALIZING';
  const copy = PHASE_COPY[phase] ?? PHASE_COPY.INITIALIZING;
  const activeIndex = STEP_ORDER.indexOf(phase);

  return (
    <div className="startup-gate" role="status" aria-live="polite">
      <div className="startup-gate-inner">
        <div className="startup-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none" width="22" height="22">
            <path d="M16 7 L24 25 H20.2 L16 14.6 L11.8 25 H8 Z" fill="currentColor" />
            <path
              d="M12.4 20.4 H19.6"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              opacity="0.55"
            />
          </svg>
        </div>
        <h1 className="startup-title">{copy.title}</h1>
        <p className="startup-sub">{copy.body}</p>
        <ol className="startup-steps">
          {STEP_ORDER.map((step, index) => {
            const state = index < activeIndex ? 'done' : index === activeIndex ? 'active' : 'todo';
            return (
              <li key={step} className="startup-step" data-state={state}>
                <span className="startup-step-dot" aria-hidden="true" />
                <span className="startup-step-label">{STEP_LABELS[step]}</span>
                <span className="sr-only">
                  {state === 'done' ? ' — done' : state === 'active' ? ' — in progress' : ''}
                </span>
              </li>
            );
          })}
        </ol>
        <div className="startup-progress" aria-hidden="true">
          <span className="startup-bar" />
        </div>
      </div>
    </div>
  );
}
