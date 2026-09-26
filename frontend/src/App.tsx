import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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
import {
  accounts as fetchAccounts,
  emailCounts as fetchEmailCounts,
  health as fetchHealth,
  syncAccount,
  type MailFilter,
  type MailScope,
} from './api/emails';
import { FocusIntentContext, focusTarget, isAttached } from './lib/focus';
import type { FocusTarget } from './lib/focus';
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
  // Mail view + filter live here, not inside MailWorkspace, so the sidebar
  // is the single surface that owns them. Previously these were local to the
  // pane and therefore invisible from every other page.
  const [mailScope, setMailScope] = useState<MailScope>('inbox');
  const [mailFilter, setMailFilter] = useState<MailFilter>('all');
  const queryClient = useQueryClient();

  const { data: accountsList = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 0,
  });

  const { data: counts } = useQuery({
    queryKey: ['emailCounts', 'all'],
    queryFn: () => fetchEmailCounts(),
    staleTime: 30_000,
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

  // ── Focus management ────────────────────────────────────────────────────
  // Intent is recorded by whatever replaces the user's context, and consumed
  // once. Nothing infers it from a state change, which is what keeps a
  // background refetch or a plain re-render from ever moving focus.
  //
  // Declared before the navigation callbacks below because they capture it.
  const focusIntent = useRef<FocusTarget | null>(null);
  const viewHeadingRef = useRef<HTMLHeadingElement | null>(null);
  const mainRef = useRef<HTMLElement | null>(null);
  // Bumped on every view-focus request so the effect below runs for a retry
  // that swaps an error for content, not only for a page change.
  const [focusVersion, setFocusVersion] = useState(0);

  const requestFocus = useCallback((target: FocusTarget) => {
    focusIntent.current = target;
    if (target === 'view') setFocusVersion(v => v + 1);
  }, []);

  const takeFocusIntent = useCallback((target: FocusTarget) => {
    if (focusIntent.current !== target) return false;
    focusIntent.current = null;
    return true;
  }, []);

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
  //
  // This is a deliberate cross-page jump from a button that is about to
  // unmount, so focus has to be re-homed or it falls to <body>. Typing a
  // global search also changes page, but it must NOT: the user's focus is in
  // the search field and taking it away mid-keystroke would be hostile.
  const handleOpenEmail = useCallback((emailId: string) => {
    setSearchQuery('');
    setOpenEmailId(emailId);
    setPage('mail');
    requestFocus('reader');
  }, [requestFocus]);

  // Only counts the API actually returns. Alfred shows no count it cannot
  // source from real data.
  const navCounts = useMemo(
    () => ({
      inbox: counts?.active_inbox,
      allMail: counts?.all_mail,
    }),
    [counts]
  );

  // Navigation triggered from page *content* (an Overview shortcut) rather than
  // from the rail. The control the user pressed is about to unmount, so focus
  // has to be re-homed. The rail deliberately does not use this: arrowing the
  // rail both moves focus and changes page, so moving focus again would pull
  // the user out of the rail on the first arrow press.
  const handleNavigateFromContent = useCallback(
    (next: AppPage) => {
      if (next === page) return;
      handleNavigate(next);
      requestFocus('view');
    },
    [page, handleNavigate, requestFocus]
  );

  const activeMailView = `${mailScope}:${mailFilter}`;

  const handleNavigateMail = useCallback(
    (scope: MailScope, filter: MailFilter) => {
      setMailScope(scope);
      setMailFilter(filter);
      setPage('mail');
    },
    []
  );

  const syncAll = syncMutation;
  const handleSyncAll = useCallback(() => {
    void syncMutation.mutateAsync(gmailAccounts.map((a) => a.id));
  }, [gmailAccounts, syncMutation]);

  const meta = PAGE_META[page];

  // A navigation or a successful retry that did not ask for focus keeps whatever
  // the user was on. The heading lives in the header, which is mounted for every
  // view, so this runs after commit with the target already present.
  useEffect(() => {
    if (!takeFocusIntent('view')) return;
    const heading = viewHeadingRef.current;
    if (isAttached(heading)) focusTarget(heading);
  }, [page, focusVersion, takeFocusIntent]);

  const handleSkipToContent = useCallback((event: React.MouseEvent<HTMLAnchorElement>) => {
    // The href is kept so this works with scripting off and is announced as a
    // real link. The explicit focus makes the behaviour deterministic instead
    // of relying on fragment navigation, which jsdom does not perform and which
    // is uneven across engines.
    const main = mainRef.current;
    if (!isAttached(main)) return;
    event.preventDefault();
    main.focus();
    main.scrollIntoView?.({ block: 'start' });
  }, []);

  return (
    <FocusIntentContext.Provider value={{ requestFocus, takeFocusIntent }}>
      <div className="app-shell">
        <a className="skip-link" href="#main-content" onClick={handleSkipToContent}>
          Skip to content
        </a>

      <IconRail
        page={page}
        onNavigate={handleNavigate}
        aiReady={aiReady}
        gmailConnected={Boolean(gmailAccount)}
        counts={navCounts}
        activeMailView={activeMailView}
        onNavigateMail={handleNavigateMail}
      />

      <WorkspaceHeader
        title={meta.title}
        subtitle={meta.subtitle}
        headingRef={viewHeadingRef}
        searchValue={searchQuery}
        onSearchChange={handleSearchChange}
        aiReady={aiReady}
        aiState={health?.ai}
        accountEmail={gmailAccount?.email_address}
        onSync={syncAll.isPending ? undefined : handleSyncAll}
        syncing={syncAll.isPending}
      />

      <main className="workspace-content" id="main-content" tabIndex={-1} ref={mainRef}>
        {page === 'overview' && (
          <OverviewPage
            onNavigate={handleNavigateFromContent}
            onOpenEmail={handleOpenEmail}
          />
        )}
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
            scopeOverride={mailScope}
            filterOverride={mailFilter}
            onScopeChange={handleNavigateMail}
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
    </FocusIntentContext.Provider>
  );
}
