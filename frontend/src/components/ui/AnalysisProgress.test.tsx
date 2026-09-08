import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnalysisProgress } from './AnalysisProgress';
import { analysisStatus, analysisRetry } from '../../api/emails';
import type { AnalysisStatus } from '../../api/emails';

vi.mock('../../api/client', () => ({
  sseUrl: (path: string) => `http://test${path}`,
}));

vi.mock('../../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../api/emails')>();
  return {
    ...original,
    analysisStatus: vi.fn(),
    analysisRetry: vi.fn(),
  };
});

const readyStatus: AnalysisStatus = {
  state: 'ready',
  model: 'qwen3:4b',
  model_installed: true,
  ollama_installed: true,
  ollama_running: true,
  last_error: null,
  detail: null,
  pending: 0,
  worker_running: true,
  queue_paused: false,
};

function renderWithStatus(status: AnalysisStatus) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  vi.mocked(analysisStatus).mockResolvedValue(status);
  return render(
    <QueryClientProvider client={queryClient}>
      <AnalysisProgress />
    </QueryClientProvider>
  );
}

describe('AnalysisProgress', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // EventSource does not exist in jsdom — silence it.
    vi.stubGlobal('EventSource', class {
      close() {}
    });
  });

  it('stays out of the way when AI is ready and nothing is queued', async () => {
    const { container } = renderWithStatus(readyStatus);
    await waitFor(() => {
      expect(container.querySelector('.analysis-progress-bar')).toBeNull();
    });
  });

  it('shows progress when AI is ready and analyses are pending', async () => {
    renderWithStatus({ ...readyStatus, pending: 337 });
    await waitFor(() => {
      expect(screen.getByText(/Analyzing 337 messages/)).toBeInTheDocument();
    });
  });

  it('shows understandable offline state with queued count and Retry', async () => {
    renderWithStatus({
      ...readyStatus,
      state: 'ollama_not_running',
      pending: 337,
      ollama_running: false,
    });
    await waitFor(() => {
      expect(screen.getByText(/Local AI offline/)).toBeInTheDocument();
      expect(screen.getByText(/337 analyses queued/)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
    });
  });

  it('shows model-missing state naming the model', async () => {
    renderWithStatus({
      ...readyStatus,
      state: 'model_missing',
      model_installed: false,
      pending: 5,
    });
    await waitFor(() => {
      expect(screen.getByText(/qwen3:4b needs to be installed/)).toBeInTheDocument();
    });
  });

  it('Retry triggers the retry endpoint', async () => {
    vi.mocked(analysisRetry).mockResolvedValue(readyStatus);
    renderWithStatus({
      ...readyStatus,
      state: 'temporarily_unavailable',
      pending: 12,
    });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    await waitFor(() => {
      expect(vi.mocked(analysisRetry)).toHaveBeenCalled();
    });
  });

  it('shows recovering state while the smoke test runs', async () => {
    renderWithStatus({ ...readyStatus, state: 'recovering', pending: 8 });
    await waitFor(() => {
      expect(screen.getByText(/Local AI recovering/)).toBeInTheDocument();
    });
  });
});
