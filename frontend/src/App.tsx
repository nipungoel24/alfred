import { useState } from 'react';
import { OverviewPage } from './features/overview/OverviewPage';
import { InboxPage } from './features/inbox/InboxPage';
import { TasksPage } from './features/tasks/TasksPage';
import { AccountsPage } from './features/accounts/AccountsPage';
import { AnalysisProgress } from './components/ui/AnalysisProgress';
import './styles.css';

const nav = ['Overview', 'Inbox', 'Important', 'Needs Reply', 'Tasks', 'Accounts'];

export default function App() {
  const [page, setPage] = useState('Overview');

  return (
    <div className="layout">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 className="text-xl font-bold tracking-wider text-white">ALFRED</h2>
          <div className="text-xs text-muted uppercase tracking-widest mt-1">Local Executive</div>
        </div>
        <nav className="sidebar-nav">
          {nav.map(item => (
            <button
              key={item}
              className={`nav-item ${page === item ? 'active' : ''}`}
              onClick={() => setPage(item)}
            >
              {item}
            </button>
          ))}
        </nav>
      </div>

      <div className="main">
        {page === 'Overview' && <OverviewPage />}
        {page === 'Inbox' && <InboxPage />}
        {page === 'Important' && <InboxPage priorityFilter="high" />}
        {page === 'Needs Reply' && <InboxPage needsReplyFilter={true} />}
        {page === 'Tasks' && <TasksPage />}
        {page === 'Accounts' && <AccountsPage />}
        <AnalysisProgress />
      </div>
    </div>
  );
}
