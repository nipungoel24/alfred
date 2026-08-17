import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { MailOpen } from 'lucide-react';
import type { Email, MailCategory } from '../api/emails';
import { MessageRow } from './MessageRow';

interface MessageListProps {
  emails: Email[];
  category: MailCategory;
  selectedId: string | null;
  isLoading: boolean;
  onSelect: (id: string) => void;
  onToggleLater: (id: string) => void;
  laterIds: ReadonlySet<string>;
}

export function MessageList({
  emails, category, selectedId, isLoading, onSelect, onToggleLater, laterIds,
}: MessageListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: emails.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 96,
    overscan: 8,
  });

  if (isLoading) {
    return (
      <div className="message-list" aria-busy="true" aria-label="Loading messages">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="skeleton-row">
            <div className="skeleton" style={{ width: '55%', height: 12 }} />
            <div className="skeleton" style={{ width: '80%', height: 12 }} />
            <div className="skeleton" style={{ width: '90%', height: 10 }} />
          </div>
        ))}
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div className="message-list">
        <div className="empty-state">
          <MailOpen aria-hidden="true" />
          <p>No messages here.</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={parentRef} className="message-list" role="listbox" aria-label="Messages">
      <div style={{ height: virtualizer.getTotalSize(), width: '100%', position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => {
          const email = emails[virtualRow.index];
          return (
            <div
              key={email.id}
              data-index={virtualRow.index}
              ref={virtualizer.measureElement}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              <MessageRow
                email={email}
                category={category}
                selected={selectedId === email.id}
                onSelect={onSelect}
                onToggleLater={onToggleLater}
                laterIds={laterIds}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
