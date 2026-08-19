import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StartupGate } from './StartupGate';

vi.mock('../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/emails')>();
  return {
    ...actual,
    health: vi.fn(),
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
    vi.clearAllMocks();
  });

  it('shows the starting state and releases when healthy', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValueOnce(new Error('down')).mockResolvedValueOnce({ status: 'ok', ai: 'ready' });
    renderGate();
    expect(screen.getByText(/Starting Alfred/)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('workspace-content')).toBeInTheDocument();
    }, { timeout: 8000 });
  });

  it('shows the failure state after the retry budget', async () => {
    const { health } = await import('../api/emails');
    vi.mocked(health).mockRejectedValue(new Error('down'));
    renderGate();
    await waitFor(() => {
      expect(screen.getByText(/couldn't start its local service/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Retry/ })).toBeInTheDocument();
    }, { timeout: 15000 });
  }, 20000);

  it('retries after failure and recovers', async () => {
    const { health } = await import('../api/emails');
    const mock = vi.mocked(health);
    mock.mockRejectedValue(new Error('down'));
    renderGate();
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Retry/ })).toBeInTheDocument();
    }, { timeout: 15000 });
    mock.mockResolvedValue({ status: 'ok', ai: 'ready' });
    fireEvent.click(screen.getByRole('button', { name: /Retry/ }));
    await waitFor(() => {
      expect(screen.getByText('workspace-content')).toBeInTheDocument();
    }, { timeout: 8000 });
  }, 25000);
});
