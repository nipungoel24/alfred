import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DeadlinesPage } from './DeadlinesPage';
import * as api from '../../api/emails';

vi.mock('../../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../api/emails')>();
  return { ...actual, briefing: vi.fn(), emails: vi.fn(), emailCounts: vi.fn() };
});

const deadline = {
  email_id: 'e1',
  sender: 'Alice',
  subject: 'Q3 plan due',
  short_summary: 'Plan needed',
  priority: 'high' as const,
  why_it_matters: 'Commitment made',
  deadline: 'Friday',
  needs_reply: true,
};

/** A complete Briefing, built from the real type so it cannot drift. */
function briefing(overrides: Partial<api.Briefing> = {}): api.Briefing {
  return {
    executive_summary: 'Nothing urgent.',
    total_emails: 0,
    urgent_count: 0,
    high_priority_count: 0,
    needs_reply_count: 0,
    deadline_count: 0,
    top_attention_items: [],
    deadlines: [],
    important_updates: [],
    can_wait_or_review_later: [],
    ...overrides,
  };
}

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(
    <QueryClientProvider client={client}>
      <DeadlinesPage />
    </QueryClientProvider>,
  );
}

describe('DeadlinesPage — state distinction', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a loading skeleton, not an empty state, while loading', async () => {
    // Never resolves: the component must stay in its loading branch.
    vi.mocked(api.briefing).mockReturnValue(new Promise(() => {}));
    const { container } = renderPage();

    await waitFor(() => {
      expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument();
    });
    expect(screen.queryByText(/no upcoming deadlines/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders a genuine empty state when the request succeeds with no deadlines', async () => {
    vi.mocked(api.briefing).mockResolvedValue(briefing());

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('No upcoming deadlines')).toBeInTheDocument();
    });
    // An empty result must NOT be announced as an error.
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders an error state, never "no deadlines", when the request fails', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('network down'));

    renderPage();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    // The critical assertion: the failure must not masquerade as an empty list.
    expect(screen.queryByText(/no upcoming deadlines/i)).not.toBeInTheDocument();
    expect(screen.getByText("Deadlines couldn't load")).toBeInTheDocument();
  });

  it('never surfaces the raw exception text to the user', async () => {
    vi.mocked(api.briefing).mockRejectedValue(
      new Error('TypeError: cannot read properties of undefined (reading "json")'),
    );

    const { container } = renderPage();

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(container.textContent).not.toMatch(/TypeError/);
    expect(container.textContent).not.toMatch(/cannot read properties/);
  });

  it('retry re-runs the real request and renders data when it succeeds', async () => {
    vi.mocked(api.briefing)
      .mockRejectedValueOnce(new Error('network down'))
      .mockResolvedValueOnce(briefing({ deadlines: [deadline], deadline_count: 1 }));

    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    expect(api.briefing).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: /try again/i }));

    // The request really re-ran...
    await waitFor(() => expect(api.briefing).toHaveBeenCalledTimes(2));
    // ...and the successful result replaced the error.
    await waitFor(() => expect(screen.getByText('Q3 plan due')).toBeInTheDocument());
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('keeps showing the error when the retry also fails', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('still down'));

    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => expect(api.briefing).toHaveBeenCalledTimes(2));
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText("Deadlines couldn't load")).toBeInTheDocument();
  });

  it('exposes the error as an assertive alert with a keyboard-reachable retry', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());

    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');

    const retry = screen.getByRole('button', { name: /try again/i });
    retry.focus();
    expect(document.activeElement).toBe(retry);
  });

  it('reports runtime unavailability in the subtitle when failed', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('down'));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('Runtime information unavailable')).toBeInTheDocument();
    });
    // It must not claim "0 upcoming", which is a claim about the user's data.
    expect(screen.queryByText('0 upcoming')).not.toBeInTheDocument();
  });
});
