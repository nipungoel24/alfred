import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Group, Panel, Separator } from 'react-resizable-panels';
import type { GroupImperativeHandle } from 'react-resizable-panels';
import { RefreshCw, Star, MessageSquareReply, Archive, Search, X, Pause, Play } from 'lucide-react';
import {
  emails as fetchEmails, emailCounts, accounts as fetchAccounts,
  backfillAccount, pauseBackfill, searchEmailsStructured,
} from '../api/emails';
import type { MailCategory, MailKind, MailScope, SearchFilters } from '../api/emails';
import { CATEGORY_ORDER } from '../api/emails';
import { parseSearchQuery, buildSearchQueryString, getSearchFilterChips } from '../search/searchParser';
import { readSavedLayout, persistLayout, DEFAULT_LAYOUT } from './layoutStore';
import { CategoryTabs } from './CategoryTabs';
import { MessageList } from './MessageList';
import { MessageReader } from './MessageReader';
import { IntelligencePanel } from '../intelligence/IntelligencePanel';
import type { RowFilter } from './MessageRow';

const LATER_KEY = 'alfred-later-ids';
const ACCOUNTS_REFRESH_MS = 15_000;

function readLaterIds(): Set<string> {
  try {
    const raw = localStorage.getItem(LATER_KEY);
    return new Set(raw ? (JSON.parse(raw) as string[]) : []);
  } catch {
    return new Set();
  }
}

function persistLaterIds(ids: Set<string>): void {
  try {
    localStorage.setItem(LATER_KEY, JSON.stringify([...ids]));
  } catch {
    /* storage unavailable */
  }
}

interface MailWorkspaceProps {
  searchQuery: string;
  onClearSearch: () => void;
  onSearchChange: (value: string) => void;
  syncState: { syncing: boolean; lastSyncByAccount: Record<string, string | null> };
  syncReport: { id: string; ok: boolean; error?: string }[] | null;
  onDismissSyncReport: () => void;
  onRequestSync: (accountId?: string) => void;
}

export function MailWorkspace({ searchQuery, onClearSearch, onSearchChange, syncState, syncReport, onDismissSyncReport, onRequestSync }: MailWorkspaceProps) {
  const queryClient = useQueryClient();
  const groupRef = useRef<GroupImperativeHandle>(null);
  const [view, setView] = useState<MailScope>('inbox');
  const [kind, setKind] = useState<MailKind | null>(null);
  const [category, setCategory] = useState<MailCategory>('primary');
  const [filter, setFilter] = useState<RowFilter>('all');
  const [viewFilter, setViewFilter] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [intelVisible, setIntelVisible] = useState(true);
  const [laterIds, setLaterIds] = useState<Set<string>>(readLaterIds);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);

  const globalSearchActive = searchQuery.trim().length > 0;
  const scope: MailScope = globalSearchActive ? 'all' : view;
  const activeQuery = globalSearchActive ? searchQuery : viewFilter;

  // Parse structured search filters from the global search query
  const parsedFilters = useMemo(() => {
    if (!globalSearchActive) return null;
    return parseSearchQuery(searchQuery);
  }, [globalSearchActive, searchQuery]);

  const hasStructuredFilters = useMemo(() => {
    if (!parsedFilters) return false;
    return Boolean(
      parsedFilters.from || parsedFilters.subject || parsedFilters.after ||
      parsedFilters.before || parsedFilters.category || parsedFilters.in ||
      parsedFilters.isUnread || parsedFilters.isRead ||
      parsedFilters.isImportant || parsedFilters.isReply
    );
  }, [parsedFilters]);

  const filterChips = useMemo(
    () => (globalSearchActive && parsedFilters ? getSearchFilterChips(parsedFilters) : []),
    [globalSearchActive, parsedFilters]
  );

  const removeChip = useCallback((key: string) => {
    if (!parsedFilters) return;
    const next = { ...parsedFilters };
    switch (key) {
      case 'from': next.from = undefined; break;
      case 'subject': next.subject = undefined; break;
      case 'isUnread': next.isUnread = undefined; break;
      case 'isRead': next.isRead = undefined; break;
      case 'isImportant': next.isImportant = undefined; break;
      case 'isReply': next.isReply = undefined; break;
      case 'after': next.after = undefined; break;
      case 'before': next.before = undefined; break;
      case 'category': next.category = undefined; break;
      case 'in': next.in = undefined; break;
    }
    onSearchChange(buildSearchQueryString(next));
  }, [parsedFilters, onSearchChange]);

  const { data: counts, refetch: refetchCounts } = useQuery({
    queryKey: ['emailCounts', selectedAccountId],
    queryFn: () => emailCounts(selectedAccountId || undefined),
    staleTime: 15_000,
  });

  const { data: accountsList = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
    staleTime: 10_000,
    refetchInterval: ACCOUNTS_REFRESH_MS,
  });

  const gmailAccounts = accountsList.filter(
    a => a.provider === 'gmail' && a.connection_status === 'connected'
  );
  // Selected account drives sync/backfill/counts/search. All-accounts mode
  // (null) aggregates — never silently the first account.
  const gmailAccount = selectedAccountId
    ? gmailAccounts.find(a => a.id === selectedAccountId)
    : undefined;
  const backfillAccounts = selectedAccountId
    ? gmailAccounts.filter(a => a.id === selectedAccountId)
    : gmailAccounts;

  const { data: emailsList = [], isLoading, isFetching, refetch } = useQuery({
    queryKey: ['emails', { view, kind, category, filter, globalSearchActive, searchQuery, viewFilter, selectedAccountId, hasStructuredFilters }],
    queryFn: () => {
      // Global search ALWAYS uses the structured endpoint (FTS5/BM25),
      // even for plain free text: free_text-only filters hit the same
      // production search path as operator queries. The pane-local
      // "Filter inbox" field below stays on the contextual list endpoint.
      if (globalSearchActive && parsedFilters) {
        const searchFilters: SearchFilters = {
          free_text: parsedFilters.freeText,
          sender: parsedFilters.from,
          subject: parsedFilters.subject,
          is_unread: parsedFilters.isUnread,
          is_read: parsedFilters.isRead,
          is_important: parsedFilters.isImportant,
          needs_reply: parsedFilters.isReply,
          after: parsedFilters.after,
          before: parsedFilters.before,
          category: parsedFilters.category,
          mailbox_state: parsedFilters.in,
        };
        return searchEmailsStructured(searchFilters, {
          accountId: selectedAccountId || undefined,
          limit: 500,
        });
      }
      // Standard email list endpoint (pane-local filter only)
      return fetchEmails({
        category: view === 'all' ? null : category,
        scope,
        kind: view === 'all' ? kind : null,
        priority: filter === 'important' ? 'high' : undefined,
        needsReply: filter === 'reply' ? true : undefined,
        query: activeQuery || undefined,
        accountId: selectedAccountId || undefined,
        limit: 500,
      });
    },
    staleTime: 15_000,
  });

  const backfillMutation = useMutation({
    mutationFn: (id: string) => backfillAccount(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
  const pauseMutation = useMutation({
    mutationFn: (id: string) => pauseBackfill(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  const displayedEmails = useMemo(() => {
    if (globalSearchActive) return emailsList;
    if (filter === 'later') return emailsList.filter(e => laterIds.has(e.id));
    if (filter === 'important') {
      return emailsList.filter(e =>
        e.analysis?.priority === 'high' || e.analysis?.priority === 'urgent' || e.label_ids?.includes('IMPORTANT'));
    }
    if (filter === 'reply') return emailsList.filter(e => e.analysis?.needs_reply);
    return emailsList;
  }, [emailsList, filter, laterIds, globalSearchActive]);

  const selectedEmail = useMemo(
    () => emailsList.find(e => e.id === selectedId) ?? null,
    [emailsList, selectedId]
  );

  const toggleLater = useCallback((id: string) => {
    setLaterIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      persistLaterIds(next);
      return next;
    });
  }, []);

  const handleToggleIntel = useCallback(() => {
    setIntelVisible(v => {
      const next = !v;
      const group = groupRef.current;
      if (group) {
        const current = group.getLayout();
        group.setLayout({
          ...current,
          intel: next ? (readSavedLayout()?.intel ?? DEFAULT_LAYOUT.intel) : 0,
        });
      }
      return next;
    });
  }, []);

  const handleLayoutChanged = useCallback((layout: Record<string, number>) => {
    // persistLayout validates — a broken layout is never stored.
    persistLayout({ mail: layout.mail, reader: layout.reader, intel: layout.intel });
    if (layout.intel > 0) {
      setIntelVisible(true);
    }
  }, []);

  useEffect(() => {
    const t = setInterval(() => void refetchCounts(), 60_000);
    return () => clearInterval(t);
  }, [refetchCounts]);

  // Restore saved layout on mount
  useEffect(() => {
    const saved = readSavedLayout();
    if (saved && groupRef.current) {
      groupRef.current.setLayout(saved);
      if (saved.intel === 0) setIntelVisible(false);
    }
  }, []);

  const paneCount = view === 'inbox' ? counts?.active_inbox ?? 0 : counts?.all_mail ?? 0;
  const paneTitle = globalSearchActive ? 'Search results' : view === 'inbox' ? 'Inbox' : 'All Mail';

  // Last-sync refers to the selected account; in All mode the most recent
  // across connected accounts. Never another account's timestamp.
  const displayedLastSync = selectedAccountId
    ? (syncState.lastSyncByAccount[selectedAccountId] ?? null)
    : Object.values(syncState.lastSyncByAccount).filter(Boolean).sort().at(-1) ?? null;

  const failedSyncs = (syncReport ?? []).filter(r => !r.ok);

  const defaultLayout = readSavedLayout() ?? DEFAULT_LAYOUT;

  return (
    <div className="mail-workspace">
      <Group
        groupRef={groupRef}
        orientation="horizontal"
        defaultLayout={defaultLayout}
        onLayoutChanged={handleLayoutChanged}
        style={{ height: '100%' }}
      >
        {/* ── Mail pane ── */}
        <Panel id="mail" minSize={20} maxSize={45} defaultSize={defaultLayout.mail}>
          <div className="mail-pane">
            <div className="mail-pane-head">
              <div className="mail-pane-title">
                <span className="title">{paneTitle}</span>
                <span className="count">{paneCount} messages</span>
              </div>

              {accountsList.length > 1 && (
                <div className="account-filter">
                  <select
                    value={selectedAccountId || ''}
                    onChange={e => setSelectedAccountId(e.target.value || null)}
                    aria-label="Filter by account"
                    className="account-select"
                  >
                    <option value="">All accounts</option>
                    {accountsList.map(acc => (
                      <option key={acc.id} value={acc.id}>
                        {acc.display_name || acc.email_address}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {!globalSearchActive && (
                <div className="mail-view-switch" role="tablist" aria-label="Mailbox scope">
                  <ViewButton label="Inbox" active={view === 'inbox'} onClick={() => { setView('inbox'); setFilter('all'); }} />
                  <ViewButton label="All Mail" active={view === 'all'} onClick={() => { setView('all'); setFilter('all'); }} />
                </div>
              )}

              {globalSearchActive && (
                <div className="search-scope-banner">
                  <span>{selectedAccountId ? 'Searching selected account' : 'Searching all local mail'}</span>
                  <button type="button" className="icon-btn" onClick={onClearSearch} aria-label="Clear search">
                    <X size={14} aria-hidden="true" />
                  </button>
                </div>
              )}

              {globalSearchActive && filterChips.length > 0 && (
                <div className="search-filter-chips" aria-label="Active search filters">
                  {filterChips.map(chip => (
                    <button
                      key={chip.key}
                      type="button"
                      className="search-chip"
                      onClick={() => removeChip(chip.key)}
                      aria-label={`Remove ${chip.label} filter: ${chip.value}`}
                      title={`Remove ${chip.label} filter: ${chip.value}`}
                    >
                      <span className="search-chip-label">{chip.label}:</span>
                      <span className="search-chip-value">{chip.value}</span>
                      <X size={10} aria-hidden="true" />
                    </button>
                  ))}
                  <button
                    type="button"
                    className="search-chip-clear"
                    onClick={onClearSearch}
                  >
                    Clear all
                  </button>
                </div>
              )}

              {!globalSearchActive && view === 'inbox' && (
                <CategoryTabs
                  categories={CATEGORY_ORDER}
                  active={category}
                  counts={counts}
                  onChange={c => setCategory(c)}
                />
              )}

              {!globalSearchActive && view === 'all' && (
                <div className="allmail-kind-switch" role="tablist" aria-label="All Mail filter">
                  <KindButton label="All" active={kind === null} onClick={() => setKind(null)} />
                  <KindButton label="Received" active={kind === 'received'} onClick={() => setKind('received')} />
                  <KindButton label="Sent" active={kind === 'sent'} onClick={() => setKind('sent')} />
                  <KindButton label="Archived" active={kind === 'archived'} onClick={() => setKind('archived')} />
                </div>
              )}

              <BackfillStatusList
                accounts={backfillAccounts}
                showLabels={backfillAccounts.length > 1}
                onResume={(id) => backfillMutation.mutate(id)}
                onPause={(id) => pauseMutation.mutate(id)}
                busy={backfillMutation.isPending || pauseMutation.isPending}
              />

              {failedSyncs.length > 0 && (
                <SyncReportLine
                  failures={failedSyncs}
                  accounts={accountsList}
                  onDismiss={onDismissSyncReport}
                />
              )}
            </div>

            <div className="mail-pane-toolbar" role="toolbar" aria-label="Mail filters">
              {!globalSearchActive && view === 'inbox' && (
                <>
                  <FilterButton label="All" active={filter === 'all'} onClick={() => setFilter('all')} />
                  <FilterButton label="Important" icon={<Star />} active={filter === 'important'} onClick={() => setFilter('important')} />
                  <FilterButton label="Reply" icon={<MessageSquareReply />} active={filter === 'reply'} onClick={() => setFilter('reply')} />
                  <FilterButton label="Later" icon={<Archive />} active={filter === 'later'} onClick={() => setFilter('later')} />
                  <span className="spacer" />
                </>
              )}

              {!globalSearchActive && (
                <div className="pane-filter">
                  <Search size={12} aria-hidden="true" />
                  <input
                    type="search"
                    placeholder={`Filter ${paneTitle.toLowerCase()}`}
                    value={viewFilter}
                    onChange={e => setViewFilter(e.target.value)}
                    aria-label={`Filter ${paneTitle}`}
                  />
                  {viewFilter && (
                    <button type="button" className="pane-filter-clear" onClick={() => setViewFilter('')} aria-label="Clear filter">
                      <X size={11} aria-hidden="true" />
                    </button>
                  )}
                </div>
              )}

              {isFetching && !globalSearchActive && (
                <RefreshCw size={12} className="btn-spinner" style={{ color: 'var(--text-muted)' }} aria-label="Refreshing" />
              )}
              <button
                type="button"
                className="filter-icon-btn sync-button"
                onClick={() => {
                  onRequestSync(gmailAccount?.id);
                  void refetch();
                }}
                disabled={syncState.syncing}
                aria-label="Sync Gmail"
                title={displayedLastSync ? `Last sync: ${new Date(displayedLastSync).toLocaleString()}` : 'Sync Gmail'}
              >
                {syncState.syncing
                  ? <span className="btn-spinner" aria-hidden="true" />
                  : <RefreshCw size={13} aria-hidden="true" />}
                <span className="sync-label">Sync</span>
              </button>
            </div>

            <MessageList
              emails={displayedEmails}
              category={category}
              selectedId={selectedId}
              isLoading={isLoading}
              onSelect={id => setSelectedId(prev => (prev === id ? prev : id))}
              onToggleLater={toggleLater}
              laterIds={laterIds}
            />
          </div>
        </Panel>

        <Separator className="pane-separator" />

        {/* ── Reader pane ── */}
        <Panel id="reader" minSize={30} defaultSize={defaultLayout.reader}>
          <MessageReader
            emailId={selectedId}
            intelVisible={intelVisible}
            onToggleIntel={handleToggleIntel}
            laterIds={laterIds}
            onToggleLater={toggleLater}
          />
        </Panel>

        <Separator className="pane-separator" />

        {/* ── Alfred intelligence pane ── */}
        <Panel id="intel" minSize={0} maxSize={40} defaultSize={defaultLayout.intel} collapsedSize={0} collapsible>
          {selectedEmail && (
            <IntelligencePanel
              email={selectedEmail}
              onClose={handleToggleIntel}
            />
          )}
        </Panel>
      </Group>
    </div>
  );
}

function BackfillStatusList({ accounts, showLabels, onResume, onPause, busy }: {  accounts: import('../api/emails').EmailAccount[];
  showLabels: boolean;
  onResume: (id: string) => void;
  onPause: (id: string) => void;
  busy: boolean;
}) {
  if (accounts.length === 0) return null;
  return (
    <>
      {accounts.map(account => (
        <BackfillStatusLine
          key={account.id}
          backfill={account.backfill}
          accountLabel={showLabels ? (account.display_name || account.email_address) : undefined}
          onResume={() => onResume(account.id)}
          onPause={() => onPause(account.id)}
          busy={busy}
        />
      ))}
    </>
  );
}

function SyncReportLine({ failures, accounts, onDismiss }: {
  failures: { id: string; ok: boolean; error?: string }[];
  accounts: import('../api/emails').EmailAccount[];
  onDismiss: () => void;
}) {
  const names = failures.map(f => {
    const account = accounts.find(a => a.id === f.id);
    return account?.display_name || account?.email_address || f.id;
  });
  const detail = failures.map(f => `${f.id}: ${f.error ?? 'failed'}`).join('; ');
  return (
    <div className="sync-report" role="alert" title={detail}>
      <span>Sync failed for {names.join(', ')}</span>
      <button type="button" className="icon-btn" onClick={onDismiss} aria-label="Dismiss sync errors">
        <X size={12} aria-hidden="true" />
      </button>
    </div>
  );
}

function BackfillStatusLine({ backfill, accountLabel, onResume, onPause, busy }: {
  backfill?: import('../api/emails').BackfillStatus;
  accountLabel?: string;
  onResume: () => void;
  onPause: () => void;
  busy: boolean;
}) {
  if (!backfill) return null;
  const { state, imported, remaining_estimate: remaining, complete, last_error: lastError } = backfill;

  if (complete) {
    return (
      <div className="backfill-status complete" role="status">
        {accountLabel && <span className="backfill-account">{accountLabel}</span>}
        <span>All mail synced</span>
        {imported > 0 && <span className="backfill-detail">{imported} older messages local</span>}
      </div>
    );
  }

  let label: string;
  if (state === 'paused') label = 'Syncing paused';
  else if (state === 'failed') label = 'Syncing failed';
  else label = 'Syncing older mail…';

  return (
    <div className="backfill-status" role="status">
      {state === 'running' && <span className="btn-spinner" aria-hidden="true" />}
      {accountLabel && <span className="backfill-account">{accountLabel}</span>}
      <span>{label}</span>
      {state === 'running' && (
        <span className="backfill-detail">
          {imported > 0 && `${imported} synced`}
          {imported > 0 && remaining !== null ? ` · ` : ''}
          {remaining !== null && `~${remaining} remaining`}
        </span>
      )}
      {state === 'failed' && lastError && (
        <button type="button" className="backfill-retry" onClick={onResume} disabled={busy}>
          Retry
        </button>
      )}
      {state === 'running' && (
        <button type="button" className="backfill-retry" onClick={onPause} disabled={busy} aria-label="Pause syncing older mail">
          <Pause size={11} aria-hidden="true" />
        </button>
      )}
      {state === 'paused' && (
        <button type="button" className="backfill-retry" onClick={onResume} disabled={busy} aria-label="Resume syncing older mail">
          <Play size={11} aria-hidden="true" />
        </button>
      )}
    </div>
  );
}

function ViewButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      className={`view-tab ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function KindButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      className={`kind-tab ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function FilterButton({ label, icon, active, onClick }: {
  label: string; icon?: ReactNode; active: boolean; onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={`filter-icon-btn ${active ? 'active' : ''}`}
      onClick={onClick}
      aria-pressed={active}
    >
      {icon}
      {label}
    </button>
  );
}
