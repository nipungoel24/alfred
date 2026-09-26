/// <reference types="node" />
import { beforeEach, describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MailWorkspace } from './MailWorkspace';
import { FocusIntentContext } from '../lib/focus';
import type { FocusTarget } from '../lib/focus';
import type { Email } from '../api/emails';

/**
 * Focus behaviour, asserted on `document.activeElement` rather than on the
 * presence of an element. A focus defect is invisible to "does it render"
 * assertions, which is the whole reason this file exists.
 */

const primaryEmail: Email = {
  id: 'p1',
  sender: 'boss@work.com',
  sender_name: 'Boss',
  recipients: ['me@gmail.com'],
  subject: 'Q3 planning needed',
  body: 'Please send the plan by Friday.',
  received_at: '2026-08-17T09:00:00Z',
  label_ids: ['INBOX'],
  analysis: null,
};

const secondEmail: Email = {
  ...primaryEmail,
  id: 'p2',
  subject: 'Second message',
  sender: 'someone@else.com',
  sender_name: 'Someone',
};

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return {
    ...original,
    emails: vi.fn(() => Promise.resolve([primaryEmail, secondEmail])),
    emailDetails: vi.fn((id: string) =>
      Promise.resolve(id === 'p1' ? primaryEmail : secondEmail)
    ),
    emailCounts: vi.fn(() => Promise.resolve({
      active_inbox: 2,
      all_mail: 2,
      excluded: 0,
      categories: { primary: 2, promotions: 0, social: 0, updates: 0, forums: 0 },
    })),
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
          imported: 2,
          pages: 1,
          remaining_estimate: null,
          last_page_at: null,
          last_error: null,
        },
      },
    ])),
    backfillAccount: vi.fn(),
    pauseBackfill: vi.fn(),
    searchEmailsStructured: vi.fn(() => Promise.resolve([])),
  };
});

/** Records intent exactly as App does, and lets a test fire it. */
function makeIntent() {
  let pending: FocusTarget | null = null;
  return {
    requestFocus: (t: FocusTarget) => { pending = t; },
    takeFocusIntent: (t: FocusTarget) => {
      if (pending !== t) return false;
      pending = null;
      return true;
    },
  };
}

function renderWorkspace() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  const intent = makeIntent();
  const utils = render(
    <FocusIntentContext.Provider value={intent}>
      <QueryClientProvider client={queryClient}>
        <MailWorkspace
          searchQuery=""
          onClearSearch={() => {}}
          onSearchChange={() => {}}
          openEmailId={null}
          onConsumeOpenEmail={() => {}}
          syncState={{ syncing: false, lastSyncByAccount: {} }}
          syncReport={null}
          onDismissSyncReport={() => {}}
          onRequestSync={() => {}}
        />
      </QueryClientProvider>
    </FocusIntentContext.Provider>
  );
  return { ...utils, intent };
}

function activeInfo() {
  const el = document.activeElement as HTMLElement | null;
  if (!el) return 'none';
  return `${el.tagName}:${(el.textContent ?? '').trim().slice(0, 40)}`;
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

describe('message activation moves focus into the reader', () => {
  it('keyboard activation focuses the reader subject heading', async () => {
    renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    const rowButton = row.closest('[role="button"]') as HTMLElement;
    rowButton.focus();
    expect(document.activeElement).toBe(rowButton);

    fireEvent.keyDown(rowButton, { key: 'Enter' });

    await waitFor(() => {
      const subject = screen.getByRole('heading', { level: 2, name: 'Q3 planning needed' });
      expect(document.activeElement).toBe(subject);
    });
  });

  it('consumes reader focus intent exactly once, so a later refetch cannot re-fire it', async () => {
    const { intent } = renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    fireEvent.keyDown(row.closest('[role="button"]') as HTMLElement, { key: 'Enter' });

    const subject = await screen.findByRole('heading', { level: 2, name: 'Q3 planning needed' });
    await waitFor(() => expect(document.activeElement).toBe(subject));

    // Already consumed by the component: nothing is left for anyone else to act on.
    await waitFor(() => expect(intent.takeFocusIntent('reader')).toBe(false));
  });

  it('leaves focus on the row for a pointer click', async () => {
    renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    const rowButton = row.closest('[role="button"]') as HTMLElement;
    rowButton.focus();

    fireEvent.click(rowButton);

    // Content updated...
    await screen.findByRole('heading', { level: 2, name: 'Q3 planning needed' });
    // ...but a mouse user keeps focus where they already were.
    expect(document.activeElement).toBe(rowButton);
  });

  it('moves focus to the new subject when activating a second message', async () => {
    renderWorkspace();
    const first = await screen.findByText('Q3 planning needed');
    fireEvent.keyDown(first.closest('[role="button"]') as HTMLElement, { key: 'Enter' });
    await waitFor(() =>
      expect(document.activeElement).toBe(
        screen.getByRole('heading', { level: 2, name: 'Q3 planning needed' })
      )
    );

    const second = await screen.findByText('Second message');
    const secondRow = second.closest('[role="button"]') as HTMLElement;
    secondRow.focus();
    fireEvent.keyDown(secondRow, { key: ' ' });

    await waitFor(() => {
      const subject = screen.getByRole('heading', { level: 2, name: 'Second message' });
      expect(document.activeElement).toBe(subject);
    });
  });

  it('gives the subject a focus target without adding a tab stop', async () => {
    renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    fireEvent.click(row.closest('[role="button"]') as HTMLElement);

    // Scoped to the reader: the intelligence panel has its own level-2 heading.
    const subject = await screen.findByRole('heading', { level: 2, name: 'Q3 planning needed' });
    expect(subject).toHaveAttribute('tabindex', '-1');
    // tabindex="-1" is programmatically focusable but never a Tab stop.
    expect(subject.tabIndex).toBe(-1);
  });
});

describe('focus survives background activity', () => {
  it('an account poll that re-renders the list does not steal focus', async () => {
    const { rerender } = renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    const rowButton = row.closest('[role="button"]') as HTMLElement;
    fireEvent.click(rowButton);
    await screen.findByRole('heading', { level: 2, name: 'Q3 planning needed' });

    rowButton.focus();
    expect(document.activeElement).toBe(rowButton);

    // Re-render with the same props, the way a poll or an invalidation does.
    rerender(
      <FocusIntentContext.Provider value={makeIntent()}>
        <QueryClientProvider client={new QueryClient()}>
          <MailWorkspace
            searchQuery=""
            onClearSearch={() => {}}
            onSearchChange={() => {}}
            openEmailId={null}
            onConsumeOpenEmail={() => {}}
            syncState={{ syncing: false, lastSyncByAccount: {} }}
            syncReport={null}
            onDismissSyncReport={() => {}}
            onRequestSync={() => {}}
          />
        </QueryClientProvider>
      </FocusIntentContext.Provider>
    );

    await new Promise((r) => setTimeout(r, 30));
    expect(document.activeElement).toBe(rowButton);
  });

  it('selecting the already-selected message does not move focus', async () => {
    renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    const rowButton = row.closest('[role="button"]') as HTMLElement;
    fireEvent.keyDown(rowButton, { key: 'Enter' });
    // Wait for the move to actually settle, otherwise the next focus() races it.
    await waitFor(() => expect(document.activeElement?.tagName).toBe('H2'));

    rowButton.focus();
    expect(document.activeElement).toBe(rowButton);

    // Same id: state is unchanged, so no intent is recorded and focus holds.
    fireEvent.keyDown(rowButton, { key: 'Enter' });
    await new Promise((r) => setTimeout(r, 40));
    expect(document.activeElement).toBe(rowButton);
  });
});

describe('focus is never orphaned', () => {
  it('keyboard activation always lands on a real focus target', async () => {
    renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    const rowButton = row.closest('[role="button"]') as HTMLElement;

    rowButton.focus();
    fireEvent.keyDown(rowButton, { key: 'Enter' });

    // The reader is queried asynchronously, so focus arrives after the subject
    // exists — waiting on "not body" would be satisfied by the row itself.
    await waitFor(() => expect(document.activeElement?.tagName).toBe('H2'));
    expect(activeInfo()).not.toBe('BODY:');
  });

  it('a row is a real focus stop, so focus can always be placed on one', async () => {
    renderWorkspace();
    const row = await screen.findByText('Q3 planning needed');
    const rowButton = row.closest('[role="button"]') as HTMLElement;
    rowButton.focus();
    expect(document.activeElement).toBe(rowButton);
    expect(rowButton.tabIndex).toBe(0);
  });
});
