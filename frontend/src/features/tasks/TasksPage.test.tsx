import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TasksPage } from './TasksPage';

const tasksMock = vi.fn();
const toggleMock = vi.fn();
const dismissMock = vi.fn();
const patchMock = vi.fn();
const detailsMock = vi.fn();

vi.mock('../../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../api/emails')>();
  return {
    ...original,
    tasks: (...args: unknown[]) => tasksMock(...args),
    toggleTask: (...args: unknown[]) => toggleMock(...args),
    dismissTask: (...args: unknown[]) => dismissMock(...args),
    patchTaskPriority: (...args: unknown[]) => patchMock(...args),
    emailDetails: (...args: unknown[]) => detailsMock(...args),
  };
});

const task = {
  id: 'task_1',
  source_email_id: 'email_src_1',
  title: 'Send the Q3 plan',
  description: 'Owner: user',
  due_at: 'Friday',
  priority: 'high',
  status: 'pending',
  created_at: '2026-08-17T09:00:00Z',
};

function renderPage(onOpenInMail: (id: string) => void = () => {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TasksPage onOpenInMail={onOpenInMail} />
    </QueryClientProvider>
  );
}

describe('TasksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    tasksMock.mockResolvedValue([task]);
    detailsMock.mockResolvedValue({
      id: 'email_src_1',
      sender: 'boss@work.com',
      sender_name: 'Boss',
      subject: 'Q3 planning needed',
      body: 'Please send the plan by Friday.',
      received_at: '2026-08-17T09:00:00Z',
    });
  });

  it('opens the source email preview from View email using source_email_id', async () => {
    renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Send the Q3 plan/ }));
    expect(detailsMock).toHaveBeenCalledWith('email_src_1');
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(await screen.findByText('Q3 planning needed')).toBeInTheDocument();
  });

  it('Not a task dismisses durably and closes the preview', async () => {
    dismissMock.mockResolvedValue({ status: 'dismissed' });
    renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Send the Q3 plan/ }));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Not a task' }));
    await waitFor(() => {
      expect(dismissMock).toHaveBeenCalled();
    });
    expect(dismissMock.mock.calls[0][0]).toBe('task_1');
  });

  it('priority edit calls the PATCH endpoint and invalidates tasks', async () => {
    patchMock.mockResolvedValue({ ...task, priority: 'low', priority_override: 'low' });
    renderPage();
    const select = await screen.findByRole('combobox', { name: /Priority for Send the Q3 plan/ });
    fireEvent.change(select, { target: { value: 'low' } });
    await waitFor(() => {
      expect(patchMock).toHaveBeenCalled();
    });
    expect(patchMock.mock.calls[0][0]).toBe('task_1');
    expect(patchMock.mock.calls[0][1]).toBe('low');
  });

  it('Open in Mail from the preview navigates with the exact source id', async () => {
    const onOpenInMail = vi.fn();
    renderPage(onOpenInMail);
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Send the Q3 plan/ }));
    fireEvent.click(await screen.findByRole('button', { name: 'Open in Mail' }));
    expect(onOpenInMail).toHaveBeenCalledWith('email_src_1');
  });

  it('shows the detected task relationship inside the preview', async () => {
    renderPage();
    fireEvent.click(await screen.findByRole('button', { name: /View source email for Send the Q3 plan/ }));
    expect(await screen.findByText('Detected task')).toBeInTheDocument();
    expect(screen.getAllByText('Send the Q3 plan').length).toBeGreaterThanOrEqual(1);
  });
});
