// @vitest-environment jsdom
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../src/App';
import * as api from '../src/api/emails';

vi.mock('../src/api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../src/api/emails')>();
  return {
    ...actual,
    emails: vi.fn(),
    emailCounts: vi.fn(),
    emailDetails: vi.fn(),
    briefing: vi.fn(),
    analyze: vi.fn(),
    draft: vi.fn(),
    accounts: vi.fn(),
    connectGmail: vi.fn(),
    syncAccount: vi.fn(),
    deleteAccount: vi.fn(),
    tasks: vi.fn(),
    toggleTask: vi.fn(),
    deleteTask: vi.fn(),
    health: vi.fn(),
    regenerateBriefing: vi.fn(),
  };
});

describe('Alfred Frontend Application', () => {
  const mockEmails = [
    {
      id: 'email_a',
      sender: 'billing@saas.com',
      sender_name: 'Billing',
      subject: 'Payment failed - action required today',
      body: 'Our payment processor rejected the subscription renewal.',
      recipients: ['user@domain.com'],
      received_at: '2026-08-17T09:00:00Z',
      label_ids: ['INBOX', 'UNREAD', 'CATEGORY_PERSONAL'],
      analysis: {
        short_summary: 'SaaS payment rejected',
        category: 'finance',
        priority: 'urgent',
        priority_score: 95,
        reason_for_priority: 'Service interruption today',
        needs_reply: true,
        action_items: [{ description: 'Update card by 5 PM' }],
        deadlines: [{ description: 'Pay invoice', due_at: 'before 5 PM today', confidence: 'explicit' }],
        important_details: [],
      },
    },
    {
      id: 'email_b',
      sender: 'newsletter@tech.com',
      sender_name: 'Tech Digest',
      subject: 'Weekly Tech Digest',
      body: 'Welcome to your weekly tech digest.',
      recipients: ['user@domain.com'],
      received_at: '2026-08-16T09:00:00Z',
      label_ids: ['INBOX', 'CATEGORY_PROMOTIONS'],
      analysis: null,
    },
  ];

  const mockBriefing = {
    executive_summary: 'One payment failed. Tech newsletter received.',
    total_emails: 2,
    urgent_count: 1,
    high_priority_count: 0,
    needs_reply_count: 1,
    deadline_count: 1,
    top_attention_items: [
      {
        email_id: 'email_a',
        sender: 'Billing',
        subject: 'Payment failed - action required today',
        short_summary: 'SaaS payment rejected',
        priority: 'urgent',
        why_it_matters: 'Service interruption today',
        deadline: 'before 5 PM today',
        needs_reply: true,
      },
    ],
    important_updates: [],
    can_wait_or_review_later: [],
  };

  const mockAccounts = [
    {
      id: 'gmail_user',
      provider: 'gmail',
      email_address: 'user@gmail.com',
      display_name: 'User',
      connection_status: 'connected',
      last_sync_at: '2026-08-15T09:00:00Z',
    },
  ];

  const mockTasks = [
    {
      id: 'task_email_a_0',
      source_email_id: 'email_a',
      source_thread_id: 'thread_a',
      title: 'Update card by 5 PM',
      description: 'Owner: Billing',
      due_at: '5 PM today',
      priority: 'urgent',
      status: 'pending',
      created_at: '2026-08-15T09:00:00Z',
    },
  ];

  let queryClient: QueryClient;

  beforeEach(() => {
    global.EventSource = class {
      onmessage: (event: MessageEvent) => void = () => {};
      onerror: () => void = () => {};
      close = vi.fn();
      constructor() {}
    } as unknown as typeof EventSource;

    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    vi.clearAllMocks();
    vi.mocked(api.emails).mockResolvedValue(mockEmails as never);
    vi.mocked(api.emailCounts).mockResolvedValue({
      active_inbox: 2,
      excluded: 0,
      categories: { primary: 1, promotions: 1, social: 0, updates: 0, forums: 0 },
    } as never);
    vi.mocked(api.briefing).mockResolvedValue(mockBriefing as never);
    vi.mocked(api.regenerateBriefing).mockResolvedValue(mockBriefing as never);
    vi.mocked(api.accounts).mockResolvedValue(mockAccounts as never);
    vi.mocked(api.tasks).mockResolvedValue(mockTasks as never);
    vi.mocked(api.health).mockResolvedValue({ status: 'ok', ai: 'ready' });
  });

  afterEach(() => {
    cleanup();
  });

  it('renders the icon rail and local-first status', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );
    expect(await screen.findByRole('button', { name: 'Mail' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Overview' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Tasks' })).toBeInTheDocument();
    expect(await screen.findByText(/AI Ready/)).toBeInTheDocument();
  }, 15000);

  it('renders briefing metrics and top attention items on Overview', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );

    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    expect(screen.getByText('Inbox')).toBeInTheDocument();
    expect(screen.getByText('Important')).toBeInTheDocument();
    expect(screen.getByText('Deadlines')).toBeInTheDocument();
    expect(screen.getByText('Needs Your Attention')).toBeInTheDocument();
  }, 15000);

  it('navigates to Mail workspace via the rail', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );

    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    fireEvent.click(screen.getByRole('button', { name: 'Mail' }));

    await screen.findByRole('tab', { name: /Primary/ }, { timeout: 8000 });
    expect(screen.getByRole('tab', { name: /Promotions/ })).toBeInTheDocument();
    expect(screen.getByRole('searchbox')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Payment failed - action required today')).toBeInTheDocument();
    });
  }, 15000);

  it('uses high-priority email analysis when the briefing has no attention items', async () => {
    vi.mocked(api.briefing).mockResolvedValue({
      ...mockBriefing,
      top_attention_items: [],
      deadlines: [],
    } as never);
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );

    expect(await screen.findByText('Payment failed - action required today', {}, { timeout: 8000 })).toBeInTheDocument();
  }, 15000);
});
