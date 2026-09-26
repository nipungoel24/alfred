/// <reference types="node" />
import { beforeEach, describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { FocusIntentContext, focusTarget, isAttached } from '../lib/focus';
import type { FocusIntent, FocusTarget } from '../lib/focus';
import type { BriefingItem } from '../api/emails';
import { AccountsPage } from './accounts/AccountsPage';
import { SettingsPage } from './settings/SettingsPage';
import { TasksPage } from './tasks/TasksPage';
import { DeadlinesPage } from './deadlines/DeadlinesPage';

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return {
    ...original,
    accounts: vi.fn(),
    health: vi.fn(),
    analysisStatus: vi.fn(),
    tasks: vi.fn(),
    briefing: vi.fn(),
  };
});

vi.mock('../theme/ThemeProvider', () => ({
  useTheme: () => ({ preference: 'system', setPreference: vi.fn(), resolved: 'light' }),
}));

import { accounts, health, analysisStatus, tasks, briefing } from '../api/emails';

/**
 * Mirrors how App consumes focus intent: a provider plus an effect that moves
 * focus to the view heading when — and only when — intent was requested. Without
 * this the pages under test would fall back to the no-op default context and the
 * test would pass while proving nothing.
 */
function Shell({ children }: { children: React.ReactNode }) {
  const intent = useRef<FocusTarget | null>(null);
  const headingRef = useRef<HTMLHeadingElement | null>(null);
  const [version, setVersion] = useState(0);

  const value: FocusIntent = {
    requestFocus: (target) => {
      intent.current = target;
      if (target === 'view') setVersion(v => v + 1);
    },
    takeFocusIntent: (target) => {
      if (intent.current !== target) return false;
      intent.current = null;
      return true;
    },
  };

  useEffect(() => {
    if (!value.takeFocusIntent('view')) return;
    const heading = headingRef.current;
    if (isAttached(heading)) focusTarget(heading);
  }, [version, value]);

  return (
    <FocusIntentContext.Provider value={value}>
      <h1 tabIndex={-1} ref={headingRef}>View heading</h1>
      {children}
    </FocusIntentContext.Provider>
  );
}

function wrap(node: React.ReactNode) {
  return render(
    <Shell>
      <QueryClientProvider
        client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
      >
        {node}
      </QueryClientProvider>
    </Shell>
  );
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

describe('Accounts — retry keeps focus somewhere real', () => {
  it('focusing the retry button and recovering leaves a valid focus target', async () => {
    vi.mocked(accounts).mockRejectedValueOnce(new Error('down'));
    wrap(<AccountsPage />);

    const retry = await screen.findByRole('button', { name: /Try again/i });
    retry.focus();
    expect(document.activeElement).toBe(retry);

    vi.mocked(accounts).mockResolvedValue([
      {
        id: 'a1', provider: 'gmail', email_address: 'a@b.com',
        display_name: 'A', connection_status: 'connected', last_sync_at: null,
      },
    ]);
    fireEvent.click(retry);

    await screen.findByText('a@b.com');
    // The error block (and the button inside it) is gone. The view heading takes
    // focus so the user is not stranded on <body> with nothing to Tab from.
    await waitFor(() => expect(document.activeElement).not.toBe(document.body));
  });

  it('an error appearing on its own does not steal focus', async () => {
    vi.mocked(accounts).mockRejectedValue(new Error('down'));
    const { container } = wrap(
      <>
        <button type="button">outside control</button>
        <AccountsPage />
      </>
    );

    await screen.findByRole('alert');
    const outside = screen.getByRole('button', { name: 'outside control' });
    outside.focus();
    expect(document.activeElement).toBe(outside);

    // A background failure must not move the user.
    await new Promise((r) => setTimeout(r, 40));
    expect(document.activeElement).toBe(outside);
    expect(container).toBeTruthy();
  });

  it('a background refetch that repaints the list keeps focus', async () => {
    vi.mocked(accounts).mockResolvedValue([
      {
        id: 'a1', provider: 'gmail', email_address: 'a@b.com',
        display_name: 'A', connection_status: 'connected', last_sync_at: null,
      },
    ]);
    wrap(<AccountsPage />);

    const sync = await screen.findByRole('button', { name: /Sync now/i });
    sync.focus();
    expect(document.activeElement).toBe(sync);

    // Same data returning again: the list re-renders, focus must hold.
    vi.mocked(accounts).mockResolvedValue([
      {
        id: 'a1', provider: 'gmail', email_address: 'a@b.com',
        display_name: 'A', connection_status: 'connected',
        last_sync_at: '2026-09-20T00:00:00Z',
      },
    ]);
    await waitFor(() => expect(screen.getByRole('button', { name: /Sync now/i })).toBeInTheDocument());
    expect(document.activeElement).toBe(sync);
  });
});

describe('Settings — retry and background status polls', () => {
  it('a background AI status poll does not steal focus', async () => {
    vi.mocked(health).mockResolvedValue({ status: 'ok', ai: 'ready', build: 'b1' });
    vi.mocked(analysisStatus).mockResolvedValue({
      state: 'ready', model: 'm1', model_installed: true, ollama_installed: true,
      ollama_running: true, last_error: null, detail: null, pending: 0,
      worker_running: true, queue_paused: false,
    });
    wrap(<SettingsPage />);

    const theme = await screen.findByRole('radio', { name: /System/ });
    theme.focus();
    expect(document.activeElement).toBe(theme);

    // The runtime can change under the user (Ollama stops, model installs).
    vi.mocked(analysisStatus).mockResolvedValue({
      state: 'recovering', model: 'm1', model_installed: true, ollama_installed: true,
      ollama_running: false, last_error: null, detail: null, pending: 3,
      worker_running: false, queue_paused: false,
    });
    await new Promise((r) => setTimeout(r, 40));
    expect(document.activeElement).toBe(theme);
  });

  it('a runtime refetch that fails underneath the user does not steal focus', async () => {
    vi.mocked(health).mockResolvedValue({ status: 'ok', ai: 'ready', build: 'b1' });
    vi.mocked(analysisStatus).mockResolvedValue({
      state: 'ready', model: 'm1', model_installed: true, ollama_installed: true,
      ollama_running: true, last_error: null, detail: null, pending: 0,
      worker_running: true, queue_paused: false,
    });
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <Shell>
        <QueryClientProvider client={queryClient}>
          <SettingsPage />
        </QueryClientProvider>
      </Shell>
    );

    const theme = await screen.findByRole('radio', { name: /System/ });
    theme.focus();
    expect(document.activeElement).toBe(theme);

    // A refetch is how the runtime status changes under a user who is reading
    // something else. It replaces the rows; it must not replace their focus.
    vi.mocked(health).mockRejectedValue(new Error('down'));
    await queryClient.invalidateQueries({ queryKey: ['health'] });

    await screen.findByRole('alert');
    expect(document.activeElement).toBe(theme);
  });

  it('the theme control is reachable and operable by keyboard', async () => {
    vi.mocked(health).mockResolvedValue({ status: 'ok', ai: 'ready', build: 'b1' });
    vi.mocked(analysisStatus).mockResolvedValue({
      state: 'ready', model: 'm1', model_installed: true, ollama_installed: true,
      ollama_running: true, last_error: null, detail: null, pending: 0,
      worker_running: true, queue_paused: false,
    });
    wrap(<SettingsPage />);

    const system = await screen.findByRole('radio', { name: /System/ });
    system.focus();
    expect(document.activeElement).toBe(system);

    const dark = screen.getByRole('radio', { name: /Dark/ });
    fireEvent.click(dark);
    expect(document.activeElement).toBe(system);
  });
});

describe('Tasks and Deadlines — error and empty states hold focus still', () => {
  it('a background failure does not move focus off the page', async () => {
    vi.mocked(tasks).mockRejectedValue(new Error('down'));
    const { container } = wrap(
      <>
        <button type="button">outside</button>
        <TasksPage onOpenInMail={() => {}} />
      </>
    );

    await screen.findByRole('alert');
    const outside = screen.getByRole('button', { name: 'outside' });
    outside.focus();
    await new Promise((r) => setTimeout(r, 40));
    expect(document.activeElement).toBe(outside);
    expect(container).toBeTruthy();
  });

  it('a deadline poll that repaints rows does not move focus', async () => {
    const item: BriefingItem = {
      email_id: 'e1', sender: 'a@b.com', subject: 'Ship it',
      short_summary: 'Ship', priority: 'high', why_it_matters: 'Deadline',
      deadline: '2026-10-01', needs_reply: false,
    };
    vi.mocked(briefing).mockResolvedValue({
      executive_summary: 'One deadline.',
      total_emails: 1,
      urgent_count: 0,
      high_priority_count: 1,
      needs_reply_count: 0,
      deadline_count: 1,
      top_attention_items: [item],
      deadlines: [item],
      important_updates: [],
      can_wait_or_review_later: [],
    });
    wrap(<DeadlinesPage onOpenInMail={() => {}} />);

    const control = await screen.findByRole('button', { name: /Ship it/ });
    control.focus();
    expect(document.activeElement).toBe(control);

    // The briefing repaints under the user; focus must stay put.
    await new Promise((r) => setTimeout(r, 40));
    expect(document.activeElement).toBe(control);
  });
});
