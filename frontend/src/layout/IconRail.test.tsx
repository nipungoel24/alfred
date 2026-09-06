import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { IconRail } from './IconRail';

describe('IconRail', () => {
  it('renders all navigation sections with accessible labels', () => {
    render(<IconRail page="overview" onNavigate={() => {}} aiReady gmailConnected />);

    const nav = screen.getByRole('navigation', { name: 'Alfred sections' });
    expect(nav).toBeInTheDocument();

    for (const label of ['Overview', 'Mail', 'Tasks', 'Deadlines']) {
      expect(screen.getByRole('button', { name: label })).toBeInTheDocument();
    }
    expect(screen.getByRole('button', { name: 'Accounts' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Settings' })).toBeInTheDocument();
  });

  it('marks the active page with aria-current', () => {
    render(<IconRail page="mail" onNavigate={() => {}} aiReady gmailConnected />);
    expect(screen.getByRole('button', { name: 'Mail' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('button', { name: 'Overview' })).not.toHaveAttribute('aria-current');
  });

  it('navigates on item click', () => {
    const onNavigate = vi.fn();
    render(<IconRail page="overview" onNavigate={onNavigate} aiReady gmailConnected />);

    fireEvent.click(screen.getByRole('button', { name: 'Tasks' }));
    expect(onNavigate).toHaveBeenCalledWith('tasks');
  });

  it('exposes AI and Gmail service status with accessible labels', () => {
    render(<IconRail page="overview" onNavigate={() => {}} aiReady gmailConnected />);

    expect(screen.getByLabelText('Alfred AI ready')).toBeInTheDocument();
    expect(screen.getByLabelText('Gmail connected')).toBeInTheDocument();
  });

  it('reflects degraded service status', () => {
    render(<IconRail page="overview" onNavigate={() => {}} aiReady={false} gmailConnected={false} />);

    expect(screen.getByLabelText('Alfred AI offline')).toBeInTheDocument();
    expect(screen.getByLabelText('Gmail disconnected')).toBeInTheDocument();
  });
});
