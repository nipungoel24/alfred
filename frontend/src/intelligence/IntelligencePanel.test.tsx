import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { IntelligencePanel } from './IntelligencePanel';
import type { Email } from '../api/emails';

vi.mock('../api/emails', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/emails')>();
  return { ...actual, draft: vi.fn(async () => ({ draft: 'Hello,\n\nSounds good.' })) };
});

function email(analysis: Email['analysis']): Email {
  return {
    id: 'e1',
    sender: 'a@example.com',
    recipients: ['me@example.com'],
    subject: 'Q3 plan',
    body: 'text',
    label_ids: ['INBOX'],
    analysis,
  };
}

const full = {
  short_summary: 'Alice wants the Q3 plan by Friday.',
  category: 'work',
  priority: 'high' as const,
  priority_score: 82,
  reason_for_priority: 'A commitment was made to a deadline.',
  needs_reply: true,
  action_items: [{ description: 'Send the Q3 plan', owner: 'user', deadline: 'Friday' }],
  deadlines: [{ description: 'Q3 plan', due_at: 'Friday' }],
  important_details: ['Budget was cut by 12%.'],
};

function renderPanel(props: Partial<React.ComponentProps<typeof IntelligencePanel>> = {}) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <IntelligencePanel email={email(full)} {...props} />
    </QueryClientProvider>,
  );
}

describe('IntelligencePanel', () => {
  it('is a complementary landmark with an accessible name', () => {
    renderPanel();
    expect(
      screen.getByRole('complementary', { name: /alfred intelligence/i }),
    ).toBeInTheDocument();
  });

  it('shows every section when the analysis has the data', () => {
    renderPanel();
    expect(screen.getByText('Summary')).toBeInTheDocument();
    expect(screen.getByText('Why it matters')).toBeInTheDocument();
    expect(screen.getByText('Needs reply')).toBeInTheDocument();
    expect(screen.getByText('Deadlines')).toBeInTheDocument();
    expect(screen.getByText('Tasks')).toBeInTheDocument();
    expect(screen.getByText('Context')).toBeInTheDocument();
  });

  it('shows the real analysis text, not a placeholder', () => {
    renderPanel();
    expect(screen.getByText('Alice wants the Q3 plan by Friday.')).toBeInTheDocument();
    expect(screen.getByText('A commitment was made to a deadline.')).toBeInTheDocument();
    expect(screen.getByText('Send the Q3 plan')).toBeInTheDocument();
    expect(screen.getByText('Budget was cut by 12%.')).toBeInTheDocument();
  });

  it('omits sections that have no data rather than rendering them empty', () => {
    renderPanel({
      email: email({
        ...full,
        action_items: [],
        deadlines: [],
        important_details: [],
        needs_reply: false,
        reason_for_priority: '',
      }),
    });
    expect(screen.getByText('Summary')).toBeInTheDocument();
    expect(screen.queryByText('Why it matters')).not.toBeInTheDocument();
    expect(screen.queryByText('Needs reply')).not.toBeInTheDocument();
    expect(screen.queryByText('Deadlines')).not.toBeInTheDocument();
    expect(screen.queryByText('Tasks')).not.toBeInTheDocument();
    expect(screen.queryByText('Context')).not.toBeInTheDocument();
  });

  it('offers the draft action only when a reply is expected', () => {
    const { unmount } = renderPanel();
    expect(screen.getByRole('button', { name: /draft a reply/i })).toBeInTheDocument();
    unmount();

    renderPanel({ email: email({ ...full, needs_reply: false }) });
    expect(screen.queryByRole('button', { name: /draft a reply/i })).not.toBeInTheDocument();
  });

  it('explains an offline runtime instead of saying "pending" forever', () => {
    renderPanel({ email: email(null), aiState: 'ollama_not_running' });
    expect(screen.getByText('Local AI is offline')).toBeInTheDocument();
    expect(screen.getByText(/mailbox works fully/i)).toBeInTheDocument();
    expect(screen.queryByText(/pending/i)).not.toBeInTheDocument();
  });

  it('explains a missing model and points at Settings', () => {
    renderPanel({ email: email(null), aiState: 'model_missing', onOpenSettings: () => {} });
    expect(screen.getByText('No local model installed')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /open settings/i })).toBeInTheDocument();
  });

  it('says a pending analysis is pending, without inventing a result', () => {
    renderPanel({ email: email(null), aiState: 'ready' });
    expect(screen.getByText('Analysing this message')).toBeInTheDocument();
    expect(screen.queryByText(/summary/i)).not.toBeInTheDocument();
  });

  it('states plainly when there is genuinely nothing to add', () => {
    // A cached analysis written by an older model version can carry none of
    // the fields the panel renders. That is a real result, not a failure, and
    // it must not be padded with placeholder sections.
    renderPanel({ email: email({} as Email['analysis']) });
    expect(screen.getByText('Nothing to add')).toBeInTheDocument();
    expect(screen.getByText(/not a failure/i)).toBeInTheDocument();
  });

  it('gives the close control an accessible name', () => {
    renderPanel({ onClose: () => {} });
    expect(screen.getByRole('button', { name: /close alfred panel/i })).toBeInTheDocument();
  });

  it('omits the close control when it cannot be closed', () => {
    renderPanel();
    expect(screen.queryByRole('button', { name: /close alfred panel/i })).not.toBeInTheDocument();
  });

  it('renders sections as headings so they can be navigated', () => {
    renderPanel();
    expect(screen.getByRole('heading', { name: 'Summary' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Tasks' })).toBeInTheDocument();
  });
});
