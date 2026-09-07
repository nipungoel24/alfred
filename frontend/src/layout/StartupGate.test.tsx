import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StartupGate } from './StartupGate';

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>();
  return {
    ...actual,
    initApi: vi.fn(async () => {}),
    setApiCredentials: vi.fn(),
  };
});

function renderGate(initPromise?: Promise<void>) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  const promise = initPromise ?? Promise.resolve();
  return render(
    <QueryClientProvider client={queryClient}>
      <StartupGate initPromise={promise}>
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

  it('shows the starting state and releases when promise resolves', async () => {
    renderGate();
    expect(screen.getByText(/Starting Alfred/)).toBeInTheDocument();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });
    expect(screen.getByText('workspace-content')).toBeInTheDocument();
  });

  it('shows the failure state when promise rejects', async () => {
    const failingPromise = Promise.reject(new Error('sidecar exited'));
    renderGate(failingPromise);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });
    expect(screen.getByText(/couldn't start its local service/i)).toBeInTheDocument();
    expect(screen.getByText('sidecar exited')).toBeInTheDocument();
    expect(screen.getByText(/Logs:/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Retry/ })).toBeInTheDocument();
  });

  it('shows failure for startup timeout', async () => {
    const timeoutPromise = Promise.reject(new Error('startup timeout'));
    renderGate(timeoutPromise);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });
    expect(screen.getByText('startup timeout')).toBeInTheDocument();
  });

  it('shows failure for health timeout', async () => {
    const healthTimeout = Promise.reject(new Error('health timeout'));
    renderGate(healthTimeout);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });
    expect(screen.getByText('health timeout')).toBeInTheDocument();
  });
});
