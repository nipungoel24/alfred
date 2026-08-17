import { LayoutDashboard, Mail, CheckSquare, Clock, UserCircle, Settings } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type AppPage = 'overview' | 'mail' | 'tasks' | 'deadlines' | 'accounts' | 'settings';

interface RailItem {
  page: AppPage;
  label: string;
  icon: LucideIcon;
}

const PRIMARY: RailItem[] = [
  { page: 'overview', label: 'Overview', icon: LayoutDashboard },
  { page: 'mail', label: 'Mail', icon: Mail },
  { page: 'tasks', label: 'Tasks', icon: CheckSquare },
  { page: 'deadlines', label: 'Deadlines', icon: Clock },
];

const SECONDARY: RailItem[] = [
  { page: 'accounts', label: 'Accounts', icon: UserCircle },
  { page: 'settings', label: 'Settings', icon: Settings },
];

interface IconRailProps {
  page: AppPage;
  onNavigate: (page: AppPage) => void;
  aiReady: boolean;
  gmailConnected: boolean;
}

export function IconRail({ page, onNavigate, aiReady, gmailConnected }: IconRailProps) {
  return (
    <aside className="icon-rail" aria-label="Primary navigation">
      <div className="rail-brand" aria-hidden="true">A</div>
      <nav className="rail-nav" aria-label="Alfred sections">
        {PRIMARY.map(item => (
          <RailButton key={item.page} item={item} active={page === item.page} onClick={() => onNavigate(item.page)} />
        ))}
      </nav>
      <div className="rail-spacer" />
      <nav className="rail-nav" aria-label="System sections">
        {SECONDARY.map(item => (
          <RailButton key={item.page} item={item} active={page === item.page} onClick={() => onNavigate(item.page)} />
        ))}
        <span
          className="rail-item"
          data-label={aiReady ? 'Local AI ready' : 'Local AI unavailable'}
          title={aiReady ? 'Local AI ready' : 'Local AI unavailable'}
          aria-hidden="true"
        >
          <span className={`status-dot ${aiReady ? 'online' : 'offline'}`} />
        </span>
        <span
          className="rail-item"
          data-label={gmailConnected ? 'Gmail connected' : 'Gmail disconnected'}
          title={gmailConnected ? 'Gmail connected' : 'Gmail disconnected'}
          aria-hidden="true"
        >
          <span className={`status-dot ${gmailConnected ? 'online' : 'offline'}`} />
        </span>
      </nav>
    </aside>
  );
}

function RailButton({ item, active, onClick }: { item: RailItem; active: boolean; onClick: () => void }) {
  const Icon = item.icon;
  return (
    <button
      type="button"
      className={`rail-item ${active ? 'active' : ''}`}
      data-label={item.label}
      aria-label={item.label}
      aria-current={active ? 'page' : undefined}
      onClick={onClick}
    >
      <Icon size={18} strokeWidth={2} aria-hidden="true" />
    </button>
  );
}
