import { useState } from 'react';
import { LayoutDashboard, Mail, CheckSquare, Clock, UserCircle, Settings } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type AppPage = 'overview' | 'mail' | 'tasks' | 'deadlines' | 'accounts' | 'settings';

// Approved Alfred brand asset (symbol-only mark). If the generated asset
// has not been copied into frontend/public yet, the rail falls back to a
// minimal violet block until the file exists.
const BRAND_ICON_URL = '/alfred-icon.png';

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
  const [brandFailed, setBrandFailed] = useState(false);

  return (
    <aside className="icon-rail" aria-label="Primary navigation">
      <div className="rail-brand" aria-hidden="true">
        {!brandFailed && (
          <img
            src={BRAND_ICON_URL}
            alt=""
            className="rail-brand-icon"
            onError={() => setBrandFailed(true)}
          />
        )}
        {brandFailed && <span className="rail-brand-fallback">A</span>}
      </div>
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
