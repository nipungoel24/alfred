import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LayoutDashboard, Inbox, Star, MessageSquareReply, CheckSquare,
  Clock, UserCircle, Settings, Search, Cpu, Archive
} from 'lucide-react';
import { OverviewPage } from './features/overview/OverviewPage';
import { InboxPage } from './features/inbox/InboxPage';
import { TasksPage } from './features/tasks/TasksPage';
import { DeadlinesPage } from './features/deadlines/DeadlinesPage';
import { AccountsPage } from './features/accounts/AccountsPage';
import { SettingsPage } from './features/settings/SettingsPage';
import { AnalysisProgress } from './components/ui/AnalysisProgress';
import { accounts as fetchAccounts, emails as fetchEmails, tasks as fetchTasks, briefing as fetchBriefing, health as fetchHealth } from './api/emails';
import './styles.css';

type Page = 'overview' | 'inbox' | 'important' | 'reply' | 'later' | 'tasks' | 'deadlines' | 'accounts' | 'settings';

const PAGE_TITLES: Record<Page, string> = {
  overview: 'Overview',
  inbox: 'Inbox',
  important: 'Important',
  reply: 'Needs Reply',
  later: 'Later',
  tasks: 'Tasks',
  deadlines: 'Deadlines',
  accounts: 'Accounts',
  settings: 'Settings',
};

export default function App() {
  const [page, setPage] = useState<Page>('overview');
  const [globalSearch, setGlobalSearch] = useState('');

  const { data: accountsList = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  const { data: emailsList = [] } = useQuery({ queryKey: ['emails', {}], queryFn: () => fetchEmails() });
  const { data: tasksList = [] } = useQuery({ queryKey: ['tasks'], queryFn: fetchTasks });
  const { data: brief } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: fetchHealth, refetchInterval: 30_000, retry: 0 });

  const importantCount = emailsList.filter(e => e.analysis?.priority === 'high' || e.analysis?.priority === 'urgent').length;
  const replyCount = emailsList.filter(e => e.analysis?.needs_reply).length;
  const pendingTasks = tasksList.filter(t => t.status === 'pending').length;
  const deadlineCount = brief?.deadline_count ?? 0;
  const gmailConnected = accountsList.some(a => a.connection_status === 'connected');
  const ollamaReady = health?.ai === 'ready';

  // Ctrl+K global search
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      document.getElementById('global-search')?.focus();
    }
    if (e.key === 'Escape') {
      (document.activeElement as HTMLElement)?.blur();
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const nav = (p: Page) => setPage(p);

  return (
    <div className="app-shell">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>ALFRED</h1>
          <span>Smart Inbox</span>
        </div>

        <nav className="sidebar-nav">
          <NavItem icon={<LayoutDashboard />} label="Overview" active={page === 'overview'} onClick={() => nav('overview')} />
        </nav>

        <div className="sidebar-section-label">Mail</div>
        <nav className="sidebar-nav">
          <NavItem icon={<Inbox />} label="Inbox" badge={emailsList.length} active={page === 'inbox'} onClick={() => nav('inbox')} />
          <NavItem icon={<Star />} label="Important" badge={importantCount || undefined} active={page === 'important'} onClick={() => nav('important')} />
          <NavItem icon={<MessageSquareReply />} label="Needs Reply" badge={replyCount || undefined} active={page === 'reply'} onClick={() => nav('reply')} />
          <NavItem icon={<Archive />} label="Later" active={page === 'later'} onClick={() => nav('later')} />
        </nav>

        <div className="sidebar-section-label">Organize</div>
        <nav className="sidebar-nav">
          <NavItem icon={<CheckSquare />} label="Tasks" badge={pendingTasks || undefined} active={page === 'tasks'} onClick={() => nav('tasks')} />
          <NavItem icon={<Clock />} label="Deadlines" badge={deadlineCount || undefined} active={page === 'deadlines'} onClick={() => nav('deadlines')} />
        </nav>

        <div className="sidebar-section-label">System</div>
        <nav className="sidebar-nav">
          <NavItem icon={<UserCircle />} label="Accounts" active={page === 'accounts'} onClick={() => nav('accounts')} />
          <NavItem icon={<Settings />} label="Settings" active={page === 'settings'} onClick={() => nav('settings')} />
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className={`status-dot ${ollamaReady ? 'online' : 'offline'}`} />
            <span>Local AI · qwen3:4b</span>
          </div>
          <div className="sidebar-status">
            <span className={`status-dot ${gmailConnected ? 'online' : 'offline'}`} />
            <span>Gmail {gmailConnected ? 'connected' : 'disconnected'}</span>
          </div>
        </div>
      </aside>

      {/* ── Top Bar ── */}
      <header className="topbar">
        <div className="topbar-page-title">{PAGE_TITLES[page]}</div>

        <div className="search-container">
          <div className="search-box">
            <Search />
            <input
              id="global-search"
              type="text"
              placeholder="Search mail, people, tasks..."
              value={globalSearch}
              onChange={e => setGlobalSearch(e.target.value)}
            />
            <span className="search-shortcut">Ctrl K</span>
          </div>
        </div>

        <div className="topbar-actions">
          <div className="topbar-status">
            <Cpu size={12} />
            <span>{ollamaReady ? 'AI Ready' : 'AI unavailable'}</span>
          </div>
        </div>
      </header>

      {/* ── Main Workspace ── */}
      <main className="workspace">
        {page === 'overview'  && <OverviewPage onNavigate={nav} />}
        {page === 'inbox'     && <InboxPage searchQuery={globalSearch} />}
        {page === 'important' && <InboxPage priorityFilter="high" searchQuery={globalSearch} />}
        {page === 'reply'     && <InboxPage needsReplyFilter={true} searchQuery={globalSearch} />}
        {page === 'later'     && <InboxPage priorityFilter="low" searchQuery={globalSearch} />}
        {page === 'tasks'     && <TasksPage />}
        {page === 'deadlines' && <DeadlinesPage />}
        {page === 'accounts'  && <AccountsPage />}
        {page === 'settings'  && <SettingsPage />}
        <AnalysisProgress />
      </main>
    </div>
  );
}

/* ── NavItem ── */
function NavItem({ icon, label, badge, active, onClick }: {
  icon: React.ReactNode;
  label: string;
  badge?: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button className={`nav-item ${active ? 'active' : ''}`} onClick={onClick} aria-label={label}>
      {icon}
      <span>{label}</span>
      {badge !== undefined && badge > 0 && <span className="nav-badge">{badge}</span>}
    </button>
  );
}
