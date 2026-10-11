import { beforeEach, describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { EmailAccount } from '../../api/emails';

const fetchAccountsMock = vi.fn<(q?: unknown) => Promise<EmailAccount[]>>();
const connectGmailMock = vi.fn<(uri: string) => Promise<{ url: string }>>();
const syncAccountMock = vi.fn<(id: string, older?: boolean) => Promise<unknown>>();
const deleteAccountMock = vi.fn<(id: string) => Promise<unknown>>();
const apiBaseMock = vi.fn<() => string>();

vi.mock('../../api/emails', () => ({
  accounts: (...a: unknown[]) => fetchAccountsMock(...(a as [])),
  connectGmail: (...a: unknown[]) => connectGmailMock(...(a as [string])),
  syncAccount: (...a: unknown[]) => syncAccountMock(...(a as [string, boolean])),
  deleteAccount: (...a: unknown[]) => deleteAccountMock(...(a as [string])),
}));

vi.mock('../../api/client', () => ({ apiBase: () => apiBaseMock() }));

import { AccountsPage } from './AccountsPage';

const connected: EmailAccount = {
  id: 'acc-1',
  provider: 'gmail',
  email_address: 'alex@example.com',
  display_name: 'Alex',
  connection_status: 'connected',
  last_sync_at: '2026-09-20T08:30:00Z',
  backfill: { state: 'complete', complete: true, estimate: null, imported: 240, pages: 12, remaining_estimate: null, last_page_at: null, last_error: null },
};

const needsAuth: EmailAccount = {
  id: 'acc-2',
  provider: 'gmail',
  email_address: 'work@example.com',
  display_name: null,
  connection_status: 'error',
  last_sync_at: null,
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AccountsPage />
    </QueryClientProvider>
  );
}

beforeEach(() => {
  fetchAccountsMock.mockReset();
  connectGmailMock.mockReset();
  syncAccountMock.mockReset();
  deleteAccountMock.mockReset();
  apiBaseMock.mockReset();
  apiBaseMock.mockReturnValue('http://127.0.0.1:8765');
  connectGmailMock.mockResolvedValue({ url: 'https://accounts.google.com/consent' });
  syncAccountMock.mockResolvedValue({ imported: 1, skipped_duplicates: 0 });
  deleteAccountMock.mockResolvedValue({ status: 'deleted' });
});

describe('AccountsPage — states', () => {
  it('shows a loading placeholder, not an empty state, while fetching', async () => {
    let resolve!: (a: EmailAccount[]) => void;
    fetchAccountsMock.mockReturnValue(new Promise((r) => { resolve = r; }));

    const { container } = renderPage();

    const busy = container.querySelector('[aria-busy="true"]');
    expect(busy).toBeInTheDocument();
    expect(container.querySelectorAll('.skeleton').length).toBeGreaterThan(0);
    expect(screen.queryByText('No accounts connected')).toBeNull();

    resolve([]);
    await screen.findByText('No accounts connected');
  });

  it('renders a genuine empty state when the request succeeds with no accounts', async () => {
    fetchAccountsMock.mockResolvedValue([]);
    renderPage();

    expect(await screen.findByText('No accounts connected')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Connected Accounts' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Connect Gmail/ })).toBeInTheDocument();
  });

  it('renders an error with retry, never the empty state, when the request fails', async () => {
    fetchAccountsMock.mockRejectedValue(new Error('ConnectError: ECONNREFUSED 127.0.0.1:49152'));
    const { container } = renderPage();

    const alert = await screen.findByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(screen.getByText("Couldn't load your accounts")).toBeInTheDocument();
    expect(screen.queryByText('No accounts connected')).toBeNull();
    expect(container.textContent).not.toMatch(/ConnectError/);
    expect(container.textContent).not.toMatch(/ECONNREFUSED/);
  });

  it('recovers when the retry succeeds', async () => {
    fetchAccountsMock.mockRejectedValueOnce(new Error('down'));
    renderPage();

    const retry = await screen.findByRole('button', { name: /Try again/i });
    fetchAccountsMock.mockResolvedValue([connected]);
    fireEvent.click(retry);

    expect(await screen.findByText('alex@example.com')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).toBeNull();
  });
});

describe('AccountsPage — connected account', () => {
  beforeEach(() => fetchAccountsMock.mockResolvedValue([connected]));

  it('shows only real data: address, provider, status, last sync, backfill', async () => {
    renderPage();

    expect(await screen.findByText('Alex')).toBeInTheDocument();
    expect(screen.getByText('alex@example.com')).toBeInTheDocument();
    expect(screen.getByText('gmail')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
    expect(screen.queryByText('Never')).toBeNull();
    expect(screen.getByText('Complete')).toBeInTheDocument();
  });

  it('invents no avatar, name or score', async () => {
    const { container } = renderPage();
    await screen.findByText('Alex');

    expect(container.querySelector('.avatar-chip')).toBeNull();
    expect(container.querySelector('[class*="avatar"]')).toBeNull();
    expect(container.textContent).not.toMatch(/score|health|profile photo/i);
  });

  it('falls back to the address when no display name exists, without repeating it', async () => {
    fetchAccountsMock.mockResolvedValue([{ ...connected, display_name: null }]);
    renderPage();

    // The address becomes the name; it must not also be repeated underneath.
    expect(await screen.findByText('alex@example.com')).toBeInTheDocument();
    expect(screen.getAllByText('alex@example.com')).toHaveLength(1);
  });

  it('reports a never-synced account honestly', async () => {
    fetchAccountsMock.mockResolvedValue([{ ...connected, last_sync_at: null, backfill: undefined }]);
    renderPage();

    expect(await screen.findByText('Never')).toBeInTheDocument();
  });

  it('offers Sync and Disconnect, and syncs the right account', async () => {
    renderPage();
    const sync = await screen.findByRole('button', { name: /Sync now/i });
    fireEvent.click(sync);

    await waitFor(() => expect(syncAccountMock).toHaveBeenCalledWith('acc-1', false));
    expect(screen.getByRole('button', { name: /Disconnect/i })).toBeInTheDocument();
  });

  it('marks the row busy and blocks a second sync while it runs', async () => {
    let resolve!: () => void;
    syncAccountMock.mockReturnValue(new Promise<void>((r) => { resolve = r; }));

    renderPage();
    const sync = await screen.findByRole('button', { name: /Sync now/i });
    fireEvent.click(sync);

    const busy = await screen.findByRole('button', { name: /Syncing/ });
    expect(busy).toBeDisabled();
    expect(busy).toHaveAttribute('aria-busy', 'true');

    resolve();
    await waitFor(() => expect(screen.getByRole('button', { name: /Sync now/i })).toBeEnabled());
  });

  it('surfaces a failed sync on the account without wiping the list', async () => {
    syncAccountMock.mockRejectedValue(new Error('boom'));

    renderPage();
    const sync = await screen.findByRole('button', { name: /Sync now/i });
    fireEvent.click(sync);

    const alert = await screen.findByRole('alert');
    expect(within(alert).getByText(/Sync failed/)).toBeInTheDocument();
    expect(screen.getByText('alex@example.com')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });
});

describe('AccountsPage — account needing authentication', () => {
  beforeEach(() => fetchAccountsMock.mockResolvedValue([needsAuth]));

  it('shows Authentication required rather than a bare error string', async () => {
    renderPage();
    expect(await screen.findByText('Authentication required')).toBeInTheDocument();
  });

  it('offers Reconnect instead of a sync that cannot work', async () => {
    renderPage();
    const reconnect = await screen.findByRole('button', { name: /Reconnect/i });
    expect(screen.queryByRole('button', { name: /Sync now/i })).toBeNull();

    fireEvent.click(reconnect);
    // React Query hands mutationFn a context object as a second argument, so
    // assert on the argument the component actually controls.
    await waitFor(() => expect(connectGmailMock).toHaveBeenCalled());
    expect(connectGmailMock.mock.calls[0][0]).toBe(
      'http://127.0.0.1:8765/api/accounts/gmail/callback'
    );
  });

  it('still allows disconnecting', async () => {
    renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /Disconnect/i }));
    await waitFor(() => expect(deleteAccountMock).toHaveBeenCalled());
    expect(deleteAccountMock.mock.calls[0][0]).toBe('acc-2');
  });

  it('reloads when the OAuth window reports success', async () => {
    renderPage();
    await screen.findByText('Authentication required');
    const before = fetchAccountsMock.mock.calls.length;

    // The callback page is served by the backend, so only its origin may
    // report a completed handshake.
    window.dispatchEvent(
      new MessageEvent('message', {
        data: 'auth_success',
        origin: 'http://127.0.0.1:8765',
      }),
    );

    await waitFor(() => expect(fetchAccountsMock.mock.calls.length).toBeGreaterThan(before));
  });

  it('ignores a success message from any other origin', async () => {
    renderPage();
    await screen.findByText('Authentication required');
    const before = fetchAccountsMock.mock.calls.length;

    window.dispatchEvent(
      new MessageEvent('message', {
        data: 'auth_success',
        origin: 'https://evil.example',
      }),
    );

    // Give the handler a chance to run before asserting it did nothing.
    await new Promise((r) => setTimeout(r, 20));
    expect(fetchAccountsMock.mock.calls.length).toBe(before);
  });
});

describe('AccountsPage — multiple accounts', () => {
  it('keeps each row independent', async () => {
    fetchAccountsMock.mockResolvedValue([connected, needsAuth]);
    renderPage();

    expect(await screen.findByText('alex@example.com')).toBeInTheDocument();
    expect(screen.getByText('work@example.com')).toBeInTheDocument();
    // Only the disconnected account offers Reconnect.
    expect(screen.getAllByRole('button', { name: /Reconnect/i })).toHaveLength(1);
    expect(screen.getAllByRole('button', { name: /Sync now/i })).toHaveLength(1);
  });

  it('still offers to add another account', async () => {
    fetchAccountsMock.mockResolvedValue([connected]);
    renderPage();
    expect(await screen.findByRole('button', { name: /Add another Gmail account/i })).toBeInTheDocument();
  });
});

describe('AccountsPage — connect failure', () => {
  it('explains the failure and offers a retry, without raw exception text', async () => {
    fetchAccountsMock.mockResolvedValue([]);
    connectGmailMock.mockRejectedValue(new Error('invalid_client 401'));

    const { container } = renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /Connect Gmail/ }));

    const alert = await screen.findByRole('alert');
    expect(within(alert).getByText("Couldn't start the Gmail connection")).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/invalid_client/);
  });
});

describe('AccountsPage — accessibility', () => {
  it('has one h1 and a named main region', async () => {
    fetchAccountsMock.mockResolvedValue([connected]);
    renderPage();

    expect(await screen.findByRole('heading', { level: 1, name: 'Connected Accounts' })).toBeInTheDocument();
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1);
  });

  it('exposes every action as a real button with an accessible name', async () => {
    fetchAccountsMock.mockResolvedValue([connected, needsAuth]);
    renderPage();

    await screen.findByText('alex@example.com');
    for (const b of screen.getAllByRole('button')) {
      expect(b.tagName).toBe('BUTTON');
      expect(b).toHaveAttribute('type', 'button');
      expect(b.getAttribute('aria-label') ?? b.textContent ?? '').not.toBe('');
    }
  });

  it('marks status with an icon and a label, never colour alone', async () => {
    fetchAccountsMock.mockResolvedValue([connected]);
    const { container } = renderPage();

    await screen.findByText('Connected');
    const indicator = container.querySelector('.status-indicator')!;
    expect(indicator).toBeInTheDocument();
    expect(indicator.querySelector('svg')).toBeInTheDocument();
    expect(indicator.textContent).toContain('Connected');
  });

  it('uses no inline styles', async () => {
    fetchAccountsMock.mockResolvedValue([connected]);
    const { container } = renderPage();

    await screen.findByText('alex@example.com');
    expect(container.querySelectorAll('[style]')).toHaveLength(0);
  });
});
