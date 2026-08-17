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

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return {
    ...original,
    emails: vi.fn((options?: { category?: string | null; scope?: string; query?: string }) => {
      if (options?.query) {
        return Promise.resolve([archivedEmail]);
      }
      if (options?.scope === 'all') {
        return Promise.resolve([primaryEmail, archivedEmail]);
      }
      if (options?.category === 'promotions') return Promise.resolve([promoEmail]);
      return Promise.resolve([primaryEmail]);
    }),
    emailCounts: vi.fn(() => Promise.resolve({
      active_inbox: 2,
      all_mail: 3,
      excluded: 0,
      categories: { primary: 1, promotions: 1, social: 0, updates: 0, forums: 0 },
    })),
    emailDetails: vi.fn((id: string) => Promise.resolve(
      id === 'p1' ? primaryEmail : id === 'pr1' ? promoEmail : archivedEmail)),
    accounts: vi.fn(() => Promise.resolve([
      {
        id: 'gmail_user',
        provider: 'gmail',
        email_address: 'user@gmail.com',
        display_name: 'User',
        connection_status: 'connected',
        backfill_complete: true,
      },
    ])),
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
    // still shows inbox mail too
    expect(screen.getByText('Q3 planning needed')).toBeInTheDocument();

    // category tabs disappear in All Mail view
    expect(screen.queryByRole('tab', { name: /Promotions/ })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'Inbox' }));
    await waitFor(() => {
      expect(screen.queryByText('Archived planning notes')).not.toBeInTheDocument();
    });
    expect(screen.getByRole('tab', { name: /Promotions/ })).toBeInTheDocument();
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
