import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const fetchBriefingMock = vi.fn();
const fetchEmailsMock = vi.fn();
const fetchCountsMock = vi.fn();
const regenerateMock = vi.fn();
const fetchDetailsMock = vi.fn();

vi.mock('../../api/emails', () => ({
  briefing: (...args: unknown[]) => fetchBriefingMock(...args),
  emailCounts: (...args: unknown[]) => fetchCountsMock(...args),
  emails: (...args: unknown[]) => fetchEmailsMock(...args),
  regenerateBriefing: (...args: unknown[]) => regenerateMock(...args),
  emailDetails: (...args: unknown[]) => fetchDetailsMock(...args),
}));

import { OverviewPage } from './OverviewPage';

function renderPage(onNavigate?: (page: string) => void, onOpenEmail?: (id: string) => void) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <OverviewPage onNavigate={onNavigate ?? (() => {})} onOpenEmail={onOpenEmail ?? (() => {})} />
    </QueryClientProvider>
  );
}

describe('OverviewPage', () => {
  beforeEach(() => {
    fetchBriefingMock.mockReset();
    fetchEmailsMock.mockReset();
    fetchCountsMock.mockReset();
    regenerateMock.mockReset();
    fetchDetailsMock.mockReset();
  });

  it('renders Inbox and All Mail counts from the live counts endpoint', async () => {
    fetchCountsMock.mockResolvedValue({
      active_inbox: 867,
      all_mail: 947,
      excluded: 0,
      categories: { primary: 56, promotions: 71, social: 2, updates: 738, forums: 0 },
    });
    fetchEmailsMock.mockResolvedValue([]);
    fetchBriefingMock.mockResolvedValue({ executive_summary: '', total_emails: 0 });

    renderPage();
    await waitFor(() => expect(screen.getByText(/867 messages in Inbox/)).toBeInTheDocument());
    expect(screen.getByText(/947 in All Mail/)).toBeInTheDocument();
  });

  it('falls back to the loaded email list when counts are missing', async () => {
    fetchCountsMock.mockResolvedValue(undefined);
    fetchEmailsMock.mockResolvedValue([{ id: 'e1', subject: 'A', sender: 'x', recipients: [], body: '', label_ids: [], received_at: '2026-08-01T00:00:00Z' }]);
    fetchBriefingMock.mockResolvedValue({ executive_summary: '', total_emails: 0 });

    renderPage();
    await waitFor(() => expect(screen.getByText(/1 messages in Inbox/)).toBeInTheDocument());
  });

  it('shows metric cards for Important, Needs Reply, Deadlines and Inbox', async () => {
    fetchCountsMock.mockResolvedValue({ active_inbox: 12, all_mail: 40, excluded: 0, categories: {} as never });
    fetchEmailsMock.mockResolvedValue([]);
    fetchBriefingMock.mockResolvedValue({
      executive_summary: '',
      total_emails: 40,
      urgent_count: 0,
      high_priority_count: 3,
      needs_reply_count: 5,
      deadline_count: 2,
      top_attention_items: [],
      deadlines: [],
      important_updates: [],
      can_wait_or_review_later: [],
    });

    renderPage();
    // Metric cards surface the live briefing counts via their accessible name
    expect(await screen.findByRole('button', { name: 'Important: 3' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Needs Reply: 5' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Deadlines: 2' })).toBeInTheDocument();
  });

  it('navigates to the mail workspace from the Inbox metric', async () => {
    const onNavigate = vi.fn();
    fetchCountsMock.mockResolvedValue({ active_inbox: 12, all_mail: 40, excluded: 0, categories: {} as never });
    fetchEmailsMock.mockResolvedValue([]);
    fetchBriefingMock.mockResolvedValue({
      executive_summary: '',
      total_emails: 40,
      urgent_count: 0,
      high_priority_count: 0,
      needs_reply_count: 0,
      deadline_count: 0,
      top_attention_items: [],
      deadlines: [],
      important_updates: [],
      can_wait_or_review_later: [],
    });

    renderPage(onNavigate);
    await waitFor(() => expect(screen.getByText('Inbox')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: /Inbox/ }));
    expect(onNavigate).toHaveBeenCalledWith('mail');
  });

  it('opens the exact email preview for a needs-attention item', async () => {
    const onOpenEmail = vi.fn();
    fetchCountsMock.mockResolvedValue({ active_inbox: 1, all_mail: 1, excluded: 0, categories: {} as never });
    fetchEmailsMock.mockResolvedValue([]);
    fetchBriefingMock.mockResolvedValue({
      executive_summary: '',
      total_emails: 1,
      urgent_count: 1,
      high_priority_count: 0,
      needs_reply_count: 1,
      deadline_count: 0,
      top_attention_items: [
        {
          email_id: 'email_exact_1',
          sender: 'Boss',
          subject: 'Q3 planning needed',
          priority: 'urgent',
          why_it_matters: 'Direct request',
          needs_reply: true,
        },
      ],
      deadlines: [],
      important_updates: [],
      can_wait_or_review_later: [],
    });

    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <OverviewPage onNavigate={() => {}} onOpenEmail={onOpenEmail} />
      </QueryClientProvider>
    );
    fireEvent.click(await screen.findByRole('button', { name: /Boss: Q3 planning needed/ }));
    // Clicking the derived item previews THAT email (SourceEmailPreview
    // opens); "Open in Mail" would then navigate with the exact id.
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(onOpenEmail).not.toHaveBeenCalled();
  });

  it('Open in Mail from the preview navigates with the exact email id', async () => {
    const onOpenEmail = vi.fn();
    fetchCountsMock.mockResolvedValue({ active_inbox: 1, all_mail: 1, excluded: 0, categories: {} as never });
    fetchEmailsMock.mockResolvedValue([]);
    fetchDetailsMock.mockResolvedValue({
      id: 'email_exact_1',
      sender: 'boss@work.com',
      sender_name: 'Boss',
      subject: 'Q3 planning needed',
      body: 'Please send the plan.',
      received_at: '2026-08-17T09:00:00Z',
    });
    fetchBriefingMock.mockResolvedValue({
      executive_summary: '',
      total_emails: 1,
      urgent_count: 1,
      high_priority_count: 0,
      needs_reply_count: 1,
      deadline_count: 0,
      top_attention_items: [
        {
          email_id: 'email_exact_1',
          sender: 'Boss',
          subject: 'Q3 planning needed',
          priority: 'urgent',
          why_it_matters: 'Direct request',
          needs_reply: true,
        },
      ],
      deadlines: [],
      important_updates: [],
      can_wait_or_review_later: [],
    });

    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <OverviewPage onNavigate={() => {}} onOpenEmail={onOpenEmail} />
      </QueryClientProvider>
    );
    fireEvent.click(await screen.findByRole('button', { name: /Boss: Q3 planning needed/ }));
    fireEvent.click(await screen.findByRole('button', { name: 'Open in Mail' }));
    expect(onOpenEmail).toHaveBeenCalledWith('email_exact_1');
  });
});
