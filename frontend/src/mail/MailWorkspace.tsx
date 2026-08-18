import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { RefreshCw, Star, MessageSquareReply, Archive, Search, X, Pause, Play } from 'lucide-react';
import {
  emails as fetchEmails, emailCounts, accounts as fetchAccounts,
  backfillAccount, pauseBackfill,
} from '../api/emails';
import type { MailCategory, MailKind, MailScope } from '../api/emails';
import { CATEGORY_ORDER } from '../api/emails';
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
  syncState: { syncing: boolean; lastSyncAt: string | null };
  onRequestSync: () => void;
}

export function MailWorkspace({ searchQuery, onClearSearch, syncState, onRequestSync }: MailWorkspaceProps) {
  const queryClient = useQueryClient();
  const [view, setView] = useState<MailScope>('inbox');
  const [kind, setKind] = useState<MailKind | null>(null);
  const [category, setCategory] = useState<MailCategory>('primary');
  const [filter, setFilter] = useState<RowFilter>('all');
  const [viewFilter, setViewFilter] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [intelVisible, setIntelVisible] = useState(true);
  const [laterIds, setLaterIds] = useState<Set<string>>(readLaterIds);

  const globalSearchActive = searchQuery.trim().length > 0;
  const scope: MailScope = globalSearchActive ? 'all' : view;
  const activeQuery = globalSearchActive ? searchQuery : viewFilter;

  const { data: counts, refetch: refetchCounts } = useQuery({
    queryKey: ['emailCounts'],
    queryFn: emailCounts,
    staleTime: 15_000,
  });

  // Passive observation of backend-owned backfill state.
  const { data: accountsList = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
    staleTime: 10_000,
    refetchInterval: ACCOUNTS_REFRESH_MS,
  });

  const gmailAccount = accountsList.find(a => a.provider === 'gmail' && a.connection_status === 'connected');
  const backfill = gmailAccount?.backfill;

  const { data: emailsList = [], isLoading, isFetching, refetch } = useQuery({
    queryKey: ['emails', { view, kind, category, filter, globalSearchActive, searchQuery, viewFilter }],
    queryFn: () => fetchEmails({
      category: globalSearchActive || view === 'all' ? null : category,
      scope,
      kind: globalSearchActive ? null : view === 'all' ? kind : null,
      priority: filter === 'important' && !globalSearchActive ? 'high' : undefined,
      needsReply: filter === 'reply' && !globalSearchActive ? true : undefined,
      query: activeQuery || undefined,
      limit: 500,
    }),
    staleTime: 15_000,
  });

  // Backfill controls: start/resume + pause. The loop itself lives in the
  // backend worker; these only flip the typed state and arm the job.
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

  useEffect(() => {
    const t = setInterval(() => void refetchCounts(), 60_000);
    return () => clearInterval(t);
  }, [refetchCounts]);

  const paneCount = view === 'inbox' ? counts?.active_inbox ?? 0 : counts?.all_mail ?? 0;
  const paneTitle = globalSearchActive ? 'Search results' : view === 'inbox' ? 'Inbox' : 'All Mail';

  return (
    <div className="mail-workspace">
      {/* ── Mail pane ── */}
      <div className="mail-pane">
        <div className="mail-pane-head">
          <div className="mail-pane-title">
            <span className="title">{paneTitle}</span>
            <span className="count">{paneCount} messages</span>
          </div>

          {!globalSearchActive && (
            <div className="mail-view-switch" role="tablist" aria-label="Mailbox scope">
              <ViewButton label="Inbox" active={view === 'inbox'} onClick={() => { setView('inbox'); setFilter('all'); }} />
              <ViewButton label="All Mail" active={view === 'all'} onClick={() => { setView('all'); setFilter('all'); }} />
            </div>
          )}

          {globalSearchActive && (
            <div className="search-scope-banner">
              <span>Searching all local mail</span>
              <button type="button" className="icon-btn" onClick={onClearSearch} aria-label="Clear search">
                <X size={14} aria-hidden="true" />
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

          <BackfillStatusLine
            backfill={backfill}
            onResume={() => gmailAccount && backfillMutation.mutate(gmailAccount.id)}
            onPause={() => gmailAccount && pauseMutation.mutate(gmailAccount.id)}
            busy={backfillMutation.isPending || pauseMutation.isPending}
          />
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
            className="filter-icon-btn"
            onClick={() => {
              onRequestSync();
              void refetch();
            }}
            disabled={syncState.syncing}
            aria-label="Sync Gmail"
            title={syncState.lastSyncAt ? `Last sync: ${new Date(syncState.lastSyncAt).toLocaleString()}` : 'Sync Gmail'}
          >
            {syncState.syncing
              ? <span className="btn-spinner" aria-hidden="true" />
              : <RefreshCw size={13} aria-hidden="true" />}
            Sync
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

      {/* ── Reader pane ── */}
      <MessageReader
        emailId={selectedId}
        intelVisible={intelVisible}
        onToggleIntel={() => setIntelVisible(v => !v)}
        laterIds={laterIds}
        onToggleLater={toggleLater}
      />

      {/* ── Alfred intelligence pane ── */}
      {intelVisible && selectedEmail && (
        <IntelligencePanel
          email={selectedEmail}
          onClose={() => setIntelVisible(false)}
        />
      )}
    </div>
  );
}

function BackfillStatusLine({ backfill, onResume, onPause, busy }: {
  backfill?: import('../api/emails').BackfillStatus;
  onResume: () => void;
  onPause: () => void;
  busy: boolean;
}) {
  if (!backfill) return null;
  const { state, imported, remaining_estimate: remaining, complete, last_error: lastError } = backfill;

  if (complete) {
    return (
      <div className="backfill-status complete" role="status">
        All mail synced
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
