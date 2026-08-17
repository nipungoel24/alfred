import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RefreshCw, Star, MessageSquareReply, Archive } from 'lucide-react';
import { emails as fetchEmails, emailCounts } from '../api/emails';
import type { MailCategory } from '../api/emails';
import { CATEGORY_ORDER } from '../api/emails';
import { CategoryTabs } from './CategoryTabs';
import { MessageList } from './MessageList';
import { MessageReader } from './MessageReader';
import { IntelligencePanel } from '../intelligence/IntelligencePanel';
import type { RowFilter } from './MessageRow';

const LATER_KEY = 'alfred-later-ids';

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
  syncState: { syncing: boolean; lastSyncAt: string | null };
  onRequestSync: () => void;
}

export function MailWorkspace({ searchQuery, syncState, onRequestSync }: MailWorkspaceProps) {
  const [category, setCategory] = useState<MailCategory>('primary');
  const [filter, setFilter] = useState<RowFilter>('all');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [intelVisible, setIntelVisible] = useState(true);
  const [laterIds, setLaterIds] = useState<Set<string>>(readLaterIds);

  const { data: counts, refetch: refetchCounts } = useQuery({
    queryKey: ['emailCounts'],
    queryFn: emailCounts,
    staleTime: 15_000,
  });

  const { data: emailsList = [], isLoading, isFetching } = useQuery({
    queryKey: ['emails', { category, filter, searchQuery }],
    queryFn: () => fetchEmails({
      category,
      priority: filter === 'important' ? 'high' : undefined,
      needsReply: filter === 'reply' ? true : filter === 'all' || filter === 'later' ? null : undefined,
      query: searchQuery,
      limit: 500,
    }),
  });

  const displayedEmails = useMemo(() => {
    if (filter === 'later') return emailsList.filter(e => laterIds.has(e.id));
    if (filter === 'important') {
      return emailsList.filter(e =>
        e.analysis?.priority === 'high' || e.analysis?.priority === 'urgent' || e.label_ids?.includes('IMPORTANT'));
    }
    if (filter === 'reply') return emailsList.filter(e => e.analysis?.needs_reply);
    return emailsList;
  }, [emailsList, filter, laterIds]);

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

  // Keep counts fresh when new analyses land or sync happens
  useEffect(() => {
    const t = setInterval(() => {
      void refetchCounts();
    }, 60_000);
    return () => clearInterval(t);
  }, [refetchCounts]);

  return (
    <div className="mail-workspace">
      {/* ── Mail pane: categories + list ── */}
      <div className="mail-pane">
        <div className="mail-pane-head">
          <div className="mail-pane-title">
            <span className="title">Inbox</span>
            <span className="count">{counts?.active_inbox ?? 0} messages</span>
          </div>
          <CategoryTabs
            categories={CATEGORY_ORDER}
            active={category}
            counts={counts}
            onChange={c => setCategory(c)}
          />
        </div>

        <div className="mail-pane-toolbar" role="toolbar" aria-label="Mail filters">
          <FilterButton
            label="All"
            active={filter === 'all'}
            onClick={() => setFilter('all')}
          />
          <FilterButton
            label="Important"
            icon={<Star />}
            active={filter === 'important'}
            onClick={() => setFilter('important')}
          />
          <FilterButton
            label="Reply"
            icon={<MessageSquareReply />}
            active={filter === 'reply'}
            onClick={() => setFilter('reply')}
          />
          <FilterButton
            label="Later"
            icon={<Archive />}
            active={filter === 'later'}
            onClick={() => setFilter('later')}
          />
          <span className="spacer" />
          {isFetching && <RefreshCw size={12} className="btn-spinner" style={{ color: 'var(--text-muted)' }} aria-label="Refreshing" />}
          <button
            type="button"
            className="filter-icon-btn"
            onClick={onRequestSync}
            disabled={syncState.syncing}
            aria-label="Sync Gmail"
            title={syncState.lastSyncAt ? `Last sync: ${new Date(syncState.lastSyncAt).toLocaleString()}` : 'Sync Gmail'}
          >
            {syncState.syncing ? <RefreshCw size={13} className="btn-spinner" aria-hidden="true" /> : <RefreshCw size={13} aria-hidden="true" />}
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
