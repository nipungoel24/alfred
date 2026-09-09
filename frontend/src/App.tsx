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

export interface SyncOutcome {
  id: string;
  ok: boolean;
  error?: string;
}

export default function App() {
  const [page, setPage] = useState<AppPage>('mail');
  const [searchQuery, setSearchQuery] = useState('');
  const [syncReport, setSyncReport] = useState<SyncOutcome[] | null>(null);
  // Navigation intent: open an EXACT email in the Mail workspace (from a
  // task/deadline/overview source preview). No routing framework — the
  // workspace consumes and clears it.
  const [openEmailId, setOpenEmailId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: accountsList = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 0,
  });

  const gmailAccounts = accountsList.filter(a => a.provider === 'gmail' && a.connection_status === 'connected');
  const gmailAccount = gmailAccounts[0];
  const aiReady = health?.ai === 'ready';

  // Sync-all is ONE logical operation: a single mutation over the target
  // account ids with aggregate pending state. Parallel per-account syncs
  // settle independently; failures identify their account without hiding
  // the accounts that succeeded.
  const syncMutation = useMutation({
    mutationFn: async (ids: string[]): Promise<SyncOutcome[]> => {
      const settled = await Promise.allSettled(ids.map(id => syncAccount(id, false)));
      return ids.map((id, i) => {
        const result = settled[i];
        if (result.status === 'fulfilled') return { id, ok: true };
        const reason = result.reason;
        return {
          id,
          ok: false,
          error: reason instanceof Error ? reason.message : 'Sync failed',
        };
      });
    },
    onSuccess: (outcomes) => {
      setSyncReport(outcomes.every(o => o.ok) ? null : outcomes);
      void queryClient.invalidateQueries({ queryKey: ['emails'] });
      void queryClient.invalidateQueries({ queryKey: ['emailCounts'] });
      void queryClient.invalidateQueries({ queryKey: ['accounts'] });
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
      void queryClient.invalidateQueries({ queryKey: ['briefing'] });
    },
  });

  const lastSyncByAccount = useMemo(() => {
    const map: Record<string, string | null> = {};
    for (const account of accountsList) {
      map[account.id] = account.last_sync_at ?? null;
    }
    return map;
  }, [accountsList]);

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

  // "Open in Mail" from any source preview: land on Mail with the exact
  // message selected — never a bare navigation with nothing selected.
  const handleOpenEmail = useCallback((emailId: string) => {
    setSearchQuery('');
    setOpenEmailId(emailId);
    setPage('mail');
  }, []);

  const accountInitial = useMemo(
    () => (gmailAccount?.display_name?.[0] ?? gmailAccount?.email_address?.[0] ?? '').toUpperCase(),
    [gmailAccount]
  );

  const meta = PAGE_META[page];

  return (
    <div className="app-shell">
      {/* Ambient aurora — quiet Siri-like glow behind the product UI */}
      <div className="ambient-layer" aria-hidden="true">
        <span className="ambient-orb orb-violet" />
        <span className="ambient-orb orb-indigo" />
        <span className="ambient-orb orb-cyan" />
        <span className="ambient-orb orb-pink" />
      </div>

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
        aiState={health?.ai}
        accountInitial={accountInitial || undefined}
      />

      <main className="workspace-content">
        {page === 'overview' && <OverviewPage onNavigate={handleNavigate} onOpenEmail={handleOpenEmail} />}
        {page === 'mail' && (
          <MailWorkspace
            searchQuery={searchQuery}
            onClearSearch={() => setSearchQuery('')}
            onSearchChange={handleSearchChange}
            openEmailId={openEmailId}
            onConsumeOpenEmail={() => setOpenEmailId(null)}
            syncState={{
              syncing: syncMutation.isPending,
              lastSyncByAccount,
            }}
            syncReport={syncReport}
            onDismissSyncReport={() => setSyncReport(null)}
            onRequestSync={(accountId?: string) => {
              // No account id (All accounts mode) => sync EVERY connected
              // Gmail account in one aggregate operation. A specific id
              // syncs only that account. The button disables while the
              // aggregate is pending, so repeat clicks can't stack syncs.
              if (syncMutation.isPending) return;
              const targets = accountId
                ? accountsList.filter(a => a.id === accountId)
                : gmailAccounts;
              if (targets.length === 0) return;
              setSyncReport(null);
              syncMutation.mutate(targets.map(t => t.id));
            }}
          />
        )}
        {page === 'tasks' && <TasksPage onOpenInMail={handleOpenEmail} />}
        {page === 'deadlines' && <DeadlinesPage onOpenInMail={handleOpenEmail} />}
        {page === 'accounts' && <AccountsPage />}
        {page === 'settings' && <SettingsPage />}
      </main>

      <AnalysisProgress />
    </div>
  );
}
