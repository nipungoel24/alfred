import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StartupGate } from './StartupGate';
import {
  STARTUP_PHASE_EVENT,
  StartupError,
  fetchStartupDiagnostics,
  fetchStartupStatus,
  retryStartup,
  type StartupStatus,
} from '../api/client';

const listen = vi.fn(async () => () => {});

vi.mock('@tauri-apps/api/event', () => ({
  listen: (...args: unknown[]) => listen(...(args as [])),
}));

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>();
  return {
    ...actual,
    initApi: vi.fn(async () => {}),
    setApiCredentials: vi.fn(),
    retryStartup: vi.fn(async () => {}),
    fetchStartupStatus: vi.fn(async () => null),
    fetchStartupDiagnostics: vi.fn(async () => null),
    isTauriRuntime: vi.fn(() => true),
  };
});

function client() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
}

function renderGate(initPromise?: Promise<void>, tauri = true) {
  const promise = initPromise ?? Promise.resolve();
  return render(
    <QueryClientProvider client={client()}>
      <StartupGate initPromise={promise} tauri={tauri}>
        <div>workspace-content</div>
      </StartupGate>
    </QueryClientProvider>,
  );
}

async function flush() {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
  });
}

function statusFor(phase: StartupStatus['phase']): StartupStatus {
  return {
    phase,
    code: 'NONE',
    detail: '',
    guidance: '',
    ready: false,
    degraded: false,
    phase_elapsed_ms: 0,
    build: 'abc1234',
    version: '0.1.0',
  };
}

describe('StartupGate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listen.mockResolvedValue(() => {});
    vi.mocked(fetchStartupStatus).mockResolvedValue(null);
    vi.mocked(fetchStartupDiagnostics).mockResolvedValue(null);
    vi.mocked(retryStartup).mockResolvedValue(undefined);
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows a starting state and releases the workspace when the backend is ready', async () => {
    renderGate();
    expect(screen.getByRole('heading', { name: /Starting Alfred/ })).toBeInTheDocument();
    await flush();
    expect(screen.getByText('workspace-content')).toBeInTheDocument();
  });

  it('names each startup step so the user can see what is running', async () => {
    renderGate(new Promise(() => {}));
    expect(screen.getByText('Starting local service')).toBeInTheDocument();
    expect(screen.getByText('Opening mailbox')).toBeInTheDocument();
    expect(screen.getByText('Restoring accounts')).toBeInTheDocument();
  });

  it('does not render the workspace before the backend is ready', async () => {
    renderGate(new Promise(() => {}));
    await flush();
    expect(screen.queryByText('workspace-content')).not.toBeInTheDocument();
  });

  it('is a polite live region while starting', async () => {
    renderGate(new Promise(() => {}));
    expect(screen.getByRole('status')).toHaveAttribute('aria-live', 'polite');
  });

  it('renders the diagnostic code and guidance from the failure envelope', async () => {
    renderGate(
      Promise.reject(
        new StartupError('BACKEND_HEALTH_TIMEOUT', 'The local service did not respond.', true),
      ),
    );
    await flush();
    expect(screen.getByRole('heading', { name: /couldn't start/i })).toBeInTheDocument();
    expect(screen.getByText('BACKEND_HEALTH_TIMEOUT')).toBeInTheDocument();
    expect(screen.getByText(/did not respond/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Try again/ })).toBeInTheDocument();
  });

  it('surfaces the credential-store failure with its own wording', async () => {
    renderGate(
      Promise.reject(
        new StartupError(
          'CREDENTIAL_STORE_UNAVAILABLE',
          'Alfred could not initialize secure credential storage.',
          true,
        ),
      ),
    );
    await flush();
    expect(screen.getByText('CREDENTIAL_STORE_UNAVAILABLE')).toBeInTheDocument();
    expect(screen.getByText(/could not initialize secure credential storage/)).toBeInTheDocument();
  });

  it('never presents a raw exception as the primary message', async () => {
    renderGate(Promise.reject(new Error('panic at src\\foo.rs:12')));
    await flush();
    expect(screen.getByRole('heading', { name: /couldn't start/i })).toBeInTheDocument();
    expect(screen.getByText('UNEXPECTED_STARTUP_FAILURE')).toBeInTheDocument();
    expect(screen.queryByText(/panic at/)).not.toBeInTheDocument();
  });

  it('uses role=alert for failures so it interrupts', async () => {
    renderGate(Promise.reject(new StartupError('SIDECAR_EXITED', 'Stopped.', true)));
    await flush();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('shows the real log path from the shell when available', async () => {
    vi.mocked(fetchStartupDiagnostics).mockResolvedValue({
      log_path: 'C:\\Users\\test\\AppData\\Local\\AlfredData\\logs\\desktop.log',
      build: 'abc1234',
      version: '0.1.0',
    });
    renderGate(Promise.reject(new StartupError('SIDECAR_EXITED', 'Stopped.', true)));
    await flush();
    expect(
      screen.getByText('C:\\Users\\test\\AppData\\Local\\AlfredData\\logs\\desktop.log'),
    ).toBeInTheDocument();
  });

  it('falls back to the documented log directory when diagnostics fail', async () => {
    vi.mocked(fetchStartupDiagnostics).mockRejectedValue(new Error('no ipc'));
    renderGate(Promise.reject(new StartupError('SIDECAR_EXITED', 'Stopped.', true)));
    await flush();
    expect(screen.getByText(/%LOCALAPPDATA%\\AlfredData\\logs\\desktop\.log/)).toBeInTheDocument();
  });

  it('retries once per click and then reports readiness', async () => {
    renderGate(Promise.reject(new StartupError('SIDECAR_EXITED', 'Stopped.', true)));
    await flush();

    await act(async () => {
      screen.getByRole('button', { name: /Try again/ }).click();
    });
    await flush();

    expect(retryStartup).toHaveBeenCalledTimes(1);
    expect(screen.getByText('workspace-content')).toBeInTheDocument();
  });

  it('does not auto-retry: exactly one call per click', async () => {
    renderGate(Promise.reject(new StartupError('SIDECAR_EXITED', 'Stopped.', true)));
    await flush();
    await flush();
    expect(retryStartup).not.toHaveBeenCalled();
  });

  it('shows a new diagnostic code when the retry also fails', async () => {
    vi.mocked(retryStartup).mockRejectedValue(
      new StartupError('BACKEND_REJECTED', 'The local service refused the check.', true),
    );
    renderGate(Promise.reject(new StartupError('SIDECAR_EXITED', 'Stopped.', true)));
    await flush();

    await act(async () => {
      screen.getByRole('button', { name: /Try again/ }).click();
    });
    await flush();

    expect(screen.getByText('BACKEND_REJECTED')).toBeInTheDocument();
    expect(screen.getByText(/Retried 1 time/)).toBeInTheDocument();
  });

  it('subscribes to the shell startup event', async () => {
    renderGate(new Promise(() => {}));
    await flush();
    expect(listen).toHaveBeenCalledWith(STARTUP_PHASE_EVENT, expect.any(Function));
  });

  it('renders the phase reported by the shell', async () => {
    vi.mocked(fetchStartupStatus).mockResolvedValue(statusFor('CHECKING_DATABASE'));
    renderGate(new Promise(() => {}));
    await flush();
    expect(screen.getByText('Opening your local mailbox.')).toBeInTheDocument();
  });

  it('unsubscribes from the shell event on unmount', async () => {
    const unlisten = vi.fn();
    listen.mockResolvedValue(unlisten);
    const { unmount } = renderGate(new Promise(() => {}));
    await flush();
    unmount();
    expect(unlisten).toHaveBeenCalled();
  });

  it('works in browser dev mode without any Tauri command', async () => {
    renderGate(undefined, false);
    await flush();
    expect(screen.getByText('workspace-content')).toBeInTheDocument();
    expect(listen).not.toHaveBeenCalled();
    expect(fetchStartupStatus).not.toHaveBeenCalled();
  });
});

describe('StartupGate phase copy', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listen.mockResolvedValue(() => {});
    vi.mocked(fetchStartupDiagnostics).mockResolvedValue(null);
  });

  const cases: Array<[StartupStatus['phase'], string]> = [
    ['BOOT', 'Preparing to launch.'],
    ['INITIALIZING', 'Preparing your workspace.'],
    ['STARTING_BACKEND', 'Launching the local inbox service.'],
    ['WAITING_FOR_BACKEND', 'Waiting for the local inbox service to respond.'],
    ['CHECKING_DATABASE', 'Opening your local mailbox.'],
    ['CHECKING_AI_RUNTIME', 'Checking your local AI runtime.'],
    ['CHECKING_MODEL', 'Checking the local model.'],
    ['RESTORING_SESSION', 'Restoring your connected accounts.'],
  ];

  it.each(cases)('renders the sentence for %s', async (phase, body) => {
    vi.mocked(fetchStartupStatus).mockResolvedValue(statusFor(phase));
    render(
      <QueryClientProvider client={client()}>
        <StartupGate initPromise={new Promise(() => {})} tauri>
          <div>workspace-content</div>
        </StartupGate>
      </QueryClientProvider>,
    );
    await flush();
    expect(screen.getByText(body)).toBeInTheDocument();
  });
});
