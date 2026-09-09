import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DeadlinesPage } from './DeadlinesPage';

const briefingMock = vi.fn();
const detailsMock = vi.fn();

vi.mock('../../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../api/emails')>();
  return {
    ...original,
    briefing: (...args: unknown[]) => briefingMock(...args),
    emailDetails: (...args: unknown[]) => detailsMock(...args),
  };
});

function renderPage(onOpenInMail: (id: string) => void = () => {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <DeadlinesPage onOpenInMail={onOpenInMail} />
    </QueryClientProvider>
  );
}

describe('DeadlinesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    briefingMock.mockResolvedValue({
      deadlines: [
        {
          email_id: 'email_dl_1',
          sender: 'Client',
          subject: 'Contract renewal',
          short_summary: 'Renew by Friday',
          priority: 'high',
          why_it_matters: 'Revenue at risk',
          deadline: 'Friday',
          needs_reply: true,
        },
      ],
    });
    detailsMock.mockResolvedValue({
      id: 'email_dl_1',
      sender: 'client@corp.com',
      sender_name: 'Client',
      subject: 'Contract renewal',
      body: 'Please renew the contract by Friday.',
      received_at: '2026-08-17T09:00:00Z',
    });
  });

  it('opens the source email preview from View email using email_id', async () => {
    renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Contract renewal/ }));
    expect(detailsMock).toHaveBeenCalledWith('email_dl_1');
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(await screen.findByText('Contract renewal')).toBeInTheDocument();
  });

  it('shows no task controls for a deadline preview', async () => {
    renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Contract renewal/ }));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(screen.queryByText('Detected task')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Not a task' })).not.toBeInTheDocument();
  });

  it('Open in Mail from the preview navigates with the exact id', async () => {
    const onOpenInMail = vi.fn();
    renderPage(onOpenInMail);
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Contract renewal/ }));
    fireEvent.click(await screen.findByRole('button', { name: 'Open in Mail' }));
    expect(onOpenInMail).toHaveBeenCalledWith('email_dl_1');
  });
});
