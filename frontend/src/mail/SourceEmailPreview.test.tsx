import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { SourceEmailPreview } from './SourceEmailPreview';

const detailsMock = vi.fn();

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return {
    ...original,
    emailDetails: (...args: unknown[]) => detailsMock(...args),
  };
});

function renderHarness() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  function Harness() {
    const [open, setOpen] = useState(false);
    return (
      <>
        <button type="button" onClick={() => setOpen(true)}>
          Open preview
        </button>
        {open && (
          <SourceEmailPreview
            emailId="email_1"
            onClose={() => setOpen(false)}
            onOpenInMail={() => {}}
            relationship={<button type="button">Relation action</button>}
          />
        )}
      </>
    );
  }
  return render(
    <QueryClientProvider client={queryClient}>
      <Harness />
    </QueryClientProvider>
  );
}

describe('SourceEmailPreview focus', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    detailsMock.mockResolvedValue({
      id: 'email_1',
      sender: 'boss@work.com',
      sender_name: 'Boss',
      subject: 'Q3 planning needed',
      body: 'Please send the plan.',
      received_at: '2026-08-17T09:00:00Z',
    });
  });

  it('moves initial focus to the close button on open', async () => {
    renderHarness();
    fireEvent.click(screen.getByRole('button', { name: 'Open preview' }));
    const close = await screen.findByRole('button', { name: 'Close source email preview' });
    await waitFor(() => {
      expect(close).toHaveFocus();
    });
  });

  it('traps Tab inside the dialog and wraps Shift+Tab', async () => {
    renderHarness();
    fireEvent.click(screen.getByRole('button', { name: 'Open preview' }));
    const close = await screen.findByRole('button', { name: 'Close source email preview' });
    await waitFor(() => expect(close).toHaveFocus());

    const dialog = screen.getByRole('dialog');
    const buttons = Array.from(dialog.querySelectorAll('button:not([disabled])')) as HTMLElement[];
    expect(buttons.length).toBeGreaterThan(1);
    const first = buttons[0];
    const last = buttons[buttons.length - 1];

    // Tab on the last control wraps to the first.
    last.focus();
    fireEvent.keyDown(document, { key: 'Tab' });
    expect(first).toHaveFocus();

    // Shift+Tab on the first control wraps to the last.
    first.focus();
    fireEvent.keyDown(document, { key: 'Tab', shiftKey: true });
    expect(last).toHaveFocus();
  });

  it('Escape closes the preview', async () => {
    renderHarness();
    fireEvent.click(screen.getByRole('button', { name: 'Open preview' }));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    fireEvent.keyDown(document, { key: 'Escape' });
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('restores focus to the opener on close', async () => {
    renderHarness();
    const opener = screen.getByRole('button', { name: 'Open preview' });
    opener.focus();
    fireEvent.click(opener);
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    fireEvent.keyDown(document, { key: 'Escape' });
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
    expect(opener).toHaveFocus();
  });
});
