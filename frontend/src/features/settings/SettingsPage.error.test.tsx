import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SettingsPage } from './SettingsPage';
import { ThemeProvider } from '../../theme/ThemeProvider';
import * as api from '../../api/emails';

vi.mock('../../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../api/emails')>();
  return { ...actual, health: vi.fn(), analysisStatus: vi.fn() };
});

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(
    <QueryClientProvider client={client}>
      {/* SettingsPage renders ThemeToggle, which requires the provider. */}
      <ThemeProvider>
        <SettingsPage />
      </ThemeProvider>
    </QueryClientProvider>,
  );
}

describe('SettingsPage — state distinction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.health).mockResolvedValue({
      status: 'ok',
      ai: 'ready',
      build: 'abc1234',
    });
    vi.mocked(api.analysisStatus).mockResolvedValue({
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
    });
  });

  it('shows runtime rows when the queries succeed', async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('Ready')).toBeInTheDocument();
    });
    expect(screen.getByText('Model installed')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('shows a scoped error when runtime status cannot be read', async () => {
    vi.mocked(api.health).mockRejectedValue(new Error('network down'));
    renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByText('Runtime status unavailable')).toBeInTheDocument();
  });

  it('keeps the rest of the page working when only runtime status fails', async () => {
    vi.mocked(api.health).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    // Theme, Data, Privacy and About do not depend on this query. A
    // page-level error would hide working settings, which is its own bug.
    expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument();
    expect(screen.getByText('Appearance')).toBeInTheDocument();
    expect(screen.getByText('Local SQLite (AppData)')).toBeInTheDocument();
    expect(screen.getByText('Analysis')).toBeInTheDocument();
  });

  it('never surfaces the raw exception text', async () => {
    vi.mocked(api.health).mockRejectedValue(
      new Error('ConnectError: ECONNREFUSED 127.0.0.1:49152'),
    );
    const { container } = renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(container.textContent).not.toMatch(/ConnectError/);
    expect(container.textContent).not.toMatch(/ECONNREFUSED/);
  });

  it('retry re-runs the request and renders runtime rows when it recovers', async () => {
    vi.mocked(api.health).mockRejectedValueOnce(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(api.health).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => expect(api.health).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByText('Ready')).toBeInTheDocument());
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('keeps showing the error when the retry also fails', async () => {
    vi.mocked(api.health).mockRejectedValue(new Error('still down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));
    await waitFor(() => expect(api.health).toHaveBeenCalledTimes(2));
    expect(screen.getByText('Runtime status unavailable')).toBeInTheDocument();
  });

  it('exposes an assertive alert with a keyboard-reachable retry', async () => {
    vi.mocked(api.health).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(screen.getByRole('alert')).toHaveAttribute('aria-live', 'assertive');
    const retry = screen.getByRole('button', { name: /try again/i });
    retry.focus();
    expect(document.activeElement).toBe(retry);
  });
});
