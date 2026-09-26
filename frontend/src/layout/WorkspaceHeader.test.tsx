import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { WorkspaceHeader } from './WorkspaceHeader';

function renderHeader(props: Partial<React.ComponentProps<typeof WorkspaceHeader>> = {}) {
  return render(
    <WorkspaceHeader
      title="Mail"
      subtitle="Gmail inbox"
      searchValue=""
      onSearchChange={() => {}}
      aiReady
      {...props}
    />,
  );
}

describe('WorkspaceHeader', () => {
  it('focuses search on Ctrl+K', () => {
    renderHeader();
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    expect(document.activeElement).toBe(screen.getByRole('searchbox'));
  });

  it('focuses search on Cmd+K', () => {
    renderHeader();
    fireEvent.keyDown(document, { key: 'k', metaKey: true });
    expect(document.activeElement).toBe(screen.getByRole('searchbox'));
  });

  it('blurs search on Escape while focused', () => {
    renderHeader();
    const input = screen.getByRole('searchbox');
    input.focus();
    expect(document.activeElement).toBe(input);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(document.activeElement).not.toBe(input);
  });

  it('propagates typed search value', () => {
    const onSearchChange = vi.fn();
    renderHeader({ onSearchChange });
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'Adobe' } });
    expect(onSearchChange).toHaveBeenCalledWith('Adobe');
  });

  it('gives the page title an h1', () => {
    renderHeader();
    expect(screen.getByRole('heading', { level: 1, name: 'Mail' })).toBeInTheDocument();
  });

  it('labels the search input for screen readers', () => {
    renderHeader();
    expect(screen.getByRole('searchbox', { name: /search all mail/i })).toBeInTheDocument();
  });

  it('advertises the keyboard shortcut', () => {
    renderHeader();
    expect(screen.getByText(/Ctrl K|Cmd K/)).toBeInTheDocument();
  });

  it('shows a clear affordance only when there is a query', () => {
    const onSearchChange = vi.fn();
    const { rerender } = renderHeader({ onSearchChange, searchValue: '' });
    expect(screen.queryByRole('button', { name: /clear search/i })).not.toBeInTheDocument();

    rerender(
      <WorkspaceHeader
        title="Mail"
        searchValue="invoice"
        onSearchChange={onSearchChange}
        aiReady
      />,
    );
    expect(screen.getByRole('button', { name: /clear search/i })).toBeInTheDocument();
  });

  it('clears the query from the clear button', () => {
    const onSearchChange = vi.fn();
    renderHeader({ onSearchChange, searchValue: 'invoice' });
    fireEvent.click(screen.getByRole('button', { name: /clear search/i }));
    expect(onSearchChange).toHaveBeenCalledWith('');
  });

  it('names the connected account for screen readers', () => {
    renderHeader({ accountEmail: 'nora@example.com' });
    expect(screen.getByText(/Connected as nora@example\.com/)).toBeInTheDocument();
  });

  it('reports AI state as text, not a bare coloured dot', () => {
    const { rerender } = renderHeader({ aiReady: true, aiState: 'ready' });
    expect(screen.getByText('AI ready')).toBeInTheDocument();

    rerender(
      <WorkspaceHeader
        title="Mail"
        searchValue=""
        onSearchChange={() => {}}
        aiReady={false}
        aiState="ollama_not_running"
      />,
    );
    expect(screen.getByText('AI offline')).toBeInTheDocument();
  });

  it('disables sync while a sync is running so clicks cannot stack', () => {
    const onSync = vi.fn();
    const { rerender } = renderHeader({ onSync, syncing: false });
    const button = screen.getByRole('button', { name: /sync/i });
    expect(button).toBeEnabled();

    rerender(
      <WorkspaceHeader
        title="Mail"
        searchValue=""
        onSearchChange={() => {}}
        aiReady
        onSync={onSync}
        syncing
      />,
    );
    expect(screen.getByRole('button', { name: /syncing/i })).toBeDisabled();
  });

  it('hides sync entirely when no handler is supplied', () => {
    renderHeader();
    expect(screen.queryByRole('button', { name: /sync/i })).not.toBeInTheDocument();
  });
});
