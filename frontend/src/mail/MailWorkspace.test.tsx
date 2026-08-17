import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MailWorkspace } from './MailWorkspace';
import type { Email } from '../api/emails';

const primaryEmail: Email = {
  id: 'p1',
  sender: 'boss@work.com',
  sender_name: 'Boss',
  recipients: ['me@gmail.com'],
  subject: 'Q3 planning needed',
  body: 'Please send the plan by Friday.',
  received_at: '2026-08-17T09:00:00Z',
  label_ids: ['INBOX', 'UNREAD', 'CATEGORY_PERSONAL'],
  analysis: {
    short_summary: 'Plan request',
    category: 'work',
    priority: 'high',
    priority_score: 78,
    reason_for_priority: 'Direct request',
    needs_reply: true,
    action_items: [{ description: 'Send the Q3 plan', owner: 'user', deadline: 'Friday' }],
    deadlines: [{ description: 'Q3 plan', due_at: 'Friday' }],
    important_details: [],
  },
};

const promoEmail: Email = {
  id: 'pr1',
  sender: 'adobe@marketing.com',
  sender_name: 'Adobe',
  recipients: ['me@gmail.com'],
  subject: 'Creative Cloud sale',
  body: 'Big discounts inside.',
  received_at: '2026-08-16T09:00:00Z',
  label_ids: ['INBOX', 'CATEGORY_PROMOTIONS'],
  analysis: null,
};

const archivedEmail: Email = {
  id: 'a1',
  sender: 'old@project.com',
  sender_name: 'Old Project',
  recipients: ['me@gmail.com'],
  subject: 'Archived planning notes',
  body: 'Notes from last quarter.',
  received_at: '2026-06-01T09:00:00Z',
  label_ids: ['CATEGORY_PERSONAL'],
  analysis: null,
};

const sentEmail: Email = {
  id: 's1',
  sender: 'me@gmail.com',
  sender_name: 'Me',
  recipients: ['client@corp.com'],
  subject: 'Re: proposal follow-up',
  body: 'Attached the updated proposal.',
  received_at: '2026-07-01T09:00:00Z',
  label_ids: ['SENT'],
  analysis: null,
};

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return {
    ...original,
    emails: vi.fn((options?: { category?: string | null; scope?: string; kind?: string | null; query?: string }) => {
      if (options?.query) {
        return Promise.resolve([archivedEmail]);
      }
      if (options?.scope === 'all' && options?.kind === 'sent') {
        return Promise.resolve([sentEmail]);
      }
      if (options?.scope === 'all' && options?.kind === 'archived') {
        return Promise.resolve([archivedEmail]);
      }
      if (options?.scope === 'all') {
        return Promise.resolve([primaryEmail, archivedEmail, sentEmail]);
      }
      if (options?.category === 'promotions') return Promise.resolve([promoEmail]);
      return Promise.resolve([primaryEmail]);
    }),
    emailCounts: vi.fn(() => Promise.resolve({
      active_inbox: 2,
      all_mail: 4,
      excluded: 0,
      categories: { primary: 1, promotions: 1, social: 0, updates: 0, forums: 0 },
    })),
    emailDetails: vi.fn((id: string) => Promise.resolve(
      id === 'p1' ? primaryEmail : id === 'pr1' ? promoEmail
        : id === 'a1' ? archivedEmail : sentEmail)),
    accounts: vi.fn(() => Promise.resolve([
      {
        id: 'gmail_user',
        provider: 'gmail',
        email_address: 'user@gmail.com',
        display_name: 'User',
        connection_status: 'connected',
        backfill: {
          state: 'complete',
          complete: true,
          estimate: null,
          imported: 55,
          pages: 2,
          remaining_estimate: null,
          last_page_at: null,
          last_error: null,
        },
      },
    ])),
    backfillAccount: vi.fn(() => Promise.resolve({ action: 'resumed', status: {} })),
    pauseBackfill: vi.fn(() => Promise.resolve({ action: 'paused', status: {} })),
  };
});

function renderWorkspace() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MailWorkspace
        searchQuery=""
        onClearSearch={() => {}}
        syncState={{ syncing: false, lastSyncAt: null }}
        onRequestSync={() => {}}
      />
    </QueryClientProvider>
  );
}

describe('MailWorkspace', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders Primary messages by default', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    expect(screen.queryByText('Creative Cloud sale')).not.toBeInTheDocument();
  });

  it('switches between Inbox and All Mail views', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    expect(screen.queryByText('Archived planning notes')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'All Mail' }));
    await waitFor(() => {
      expect(screen.getByText('Archived planning notes')).toBeInTheDocument();
    });
    // still shows inbox mail and sent mail too
    expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    expect(screen.getByText('Re: proposal follow-up')).toBeInTheDocument();

    // category tabs disappear in All Mail view; kind filters appear
    expect(screen.queryByRole('tab', { name: /Promotions/ })).not.toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Sent' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Archived' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'Inbox' }));
    await waitFor(() => {
      expect(screen.queryByText('Archived planning notes')).not.toBeInTheDocument();
    });
    expect(screen.getByRole('tab', { name: /Promotions/ })).toBeInTheDocument();
  });

  it('All Mail kind filters narrow to Sent and Archived', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('tab', { name: 'All Mail' }));
    await waitFor(() => {
      expect(screen.getByText('Archived planning notes')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('tab', { name: 'Sent' }));
    await waitFor(() => {
      expect(screen.getByText('Re: proposal follow-up')).toBeInTheDocument();
    });
    expect(screen.queryByText('Q3 planning needed')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'Archived' }));
    await waitFor(() => {
      expect(screen.getByText('Archived planning notes')).toBeInTheDocument();
    });
    expect(screen.queryByText('Re: proposal follow-up')).not.toBeInTheDocument();
  });

  it('marks Sent and Archived rows with badges', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('tab', { name: 'All Mail' }));
    await waitFor(() => {
      expect(screen.getByText('Archived planning notes')).toBeInTheDocument();
    });
    // kind tab + row badge both exist for each label
    expect(screen.getAllByText('Sent').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Archived').length).toBeGreaterThanOrEqual(2);
  });

  it('shows completed backfill status near All Mail', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('All mail synced')).toBeInTheDocument();
    });
    expect(screen.getByText('55 older messages local')).toBeInTheDocument();
  });

  it('shows progress and pause control while syncing older mail', async () => {
    const { accounts: accountsMock } = await import('../api/emails');
    vi.mocked(accountsMock).mockResolvedValue([
      {
        id: 'gmail_user',
        provider: 'gmail',
        email_address: 'user@gmail.com',
        display_name: 'User',
        connection_status: 'connected',
        backfill: {
          state: 'running',
          complete: false,
          estimate: 2100,
          imported: 450,
          pages: 11,
          remaining_estimate: 1650,
          last_page_at: null,
          last_error: null,
        },
      },
    ] as never);
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Syncing older mail…')).toBeInTheDocument();
    });
    expect(screen.getByText(/450 synced/)).toBeInTheDocument();
    expect(screen.getByText(/~1650 remaining/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pause syncing older mail' })).toBeInTheDocument();
  });

  it('switches to Promotions category and renders promotions', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('tab', { name: /Promotions/ }));
    await waitFor(() => {
      expect(screen.getByText('Creative Cloud sale')).toBeInTheDocument();
    });
    expect(screen.queryByText('Q3 planning needed')).not.toBeInTheDocument();
  });

  it('shows an empty state for empty categories', async () => {
    const { emails: emailsMock } = await import('../api/emails');
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    vi.mocked(emailsMock).mockResolvedValueOnce([] as never);
    fireEvent.click(screen.getByRole('tab', { name: /Updates/ }));
    await waitFor(() => {
      expect(screen.getByText('No messages here.')).toBeInTheDocument();
    });
  });

  it('global search searches all mail, not only the active inbox', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: Infinity } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MailWorkspace
          searchQuery="archived"
          onClearSearch={() => {}}
          syncState={{ syncing: false, lastSyncAt: null }}
          onRequestSync={() => {}}
        />
      </QueryClientProvider>
    );
    await waitFor(() => {
      expect(screen.getByText('Archived planning notes')).toBeInTheDocument();
    });
    expect(screen.getByText(/Searching all local mail/)).toBeInTheDocument();
    // view switch + category tabs hidden during global search
    expect(screen.queryByRole('tab', { name: 'Inbox' })).not.toBeInTheDocument();
    expect(screen.queryByRole('tab', { name: /Promotions/ })).not.toBeInTheDocument();
  });

  it('selecting a message renders the reader and Alfred intelligence panel', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Q3 planning needed'));
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Q3 planning needed' })).toBeInTheDocument();
      expect(screen.getByText('Alfred Intelligence')).toBeInTheDocument();
    });
    expect(screen.getByText('Plan request')).toBeInTheDocument();
    expect(screen.getByText('Direct request')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Draft/ })).toBeInTheDocument();
  });

  it('toggling Later persists across interactions', async () => {
    renderWorkspace();
    await waitFor(() => {
      expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: 'Save for Later' }));
    await waitFor(() => {
      expect(JSON.parse(localStorage.getItem('alfred-later-ids') ?? '[]')).toContain('p1');
    });
  });
});
