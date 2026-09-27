import { useCallback, useRef } from 'react';
import {
  Inbox,
  Mail,
  Star,
  Reply,
  LayoutDashboard,
  CheckSquare,
  CalendarClock,
  UserCircle,
  Settings as SettingsIcon,
  Archive,
  Cpu,
  type LucideIcon,
} from 'lucide-react';
import type { MailFilter, MailScope } from '../api/emails';

export type AppPage =
  | 'overview'
  | 'mail'
  | 'tasks'
  | 'deadlines'
  | 'accounts'
  | 'settings';

export type NavCounts = {
  inbox?: number;
  allMail?: number;
};

export type IconRailProps = {
  page: AppPage;
  onNavigate: (page: AppPage) => void;
  aiReady: boolean;
  gmailConnected: boolean;
  accountEmail?: string;
  /** Only counts the API actually returns. Undefined means "not available". */
  counts?: NavCounts;
  /** `${scope}:${filter}` of the active mail view, so the rail can mark it. */
  activeMailView?: string;
  onNavigateMail?: (scope: MailScope, filter: MailFilter) => void;
};

type NavItem = {
  key: string;
  label: string;
  icon: LucideIcon;
  /** A page destination, or a mail scope/filter pair. */
  page?: AppPage;
  mail?: { scope: MailScope; filter: MailFilter };
  count?: number;
};

type NavSection = { title: string; items: NavItem[] };

/**
 * Primary navigation.
 *
 * Every capability the product already has appears here exactly once. The
 * audit found six of the ten were previously reachable only from inside the
 * mail pane, which meant they were invisible from every other page; the
 * rail is now the single surface that owns them.
 *
 * The whole rail is one tab stop with arrow-key navigation and a roving
 * tabindex, so it is reachable without tabbing through six stops.
 */
export function IconRail({
  page,
  onNavigate,
  aiReady,
  gmailConnected,
  accountEmail,
  counts,
  activeMailView,
  onNavigateMail,
}: IconRailProps) {
  const itemRefs = useRef(new Map<string, HTMLButtonElement>());

  const sections: NavSection[] = [
    {
      title: 'Mail',
      items: [
        { key: 'inbox', label: 'Inbox', icon: Inbox, mail: { scope: 'inbox', filter: 'all' }, count: counts?.inbox },
        { key: 'all', label: 'All Mail', icon: Mail, mail: { scope: 'all', filter: 'all' }, count: counts?.allMail },
        { key: 'important', label: 'Important', icon: Star, mail: { scope: 'inbox', filter: 'important' } },
        { key: 'reply', label: 'Needs Reply', icon: Reply, mail: { scope: 'inbox', filter: 'reply' } },
        { key: 'later', label: 'Later', icon: Archive, mail: { scope: 'inbox', filter: 'later' } },
      ],
    },
    {
      title: 'Intelligence',
      items: [
        { key: 'overview', label: 'Overview', icon: LayoutDashboard, page: 'overview' },
        { key: 'tasks', label: 'Tasks', icon: CheckSquare, page: 'tasks' },
        { key: 'deadlines', label: 'Deadlines', icon: CalendarClock, page: 'deadlines' },
      ],
    },
    {
      title: 'System',
      items: [
        { key: 'accounts', label: 'Accounts', icon: UserCircle, page: 'accounts' },
        { key: 'settings', label: 'Settings', icon: SettingsIcon, page: 'settings' },
      ],
    },
  ];

  const flat = sections.flatMap((s) => s.items);

  // Exactly one item is active, and it is the one that matches where the user
  // actually is. `activeMailView` is always defined (App builds it from the
  // current scope/filter even off the mail page), so a mail item must also be
  // gated on being on the mail page. Without that gate a stale view such as
  // "inbox:later" kept a mail row lit while Overview was on screen, and the
  // Overview row could never light up at all.
  const isActive = (item: NavItem): boolean => {
    if (item.page) return page === item.page;
    if (!item.mail || !activeMailView) return false;
    return page === 'mail' && activeMailView === `${item.mail.scope}:${item.mail.filter}`;
  };

  // Exactly one item is always tabbable. If nothing is active (for example a
  // search is narrowing the list), the first item becomes the entry point —
  // otherwise the whole sidebar would be unreachable by keyboard.
  const activeKey = flat.find(isActive)?.key ?? flat[0]?.key;

  const activate = useCallback(
    (item: NavItem) => {
      if (item.page) onNavigate(item.page);
      else if (item.mail) onNavigateMail?.(item.mail.scope, item.mail.filter);
    },
    [onNavigate, onNavigateMail],
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLElement>) => {
      const keys = ['ArrowDown', 'ArrowUp', 'Home', 'End'];
      if (!keys.includes(event.key)) return;
      event.preventDefault();

      const currentIndex = flat.findIndex(
        (i) => itemRefs.current.get(i.key) === document.activeElement,
      );
      let nextIndex: number;
      if (event.key === 'Home') nextIndex = 0;
      else if (event.key === 'End') nextIndex = flat.length - 1;
      else if (event.key === 'ArrowDown') nextIndex = (currentIndex + 1 + flat.length) % flat.length;
      else nextIndex = (currentIndex - 1 + flat.length) % flat.length;

      const next = flat[nextIndex];
      if (!next) return;
      const node = itemRefs.current.get(next.key);
      if (node) {
        node.focus();
        activate(next);
      }
    },
    [flat, activate],
  );

  return (
    <aside className="icon-rail" aria-label="Primary">
      <div className="rail-brand">
        <img
          className="rail-brand-icon"
          src="/alfred-icon.png"
          alt=""
          onError={(e) => {
            e.currentTarget.style.display = 'none';
          }}
        />
        <span className="rail-brand-name">Alfred</span>
      </div>

      <nav className="rail-nav" aria-label="Sections" onKeyDown={handleKeyDown}>
        {sections.map((section) => (
          <div className="rail-section" key={section.title}>
            <h2 className="rail-section-title">{section.title}</h2>
            <ul className="rail-section-list">
              {section.items.map((item) => {
                const active = isActive(item);
                const Icon = item.icon;
                return (
                  <li key={item.key}>
                    <button
                      type="button"
                      ref={(node) => {
                        if (node) itemRefs.current.set(item.key, node);
                        else itemRefs.current.delete(item.key);
                      }}
                      className="rail-item"
                      data-active={active || undefined}
                      aria-current={active ? 'page' : undefined}
                      tabIndex={item.key === activeKey ? 0 : -1}
                      onClick={() => activate(item)}
                    >
                      <Icon size={16} strokeWidth={1.75} aria-hidden="true" />
                      <span className="rail-item-label">{item.label}</span>
                      {typeof item.count === 'number' && (
                        <span className="rail-item-count">{item.count}</span>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="rail-footer">
        {accountEmail && (
          <div className="rail-account" title={accountEmail}>
            <span className="rail-account-avatar" aria-hidden="true">
              {accountEmail[0]?.toUpperCase()}
            </span>
            <span className="rail-account-email">{accountEmail}</span>
          </div>
        )}

        {/* Status is icon + label, never a bare coloured dot. Teal sits close
            to success-green in hue, so colour alone cannot carry this. */}
        <ul className="rail-status" aria-label="Service status">
          <li className="rail-status-item" data-ok={aiReady}>
            <Cpu size={14} strokeWidth={1.75} aria-hidden="true" />
            <span className="rail-status-label">
              {aiReady ? 'Local AI ready' : 'Local AI offline'}
            </span>
          </li>
          <li className="rail-status-item" data-ok={gmailConnected}>
            <Mail size={14} strokeWidth={1.75} aria-hidden="true" />
            <span className="rail-status-label">
              {gmailConnected ? 'Gmail connected' : 'Gmail not connected'}
            </span>
          </li>
        </ul>
      </div>
    </aside>
  );
}
