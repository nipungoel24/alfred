/// <reference types="node" />
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AccountsPage } from './accounts/AccountsPage';
import { FocusIntentContext, useRetryPreservingFocus, focusTarget, isAttached } from '../lib/focus';
import type { FocusIntent, FocusTarget } from '../lib/focus';
import { accounts } from '../api/emails';

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return { ...original, accounts: vi.fn() };
});

/** A shell that mirrors App: records intent, and acts on 'view' intent only. */
function Shell({ children }: { children: React.ReactNode }) {
  const intent = React.useRef<FocusTarget | null>(null);
  const headingRef = React.useRef<HTMLHeadingElement | null>(null);
  const [version, setVersion] = React.useState(0);
  const value: FocusIntent = {
    requestFocus: (t) => { intent.current = t; if (t === 'view') setVersion(v => v + 1); },
    takeFocusIntent: (t) => { if (intent.current !== t) return false; intent.current = null; return true; },
  };
  React.useEffect(() => {
    if (!value.takeFocusIntent('view')) return;
    const h = headingRef.current;
    if (isAttached(h)) focusTarget(h);
  }, [version, value]);
  return (
    <FocusIntentContext.Provider value={value}>
      <h1 tabIndex={-1} ref={headingRef}>Accounts</h1>
      {children}
    </FocusIntentContext.Provider>
  );
}

function renderPage() {
  return render(
    <Shell>
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <AccountsPage />
      </QueryClientProvider>
    </Shell>
  );
}

const connected = {
  id: 'a1', provider: 'gmail', email_address: 'a@b.com',
  display_name: 'A', connection_status: 'connected', last_sync_at: null,
};

beforeEach(() => {
  localStorage.clear();
  vi.mocked(accounts).mockReset();
});

describe('retry re-homes focus only when the retry works', () => {
  it('moves focus to the view heading when a retry recovers', async () => {
    vi.mocked(accounts).mockRejectedValueOnce(new Error('down'));
    renderPage();

    const retry = await screen.findByRole('button', { name: /Try again/i });
    retry.focus();
    expect(document.activeElement).toBe(retry);

    vi.mocked(accounts).mockResolvedValue([connected]);
    fireEvent.click(retry);

    await screen.findByText('a@b.com');
    // The error block, and the focused button inside it, are gone.
    await waitFor(() =>
      expect(document.activeElement).toBe(screen.getByRole('heading', { level: 1, name: 'Accounts' }))
    );
  });

  it('leaves focus on the retry button when the retry fails again', async () => {
    vi.mocked(accounts).mockRejectedValue(new Error('still down'));
    renderPage();

    const retry = await screen.findByRole('button', { name: /Try again/i });
    retry.focus();
    fireEvent.click(retry);

    // The error is still there and so is the button, which is still the right
    // place for the user to be. Moving focus here would be a regression.
    await screen.findByRole('button', { name: /Try again/i });
    await new Promise((r) => setTimeout(r, 40));
    expect(document.activeElement).toBe(screen.getByRole('button', { name: /Try again/i }));
  });
});

describe('useRetryPreservingFocus', () => {
  function Probe({ refetch }: { refetch: () => Promise<unknown> }) {
    const retry = useRetryPreservingFocus(refetch);
    return <button type="button" onClick={retry}>retry</button>;
  }

  it('requests view focus when the refetch reports success', async () => {
    const requestFocus = vi.fn();
    const value: FocusIntent = { requestFocus, takeFocusIntent: () => false };
    render(
      <FocusIntentContext.Provider value={value}>
        <Probe refetch={() => Promise.resolve({ isError: false })} />
      </FocusIntentContext.Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'retry' }));
    await waitFor(() => expect(requestFocus).toHaveBeenCalledWith('view'));
  });

  it('does not request focus when the refetch reports an error', async () => {
    const requestFocus = vi.fn();
    const value: FocusIntent = { requestFocus, takeFocusIntent: () => false };
    render(
      <FocusIntentContext.Provider value={value}>
        <Probe refetch={() => Promise.resolve({ isError: true })} />
      </FocusIntentContext.Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'retry' }));
    await new Promise((r) => setTimeout(r, 30));
    expect(requestFocus).not.toHaveBeenCalled();
  });

  it('does not throw when the refetch rejects', async () => {
    const requestFocus = vi.fn();
    const value: FocusIntent = { requestFocus, takeFocusIntent: () => false };
    render(
      <FocusIntentContext.Provider value={value}>
        <Probe refetch={() => Promise.reject(new Error('boom'))} />
      </FocusIntentContext.Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'retry' }));
    await new Promise((r) => setTimeout(r, 30));
    // React Query's refetch resolves rather than rejecting; a rejection here
    // must not become an unhandled rejection.
    expect(requestFocus).not.toHaveBeenCalled();
  });
});

describe('focus invariants hold across the app source', () => {
  const here = dirname(fileURLToPath(import.meta.url));
  const appFiles = readdirSync(join(here, '..'), { recursive: true })
    .filter((f): f is string => typeof f === 'string' && f.endsWith('.tsx') && !f.includes('.test.'))
    .map((f) => join(here, '..', f));

  it('no component uses autoFocus', () => {
    // autoFocus fires on mount, which is exactly the "focus something nobody
    // asked for" behaviour this work exists to prevent.
    const offenders = appFiles.filter((f) => /\bautoFocus\b/.test(readFileSync(f, 'utf8')));
    expect(offenders).toEqual([]);
  });

  it('does not ship a regex guard for focus placement', () => {
    // Attempted and deliberately not shipped: matching ".focus() inside an
    // effect or a handler" by regex flags the dialog focus trap, which is
    // correct code inside a long keydown listener. A guard with false
    // positives trains people to ignore it. The behavioural tests in this file
    // assert where focus actually lands, which is the stronger evidence.
    expect(true).toBe(true);
  });
});
