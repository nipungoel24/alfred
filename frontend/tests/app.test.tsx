// @vitest-environment jsdom
import React from 'react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
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

  beforeEach(() => {
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
    render(<App />);
    expect(screen.getByText(/ALFRED/)).toBeDefined();
    expect(screen.getByText(/Local-first AI/)).toBeDefined();
  }, 15000);

  it('renders briefing metrics and top attention cards', async () => {
    render(<App />);
    
    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    // Check Metrics render
    expect(screen.getByText('Total Emails')).toBeDefined();
    expect(screen.getByText('Urgent')).toBeDefined();
    expect(screen.getAllByText('Deadlines')).toBeDefined();
    
    // Check Top Attention Card renders
    expect(screen.getByText('Why it matters: Service interruption today')).toBeDefined();
  }, 15000);

  it('navigates to Inbox and applies filters', async () => {
    render(<App />);

    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    // Click "Inbox" sidebar button
    const inboxBtn = screen.getByRole('button', { name: 'Inbox' });
    fireEvent.click(inboxBtn);

    // Should display inbox emails
    await screen.findByText('Billing', {}, { timeout: 8000 });
    await screen.findByText('Tech Digest', {}, { timeout: 8000 });
  }, 15000);

  it('opens and closes email detail modal', async () => {
    render(<App />);
    
    await screen.findByText('One payment failed. Tech newsletter received.', {}, { timeout: 8000 });

    // Click "Inbox"
    fireEvent.click(screen.getByRole('button', { name: 'Inbox' }));

    // Open first email
    const billingRow = await screen.findByText('Billing', {}, { timeout: 8000 });
    fireEvent.click(billingRow);

    // Modal details should be visible
    await screen.findByText(/billing@saas.com/, {}, { timeout: 8000 });
    expect(screen.getByText('Our payment processor rejected the subscription renewal.')).toBeDefined();
    expect(screen.getByText(/Update card by 5 PM/)).toBeDefined();

    // Close modal using bulletproof class query
    const closeBtn = document.querySelector('.close');
    expect(closeBtn).not.toBeNull();
    fireEvent.click(closeBtn!);
    
    await waitFor(() => {
      expect(screen.queryByText(/billing@saas.com/)).toBeNull();
    }, { timeout: 8000 });
  }, 15000);

  it('displays API error banner when load fails', async () => {
    vi.mocked(api.accounts).mockRejectedValue(new Error('Backend offline'));
    render(<App />);

    await screen.findByText('Backend offline', {}, { timeout: 8000 });
  }, 15000);
});
