import { memo } from 'react';
import { Archive, MessageSquareReply, Star, ArchiveRestore } from 'lucide-react';
import type { Email, MailCategory } from '../api/emails';

const CATEGORY_BADGE: Record<MailCategory, string> = {
  primary: 'Primary',
  promotions: 'Promo',
  social: 'Social',
  updates: 'Update',
  forums: 'Forum',
};

export type RowFilter = 'all' | 'important' | 'reply' | 'later';

interface MessageRowProps {
  email: Email;
  category: MailCategory;
  selected: boolean;
  onSelect: (id: string) => void;
  onToggleLater: (id: string) => void;
  laterIds: ReadonlySet<string>;
}

export const MessageRow = memo(function MessageRow({
  email, category, selected, onSelect, onToggleLater, laterIds,
}: MessageRowProps) {
  const analysis = email.analysis;
  const unread = email.label_ids?.includes('UNREAD');
  const gmailImportant = email.label_ids?.includes('IMPORTANT');
  const important = gmailImportant || analysis?.priority === 'high' || analysis?.priority === 'urgent';
  const needsReply = analysis?.needs_reply;
  const isLater = laterIds.has(email.id);

  const timeLabel = formatTime(email.received_at);
  const snippet = bodySnippet(email);

  return (
    <div
      className={`message-row ${unread ? 'unread' : 'read'} ${selected ? 'selected' : ''}`}
      role="button"
      tabIndex={0}
      aria-pressed={selected}
      aria-label={`${unread ? 'Unread' : 'Read'} email from ${email.sender_name || email.sender}: ${email.subject}`}
      onClick={() => onSelect(email.id)}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(email.id);
        }
      }}
    >
      <div className="message-row-top">
        <span className="message-sender">{email.sender_name || email.sender}</span>
        <span className="message-time">{timeLabel}</span>
      </div>
      <div className="message-subject">{email.subject}</div>
      <div className="message-snippet">{snippet}</div>
      <div className="message-row-bottom">
        {important && (
          <span className={`badge ${analysis?.priority === 'urgent' ? 'badge-urgent' : 'badge-high'}`}>
            {analysis?.priority === 'urgent' ? 'Urgent' : 'Important'}
          </span>
        )}
        {needsReply && <span className="badge badge-reply">Reply</span>}
        {category !== 'primary' && <span className="badge badge-neutral">{CATEGORY_BADGE[category]}</span>}
        {isLater && <span className="badge badge-neutral">Later</span>}
        <span className="message-quick-actions">
          {needsReply && (
            <span className="quick-action-indicator" title="Needs a reply">
              <MessageSquareReply />
            </span>
          )}
          {important && (
            <span className="quick-action-indicator" title="Important">
              <Star />
            </span>
          )}
          <button
            type="button"
            className="quick-action-btn"
            aria-label={isLater ? 'Remove from Later' : 'Save for Later'}
            title={isLater ? 'Remove from Later' : 'Save for Later'}
            onClick={e => {
              e.stopPropagation();
              onToggleLater(email.id);
            }}
          >
            {isLater ? <ArchiveRestore /> : <Archive />}
          </button>
        </span>
      </div>
    </div>
  );
});

export function formatTime(dateStr?: string | null): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return '';
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  if (isToday) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
  if (d.getFullYear() === now.getFullYear()) {
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }
  return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: '2-digit' });
}

function bodySnippet(email: Email): string {
  const stored = (email as Email & { source_metadata?: { gmail_raw?: { snippet?: string } } })
    .source_metadata?.gmail_raw?.snippet;
  if (stored) return stored;
  const text = email.body ?? '';
  const firstLine = text.split('\n').find(line => line.trim().length > 0) ?? '';
  return firstLine.length > 110 ? `${firstLine.slice(0, 110)}…` : firstLine;
}
