import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { WorkspaceHeader } from './WorkspaceHeader';

function renderHeader() {
  return render(
    <WorkspaceHeader
      title="Mail"
      subtitle="Gmail inbox"
      searchValue=""
      onSearchChange={() => {}}
      aiReady
      accountInitial="N"
    />
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
    render(
      <WorkspaceHeader
        title="Mail"
        searchValue=""
        onSearchChange={onSearchChange}
        aiReady={false}
      />
    );
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'Adobe' } });
    expect(onSearchChange).toHaveBeenCalledWith('Adobe');
  });
});
