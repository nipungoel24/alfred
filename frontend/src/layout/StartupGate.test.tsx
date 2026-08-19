import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StartupGate } from './StartupGate';

vi.mock('../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/emails')>();
  return {
    ...actual,
    health: vi.fn(),
  };
});

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>();
  return {
    ...actual,
    initApi: vi.fn(async () => {}),
  };
});

function renderGate() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <StartupGate>
        <div>workspace-content</div>
      </StartupGate>
    </QueryClientProvider>
  );
}

describe('StartupGate', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  async function flushTimers(ms: number) {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(ms);
    });
  }

  it('shows the starting state and releases when healthy', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValueOnce(new Error('down')).mockResolvedValueOnce({ status: 'ok', ai: 'ready' });
    renderGate();
    expect(screen.getByText(/Starting Alfred/)).toBeInTheDocument();
    await flushTimers(1800);
    expect(screen.getByText('workspace-content')).toBeInTheDocument();
  });

  it('keeps waiting beyond 20s while the backend warms up', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValue(new Error('down'));
    renderGate();
    await flushTimers(25_000);
    // Budget is 45s — must still be in the starting state
    expect(screen.getByText(/Starting Alfred/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Retry/ })).not.toBeInTheDocument();
  });

  it('shows the failure state after the 45s budget with a diagnostic code', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValue(new Error('down'));
    renderGate();
    await flushTimers(46_000);
    expect(screen.getByText(/couldn't start its local service/i)).toBeInTheDocument();
    expect(screen.getByText('BACKEND_TIMEOUT')).toBeInTheDocument();
    expect(screen.getByText(/Logs:/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Retry/ })).toBeInTheDocument();
  });

  it('labels an authenticated-health rejection distinctly', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValue(new Error('Missing or invalid session token.'));
    renderGate();
    await flushTimers(46_000);
    expect(screen.getByText('BACKEND_UNAUTHORIZED')).toBeInTheDocument();
  });

  it('retries after failure and recovers', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValue(new Error('down'));
    renderGate();
    await flushTimers(46_000);
    expect(screen.getByRole('button', { name: /Retry/ })).toBeInTheDocument();

    vi.mocked(health).mockResolvedValue({ status: 'ok', ai: 'ready' });
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Retry/ }));
      await Promise.resolve();
    });
    await flushTimers(2500);
    expect(screen.getByText('workspace-content')).toBeInTheDocument();
  });
});
