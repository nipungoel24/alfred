import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TasksPage } from './TasksPage';
import type { Task } from '../../api/emails';

vi.mock('../../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../api/emails')>();
  return {
    ...original,
    tasks: vi.fn(),
    toggleTask: vi.fn(),
    dismissTask: vi.fn(),
    patchTaskPriority: vi.fn(),
    emailDetails: vi.fn(),
  };
});

import { tasks as fetchTasks } from '../../api/emails';

const mockedTasks = vi.mocked(fetchTasks);

function task(over: Partial<Task> = {}): Task {
  return {
    id: 'task-1',
    title: 'Submit the signed NDA',
    description: null,
    due_at: null,
    owner: null,
    priority: 'medium',
    status: 'pending',
    source_email_id: 'email-1',
    ...over,
  } as Task;
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TasksPage />
    </QueryClientProvider>,
  );
}

/** The list is virtualised, so wait for the rows to mount before asserting. */
async function rows(): Promise<Element[]> {
  await waitFor(() => {
    expect(document.querySelectorAll('.task-row').length).toBeGreaterThan(0);
  });
  return Array.from(document.querySelectorAll('.task-row'));
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe('TasksPage action column', () => {
  it('renders both actions in one group for every row', async () => {
    mockedTasks.mockResolvedValue([
      task({ id: 'a', title: 'Has a source email', source_email_id: 'email-1' }),
      task({ id: 'b', title: 'Has no source email', source_email_id: null }),
    ]);
    renderPage();

    const found = await rows();
    expect(found).toHaveLength(2);
    for (const row of found) {
      const actions = row.querySelector('.task-actions');
      expect(actions).not.toBeNull();
      // Both controls exist in both rows, so the column cannot resize.
      expect(actions!.querySelectorAll('.task-action')).toHaveLength(2);
      expect(actions!.querySelector('.task-action-view')).not.toBeNull();
      expect(actions!.querySelector('.task-action-dismiss')).not.toBeNull();
    }
  });

  it('keeps the view action disabled but present when there is no source email', async () => {
    mockedTasks.mockResolvedValue([task({ id: 'b', source_email_id: null })]);
    renderPage();
    await rows();

    const view = await screen.findByRole('button', { name: /No source email/i });
    expect(view).toBeDisabled();
    expect(screen.getByRole('button', { name: /Not a task: dismiss/i })).toBeEnabled();
  });

  it('gives the view action an accessible name and keeps the label with its icon', async () => {
    mockedTasks.mockResolvedValue([task({ title: 'Send the wire' })]);
    renderPage();
    await rows();

    const view = await screen.findByRole('button', {
      name: 'View source email for Send the wire',
    });
    const label = within(view).getByText('View email');
    // Icon and text are one control, not two floating pieces.
    expect(label.closest('button')).toBe(view);
    expect(view.querySelector('svg')).not.toBeNull();
  });

  it('does not reinterpret due_at or title values', async () => {
    // These are exactly the malformed values found in the real database. The
    // row must render what it was given; correcting them here would only hide
    // the extraction defect rather than fix it.
    mockedTasks.mockResolvedValue([
      task({ id: 'legacy', title: 'due_at: soon', due_at: 'due_at: soon' }),
    ]);
    renderPage();
    const [row] = await rows();

    expect(within(row as HTMLElement).getByText('due_at: soon', { selector: '.task-title' }))
      .toBeInTheDocument();
    expect(row.querySelector('.task-due')!.textContent).toBe('Due: due_at: soon');
  });

  it('renders a normalised ISO due date verbatim', async () => {
    mockedTasks.mockResolvedValue([
      task({ id: 'iso', due_at: '2026-09-12T00:00:00+00:00' }),
    ]);
    renderPage();
    const [row] = await rows();

    expect(row.querySelector('.task-due')!.textContent).toBe('Due: 2026-09-12T00:00:00+00:00');
  });

  it('omits the due element entirely when there is no due date', async () => {
    mockedTasks.mockResolvedValue([task({ id: 'none', due_at: null })]);
    renderPage();
    const [row] = await rows();

    expect(row.querySelector('.task-due')).toBeNull();
  });

  it('stays reachable by keyboard: every action is a real button', async () => {
    mockedTasks.mockResolvedValue([task({ id: 'k' })]);
    renderPage();
    const [row] = await rows();

    for (const el of Array.from(row.querySelectorAll('.task-actions button'))) {
      expect(el.tagName).toBe('BUTTON');
      expect(el.getAttribute('type')).toBe('button');
      // A disabled control must not be a tab stop.
      if ((el as HTMLButtonElement).disabled) {
        expect(el).toBeDisabled();
      }
    }
  });
});
