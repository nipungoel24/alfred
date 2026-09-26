import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TasksPage } from './TasksPage';
import * as api from '../../api/emails';

vi.mock('../../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../api/emails')>();
  return {
    ...actual,
    tasks: vi.fn(),
    toggleTask: vi.fn(),
    dismissTask: vi.fn(),
    patchTaskPriority: vi.fn(),
  };
});

const task = {
  id: 't1',
  source_email_id: 'e1',
  source_thread_id: null,
  title: 'Send the Q3 plan',
  description: 'Alice asked for it',
  due_at: 'Friday',
  priority: 'high' as const,
  status: 'pending' as const,
  created_at: '2026-01-01T00:00:00Z',
  confidence: 'high',
  fingerprint: 'fp1',
  priority_override: null,
};

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(
    <QueryClientProvider client={client}>
      <TasksPage />
    </QueryClientProvider>,
  );
}

describe('TasksPage — state distinction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a loading skeleton, not an empty state, while loading', async () => {
    vi.mocked(api.tasks).mockReturnValue(new Promise(() => {}));
    const { container } = renderPage();

    await waitFor(() => {
      expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument();
    });
    expect(screen.queryByText(/no pending tasks/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders a genuine empty state on a successful empty response', async () => {
    vi.mocked(api.tasks).mockResolvedValue([]);
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No pending tasks')).toBeInTheDocument();
    });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders an error, never "no pending tasks", when the request fails', async () => {
    vi.mocked(api.tasks).mockRejectedValue(new Error('network down'));
    renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    // The critical assertion.
    expect(screen.queryByText(/no pending tasks/i)).not.toBeInTheDocument();
    expect(screen.getByText("Tasks couldn't load")).toBeInTheDocument();
  });

  it('never surfaces the raw exception text', async () => {
    vi.mocked(api.tasks).mockRejectedValue(
      new Error('ReferenceError: jobs is not defined at line 42'),
    );
    const { container } = renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(container.textContent).not.toMatch(/ReferenceError/);
    expect(container.textContent).not.toMatch(/is not defined/);
  });

  it('retry re-runs the request and renders tasks when it succeeds', async () => {
    vi.mocked(api.tasks)
      .mockRejectedValueOnce(new Error('network down'))
      .mockResolvedValueOnce([task]);

    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(api.tasks).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => expect(api.tasks).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByText('Send the Q3 plan')).toBeInTheDocument());
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('keeps showing the error when the retry also fails', async () => {
    vi.mocked(api.tasks).mockRejectedValue(new Error('still down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));
    await waitFor(() => expect(api.tasks).toHaveBeenCalledTimes(2));
    expect(screen.getByText("Tasks couldn't load")).toBeInTheDocument();
  });

  it('hides the filter switch while failed, since there is nothing to filter', async () => {
    vi.mocked(api.tasks).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(screen.queryByRole('button', { name: 'Pending' })).not.toBeInTheDocument();
    expect(screen.getByText('Runtime information unavailable')).toBeInTheDocument();
  });

  it('keeps the page heading so the user is never left without context', async () => {
    vi.mocked(api.tasks).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(screen.getByRole('heading', { level: 1, name: 'Tasks' })).toBeInTheDocument();
  });

  it('exposes an assertive alert with a keyboard-reachable retry', async () => {
    vi.mocked(api.tasks).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(screen.getByRole('alert')).toHaveAttribute('aria-live', 'assertive');
    const retry = screen.getByRole('button', { name: /try again/i });
    retry.focus();
    expect(document.activeElement).toBe(retry);
  });
});
