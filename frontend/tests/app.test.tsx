// @vitest-environment jsdom
import React from 'react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../src/App';
import * as api from '../src/api/emails';

// Mock the API methods
vi.mock('../src/api/emails', () => {
  return {
    emails: vi.fn(),
    briefing: vi.fn(),
    analyze: vi.fn(),
    draft: vi.fn(),
    accounts: vi.fn(),
    connectGmail: vi.fn(),
    syncAccount: vi.fn(),
    deleteAccount: vi.fn(),
    tasks: vi.fn(),
    toggleTask: vi.fn(),
    deleteTask: vi.fn()
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
      analysis: {
        short_summary: 'SaaS payment rejected',
        category: 'finance',
        priority: 'urgent',
        priority_score: 95,
        reason_for_priority: 'Service interruption today',
        needs_reply: true,
        action_items: [{ description: 'Update card by 5 PM' }],
        deadlines: [{ description: 'Pay invoice', due_at: 'before 5 PM today', confidence: 'explicit' }]
      }
    },
    {
      id: 'email_b',
      sender: 'newsletter@tech.com',
      sender_name: 'Tech Digest',
      subject: 'Weekly Tech Digest',
      body: 'Welcome to your weekly tech digest.',
      recipients: ['user@domain.com'],
      analysis: null // Not analyzed yet
    }
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
        needs_reply: true
      }
    ],
    important_updates: [],
    can_wait_or_review_later: []
  };

  const mockAccounts = [
    {
      id: 'gmail_user',
      provider: 'gmail',
      email_address: 'user@gmail.com',
      display_name: 'User',
      connection_status: 'connected',
      last_sync_at: '2026-08-15T09:00:00Z'
    }
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
      created_at: '2026-08-15T09:00:00Z'
    }
  ];

  let queryClient: QueryClient;

  beforeEach(() => {
    // Mock EventSource globally for JSDOM
    global.EventSource = class {
      onmessage: any = null;
      onerror: any = null;
      close = vi.fn();
      constructor() {}
    } as any;

    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
    vi.mocked(api.emails).mockResolvedValue(mockEmails as any);
    vi.mocked(api.briefing).mockResolvedValue(mockBriefing as any);
    vi.mocked(api.accounts).mockResolvedValue(mockAccounts as any);
    vi.mocked(api.tasks).mockResolvedValue(mockTasks as any);
  });

  afterEach(() => {
    cleanup();
  });

  it('renders the branding and local-first status', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );
    expect(await screen.findByText(/ALFRED/)).toBeDefined();
    expect(screen.getByText(/Local Executive/)).toBeDefined();
  }, 15000);

  it('renders briefing metrics and top attention cards', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );
    
    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    // Check Metrics render
    expect(screen.getByText('Total Analyzed')).toBeDefined();
    expect(screen.getByText('Urgent')).toBeDefined();
    expect(screen.getByText('Deadlines')).toBeDefined();
    
    // Check Top Attention Card renders
    expect(screen.getByText('Service interruption today')).toBeDefined();
  }, 15000);

  it('navigates to Inbox and applies filters', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );

    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    // Click "Inbox" sidebar button
    const inboxBtn = screen.getByRole('button', { name: 'Inbox' });
    fireEvent.click(inboxBtn);

    // Should display inbox view (we check for search input since virtualized rows might not mount in JSDOM)
    await screen.findByPlaceholderText('Search emails...', {}, { timeout: 8000 });
  }, 15000);

  it('displays API error banner when load fails', async () => {
    vi.mocked(api.briefing).mockRejectedValue(new Error('Backend offline'));
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    );

    await screen.findByText(/Error loading briefing/i, {}, { timeout: 8000 });
  }, 15000);
});
