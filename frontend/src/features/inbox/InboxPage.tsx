import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';
import { emails as fetchEmails } from '../../api/emails';
import { EmailDetail } from '../email/EmailDetail';
import { RefreshCw, Inbox as InboxIcon } from 'lucide-react';

interface InboxPageProps {
  priorityFilter?: string;
  needsReplyFilter?: boolean | null;
  searchQuery?: string;
}

export function InboxPage({ priorityFilter = '', needsReplyFilter = null, searchQuery = '' }: InboxPageProps) {
  const [localSearch, setLocalSearch] = useState('');
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  const activeSearch = searchQuery || localSearch;

  const { data: emails = [], isLoading, isRefetching } = useQuery({
    queryKey: ['emails', { searchQuery: activeSearch, priorityFilter, needsReplyFilter }],
    queryFn: () => fetchEmails(activeSearch, priorityFilter, needsReplyFilter),
  });

  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: emails.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 56,
    overscan: 10,
  });

  const formatTime = (dateStr?: string | null) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    if (isToday) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <div className="inbox-layout">
      <div className="inbox-list-pane">
        {/* Toolbar */}
        <div className="list-toolbar">
          {!searchQuery && (
            <div className="search-box" style={{ flex: 1, maxWidth: 320 }}>
              <input
                type="text"
                placeholder="Filter emails..."
                value={localSearch}
                onChange={e => setLocalSearch(e.target.value)}
              />
            </div>
          )}
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            {isRefetching && (
              <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite', color: 'var(--text-muted)' }} />
            )}
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              {emails.length} messages
            </span>
          </div>
        </div>

        {/* Email list */}
        {isLoading ? (
          <div style={{ padding: 'var(--space-5)' }}>
            {[...Array(8)].map((_, i) => (
              <div key={i} style={{ display: 'flex', gap: 'var(--space-3)', padding: '12px var(--space-5)', borderBottom: '1px solid var(--border-subtle)' }}>
                <div className="skeleton" style={{ width: 120, height: 14 }} />
                <div className="skeleton" style={{ flex: 1, height: 14 }} />
                <div className="skeleton" style={{ width: 50, height: 14 }} />
              </div>
            ))}
          </div>
        ) : emails.length === 0 ? (
          <div className="empty-state">
            <InboxIcon />
            <p>No emails found.</p>
          </div>
        ) : (
          <div ref={parentRef} className="email-list">
            <div style={{ height: rowVirtualizer.getTotalSize(), width: '100%', position: 'relative' }}>
              {rowVirtualizer.getVirtualItems().map(virtualRow => {
                const email = emails[virtualRow.index];
                const isSelected = selectedEmailId === email.id;
                const isHighPriority = email.analysis?.priority === 'high' || email.analysis?.priority === 'urgent';
                return (
                  <button
                    key={virtualRow.index}
                    data-index={virtualRow.index}
                    ref={rowVirtualizer.measureElement}
                    type="button"
                    aria-pressed={isSelected}
                    aria-label={`Open email from ${email.sender_name || email.sender}: ${email.subject}`}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                  >
                    <div
                      className={`email-row ${isSelected ? 'selected' : ''}`}
                      onClick={() => setSelectedEmailId(email.id)}
                    >
                      <div className="email-sender">{email.sender_name || email.sender?.split('@')[0]}</div>
                      <div className="email-content">
                        <span className="email-subject">{email.subject}</span>
                        <span style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}> — </span>
                        <span className="email-snippet">{email.body?.slice(0, 80)}</span>
                      </div>
                      <div className="email-meta">
                        {email.analysis?.needs_reply && <span className="badge badge-reply">Reply</span>}
                        {isHighPriority && <span className={`badge badge-${email.analysis?.priority}`}>{email.analysis?.priority}</span>}
                        <span className="email-time">{formatTime(email.received_at)}</span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Detail panel */}
      {selectedEmailId && (
        <div className="inbox-detail-pane">
          <EmailDetail emailId={selectedEmailId} onClose={() => setSelectedEmailId(null)} />
        </div>
      )}
    </div>
  );
}
