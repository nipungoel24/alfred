import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { OverviewPage } from './OverviewPage';
import * as api from '../../api/emails';

vi.mock('../../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../api/emails')>();
  return {
    ...actual,
    briefing: vi.fn(),
    emails: vi.fn(),
    emailCounts: vi.fn(),
    regenerateBriefing: vi.fn(),
    // The first-run checklist would otherwise reach the network.
    accounts: vi.fn().mockResolvedValue([]),
    analysisStatus: vi.fn().mockResolvedValue({
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
      pull: null,
    }),
  };
});

/** A complete Briefing, built from the real type so it cannot drift. */
const emptyBriefing: api.Briefing = {
  executive_summary: 'All clear.',
  total_emails: 0,
  urgent_count: 0,
  high_priority_count: 0,
  needs_reply_count: 0,
  deadline_count: 0,
  top_attention_items: [],
  deadlines: [],
  important_updates: [],
  can_wait_or_review_later: [],
};

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(
    <QueryClientProvider client={client}>
      <OverviewPage onNavigate={() => {}} onOpenEmail={() => {}} />
    </QueryClientProvider>,
  );
}

describe('OverviewPage — state distinction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.briefing).mockResolvedValue(emptyBriefing);
    vi.mocked(api.emails).mockResolvedValue([]);
    vi.mocked(api.emailCounts).mockResolvedValue({
      active_inbox: 0,
      all_mail: 0,
      excluded: 0,
      categories: {
        primary: 0, promotions: 0, social: 0, updates: 0, forums: 0,
      },
    });
  });

  it('renders an error when the briefing request fails', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('network down'));
    renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByText("Your briefing couldn't load")).toBeInTheDocument();
  });

  it('does not present a failure as a quiet mailbox', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    // Previously this rendered "0 messages in Inbox" with empty panels,
    // which reads as "nothing to do" rather than "something is broken".
    expect(screen.queryByText(/messages in Inbox/)).not.toBeInTheDocument();
    expect(screen.getByText('Runtime information unavailable')).toBeInTheDocument();
  });

  it('renders an error when the mail list request fails', async () => {
    vi.mocked(api.emails).mockRejectedValue(new Error('network down'));
    renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByText("Your briefing couldn't load")).toBeInTheDocument();
  });

  it('tolerates a supplementary count failure without blanking the page', async () => {
    // emailCounts is supplementary: the page falls back to the list length.
    // Its failure alone must not hide working content.
    vi.mocked(api.emailCounts).mockRejectedValue(new Error('counts down'));
    renderPage();

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /Good (morning|afternoon|evening)/ })).toBeInTheDocument();
    });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('never surfaces the raw exception text', async () => {
    vi.mocked(api.briefing).mockRejectedValue(
      new Error('HTTPStatusError: 500 from http://127.0.0.1:8765/api/briefing'),
    );
    const { container } = renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(container.textContent).not.toMatch(/HTTPStatusError/);
    expect(container.textContent).not.toMatch(/127\.0\.0\.1/);
  });

  it('retry re-runs the failed requests and renders content when they recover', async () => {
    vi.mocked(api.briefing).mockRejectedValueOnce(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(api.briefing).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => expect(api.briefing).toHaveBeenCalledTimes(2));
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /Good (morning|afternoon|evening)/ })).toBeInTheDocument();
    });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('keeps showing the error when the retry also fails', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('still down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));
    await waitFor(() => expect(api.briefing).toHaveBeenCalledTimes(2));
    expect(screen.getByText("Your briefing couldn't load")).toBeInTheDocument();
  });

  it('keeps an h1 so the page is never unlabelled', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('exposes an assertive alert with a keyboard-reachable retry', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(screen.getByRole('alert')).toHaveAttribute('aria-live', 'assertive');
    const retry = screen.getByRole('button', { name: /try again/i });
    retry.focus();
    expect(document.activeElement).toBe(retry);
  });
});
