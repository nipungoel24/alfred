import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { IconRail, type IconRailProps } from './IconRail';

function renderRail(props: Partial<IconRailProps> = {}) {
  const onNavigate = vi.fn();
  const onNavigateMail = vi.fn();
  render(
    <IconRail
      page="mail"
      onNavigate={onNavigate}
      aiReady
      gmailConnected
      {...props}
      onNavigateMail={props.onNavigateMail ?? onNavigateMail}
    />,
  );
  return { onNavigate, onNavigateMail: props.onNavigateMail ?? onNavigateMail };
}

describe('IconRail (primary navigation)', () => {
  it('exposes every product capability exactly once', () => {
    renderRail();
    const nav = screen.getByRole('navigation', { name: /sections/i });
    for (const label of [
      'Inbox',
      'All Mail',
      'Important',
      'Needs Reply',
      'Later',
      'Overview',
      'Tasks',
      'Deadlines',
      'Accounts',
      'Settings',
    ]) {
      expect(within(nav).getByRole('button', { name: new RegExp(`^${label}`) })).toBeInTheDocument();
    }
  });

  it('groups capabilities under labelled sections', () => {
    renderRail();
    expect(screen.getByRole('heading', { name: 'Mail' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Intelligence' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'System' })).toBeInTheDocument();
  });

  it('marks the active item with aria-current', () => {
    renderRail({ page: 'tasks' });
    expect(screen.getByRole('button', { name: /^Tasks/ })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('button', { name: /^Deadlines/ })).not.toHaveAttribute('aria-current');
  });

  it('is a single tab stop with roving tabindex', () => {
    renderRail({ page: 'mail' });
    const buttons = screen.getAllByRole('button');
    const tabbable = buttons.filter((b) => b.getAttribute('tabindex') === '0');
    expect(tabbable).toHaveLength(1);
  });

  it('stays keyboard-reachable when nothing is active', () => {
    // A search can leave no nav item matching. The rail must still have an
    // entry point, or it becomes unreachable with Tab.
    renderRail({ page: 'mail' });
    const tabbable = screen
      .getAllByRole('button')
      .filter((b) => b.getAttribute('tabindex') === '0');
    expect(tabbable).toHaveLength(1);
  });

  it('navigates to a page destination on click', () => {
    const { onNavigate } = renderRail();
    fireEvent.click(screen.getByRole('button', { name: /^Deadlines/ }));
    expect(onNavigate).toHaveBeenCalledWith('deadlines');
  });

  it('drives the mail scope and filter rather than a page change', () => {
    const { onNavigate, onNavigateMail } = renderRail();
    fireEvent.click(screen.getByRole('button', { name: /^All Mail/ }));
    expect(onNavigateMail).toHaveBeenCalledWith('all', 'all');
    expect(onNavigate).not.toHaveBeenCalled();
  });

  it('marks the active mail scope and filter', () => {
    renderRail({ activeMailView: 'inbox:important' });
    expect(screen.getByRole('button', { name: /^Important/ })).toHaveAttribute('aria-current', 'page');
  });

  it('never lights two items at once', () => {
    // Regression: a mail view left over from the mail page used to keep a mail
    // row active while a different page was on screen, so the rail showed two
    // active items and the real page row stayed dark.
    for (const page of ['overview', 'tasks', 'deadlines', 'accounts', 'settings'] as const) {
      const { unmount } = render(
        <IconRail
          page={page}
          onNavigate={vi.fn()}
          onNavigateMail={vi.fn()}
          aiReady
          gmailConnected
          activeMailView="inbox:later"
        />,
      );
      const current = screen.getAllByRole('button').filter((b) => b.getAttribute('aria-current') === 'page');
      expect(current).toHaveLength(1);
      expect(current[0]).toHaveTextContent(
        { overview: 'Overview', tasks: 'Tasks', deadlines: 'Deadlines', accounts: 'Accounts', settings: 'Settings' }[page],
      );
      unmount();
    }
  });

  it('keeps a mail row active on the mail page', () => {
    renderRail({ page: 'mail', activeMailView: 'inbox:later' });
    const current = screen.getAllByRole('button').filter((b) => b.getAttribute('aria-current') === 'page');
    expect(current).toHaveLength(1);
    expect(current[0]).toHaveTextContent('Later');
  });

  it('shows real counts from the API', () => {
    renderRail({ counts: { inbox: 42, allMail: 1284 } });
    expect(screen.getByRole('button', { name: /^Inbox/ })).toHaveTextContent('42');
    expect(screen.getByRole('button', { name: /^All Mail/ })).toHaveTextContent('1284');
  });

  it('shows a zero count rather than hiding it', () => {
    renderRail({ counts: { inbox: 0, allMail: 0 } });
    expect(screen.getByRole('button', { name: /^Inbox/ })).toHaveTextContent('0');
  });

  it('omits a count the API does not provide', () => {
    renderRail({ counts: { inbox: 7 } });
    // No invented number for All Mail.
    expect(screen.getByRole('button', { name: /^All Mail/ })).not.toHaveTextContent(/\d/);
  });

  it('moves focus and activates the next item with ArrowDown', () => {
    const { onNavigateMail } = renderRail({ page: 'overview' });
    const nav = screen.getByRole('navigation', { name: /sections/i });

    screen.getByRole('button', { name: /^Inbox/ }).focus();
    fireEvent.keyDown(nav, { key: 'ArrowDown' });

    // Focus moved, and the destination was activated.
    expect(document.activeElement).toBe(screen.getByRole('button', { name: /^All Mail/ }));
    expect(onNavigateMail).toHaveBeenCalledWith('all', 'all');
  });

  it('wraps backwards with ArrowUp', () => {
    const { onNavigate } = renderRail({ page: 'overview' });
    const nav = screen.getByRole('navigation', { name: /sections/i });

    screen.getByRole('button', { name: /^Inbox/ }).focus();
    fireEvent.keyDown(nav, { key: 'ArrowUp' });

    expect(onNavigate).toHaveBeenCalledWith('settings');
  });

  it('jumps to the last item with End and the first with Home', () => {
    renderRail();
    const nav = screen.getByRole('navigation', { name: /sections/i });
    screen.getByRole('button', { name: /^Inbox/ }).focus();

    fireEvent.keyDown(nav, { key: 'End' });
    expect(document.activeElement).toBe(screen.getByRole('button', { name: /^Settings/ }));

    fireEvent.keyDown(nav, { key: 'Home' });
    expect(document.activeElement).toBe(screen.getByRole('button', { name: /^Inbox/ }));
  });

  it('reports service status as text, not a bare coloured dot', () => {
    renderRail({ aiReady: true, gmailConnected: true });
    expect(screen.getByText('Local AI ready')).toBeInTheDocument();
    expect(screen.getByText('Gmail connected')).toBeInTheDocument();
  });

  it('reflects a degraded service honestly', () => {
    renderRail({ aiReady: false, gmailConnected: false });
    expect(screen.getByText('Local AI offline')).toBeInTheDocument();
    expect(screen.getByText('Gmail not connected')).toBeInTheDocument();
  });

  it('shows the connected account when there is one', () => {
    renderRail({ accountEmail: 'nora@example.com' });
    expect(screen.getByText('nora@example.com')).toBeInTheDocument();
  });

  it('omits the account row when nothing is connected', () => {
    renderRail({ gmailConnected: false });
    expect(screen.queryByText(/@/)).not.toBeInTheDocument();
  });

  it('is a complementary landmark', () => {
    renderRail();
    expect(screen.getByRole('complementary', { name: /primary/i })).toBeInTheDocument();
  });
});
