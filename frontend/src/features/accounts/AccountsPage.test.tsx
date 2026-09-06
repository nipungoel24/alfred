import { beforeEach, describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const fetchAccountsMock = vi.fn();
const connectGmailMock = vi.fn();
const syncAccountMock = vi.fn();
const deleteAccountMock = vi.fn();
const apiBaseMock = vi.fn();

vi.mock('../../api/emails', () => ({
  accounts: (...args: unknown[]) => fetchAccountsMock(...args),
  connectGmail: (...args: unknown[]) => connectGmailMock(...args),
  syncAccount: (...args: unknown[]) => syncAccountMock(...args),
  deleteAccount: (...args: unknown[]) => deleteAccountMock(...args),
}));

vi.mock('../../api/client', () => ({
  apiBase: () => apiBaseMock(),
}));

import { AccountsPage } from './AccountsPage';

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <AccountsPage />
    </QueryClientProvider>
  );
}

describe('AccountsPage Gmail connect', () => {
  beforeEach(() => {
    fetchAccountsMock.mockReset();
    connectGmailMock.mockReset();
    apiBaseMock.mockReset();
    fetchAccountsMock.mockResolvedValue([]);
    connectGmailMock.mockResolvedValue({ url: 'https://accounts.google.com/consent' });
  });

  it('uses the runtime backend base for the OAuth redirect URI', async () => {
    // Packaged Tauri: the backend lives on a dynamic port, not 8765.
    apiBaseMock.mockReturnValue('http://127.0.0.1:65133');

    renderPage();
    const button = await screen.findByRole('button', { name: /Connect Gmail/ });
    fireEvent.click(button);

    await waitFor(() => expect(connectGmailMock).toHaveBeenCalled());
    expect(connectGmailMock.mock.calls[0][0]).toBe(
      'http://127.0.0.1:65133/api/accounts/gmail/callback'
    );
  });

  it('still resolves the dev callback URI when no Tauri base is set', async () => {
    apiBaseMock.mockReturnValue('http://127.0.0.1:8765');

    renderPage();
    const button = await screen.findByRole('button', { name: /Connect Gmail/ });
    fireEvent.click(button);

    await waitFor(() => expect(connectGmailMock).toHaveBeenCalled());
    expect(connectGmailMock.mock.calls[0][0]).toBe(
      'http://127.0.0.1:8765/api/accounts/gmail/callback'
    );
  });
});
