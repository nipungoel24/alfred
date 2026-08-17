import { useCallback, useMemo, useState } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { IconRail } from './layout/IconRail';
import type { AppPage } from './layout/IconRail';
import { WorkspaceHeader } from './layout/WorkspaceHeader';
import { MailWorkspace } from './mail/MailWorkspace';
import { OverviewPage } from './features/overview/OverviewPage';
import { TasksPage } from './features/tasks/TasksPage';
import { DeadlinesPage } from './features/deadlines/DeadlinesPage';
import { AccountsPage } from './features/accounts/AccountsPage';
import { SettingsPage } from './features/settings/SettingsPage';
import { AnalysisProgress } from './components/ui/AnalysisProgress';
import { accounts as fetchAccounts, health as fetchHealth, syncAccount } from './api/emails';
import './styles.css';

const PAGE_META: Record<AppPage, { title: string; subtitle?: string }> = {
  overview: { title: 'Overview', subtitle: 'What needs your attention' },
  mail: { title: 'Mail', subtitle: 'Gmail inbox' },
  tasks: { title: 'Tasks', subtitle: 'Derived from your mail' },
  deadlines: { title: 'Deadlines', subtitle: 'Time-bound commitments' },
  accounts: { title: 'Accounts', subtitle: 'Connected providers' },
  settings: { title: 'Settings', subtitle: 'Preferences' },
};

export default function App() {
  const [page, setPage] = useState<AppPage>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  const { data: accountsList = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 0,
  });

  const gmailAccount = accountsList.find(a => a.provider === 'gmail' && a.connection_status === 'connected');
  const aiReady = health?.ai === 'ready';

  const syncMutation = useMutation({
    mutationFn: (id: string) => syncAccount(id, false),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['emails'] });
      void queryClient.invalidateQueries({ queryKey: ['emailCounts'] });
      void queryClient.invalidateQueries({ queryKey: ['accounts'] });
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
      void queryClient.invalidateQueries({ queryKey: ['briefing'] });
    },
  });

  const handleNavigate = useCallback((next: AppPage) => {
    setPage(next);
    if (next !== 'mail') setSearchQuery('');
  }, []);

  // Typing a global search always lands in the mail workspace, where the
  // results span all locally synced non-spam/non-trash mail.
  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    if (value.trim().length > 0 && page !== 'mail') setPage('mail');
  }, [page]);

  const accountInitial = useMemo(
    () => (gmailAccount?.display_name?.[0] ?? gmailAccount?.email_address?.[0] ?? '').toUpperCase(),
    [gmailAccount]
  );

  const meta = PAGE_META[page];

  return (
    <div className="app-shell">
      <IconRail
        page={page}
        onNavigate={handleNavigate}
        aiReady={aiReady}
        gmailConnected={Boolean(gmailAccount)}
      />

      <WorkspaceHeader
        title={meta.title}
        subtitle={meta.subtitle}
        searchValue={searchQuery}
        onSearchChange={handleSearchChange}
        aiReady={aiReady}
        accountInitial={accountInitial || undefined}
      />

      <main className="workspace-content">
        {page === 'overview' && <OverviewPage onNavigate={handleNavigate} />}
        {page === 'mail' && (
          <MailWorkspace
            searchQuery={searchQuery}
            onClearSearch={() => setSearchQuery('')}
            syncState={{
              syncing: syncMutation.isPending,
              lastSyncAt: gmailAccount?.last_sync_at ?? null,
            }}
            onRequestSync={() => {
              if (gmailAccount) syncMutation.mutate(gmailAccount.id);
            }}
          />
        )}
        {page === 'tasks' && <TasksPage />}
        {page === 'deadlines' && <DeadlinesPage />}
        {page === 'accounts' && <AccountsPage />}
        {page === 'settings' && <SettingsPage />}
      </main>

      <AnalysisProgress />
    </div>
  );
}
