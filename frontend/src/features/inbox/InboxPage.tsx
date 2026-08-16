import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';
import { emails as fetchEmails, Email } from '../../api/emails';
import { PriorityBadge } from '../../components/PriorityBadge';
import { EmailDetail } from '../email/EmailDetail';

interface InboxPageProps {
  priorityFilter?: string;
  needsReplyFilter?: boolean;
}

export function InboxPage({ priorityFilter = '', needsReplyFilter = null }: InboxPageProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeAccount, setActiveAccount] = useState('all');
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  const { data: emails = [], isLoading } = useQuery({
    queryKey: ['emails', { searchQuery, priorityFilter, needsReplyFilter, activeAccount }],
    queryFn: () => fetchEmails(searchQuery, priorityFilter, needsReplyFilter, activeAccount === 'all' ? '' : activeAccount),
  });

  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: emails.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // Estimated height of a row
    overscan: 5,
  });

  return (
    <div className="flex h-full relative">
      <div className="flex-1 flex flex-col h-full border-r border-[#2d2d30]">
        <div className="p-4 border-b border-[#2d2d30] flex gap-4 bg-[#1e1e1e] z-10 sticky top-0">
          <input
            type="text"
            className="input flex-1"
            placeholder="Search emails..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {/* We could add account dropdown here if needed */}
        </div>
        
        {isLoading ? (
          <div className="p-8 text-center text-muted">Loading emails...</div>
        ) : emails.length === 0 ? (
          <div className="p-8 text-center text-muted">No emails found.</div>
        ) : (
          <div ref={parentRef} className="flex-1 overflow-auto">
            <div
              style={{
                height: `${rowVirtualizer.getTotalSize()}px`,
                width: '100%',
                position: 'relative',
              }}
            >
              {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                const email = emails[virtualRow.index];
                const isSelected = selectedEmailId === email.id;
                return (
                  <div
                    key={virtualRow.index}
                    data-index={virtualRow.index}
                    ref={rowVirtualizer.measureElement}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                    className={`p-4 border-b border-[#2d2d30] cursor-pointer hover:bg-[#2d2d30] transition-colors ${isSelected ? 'bg-[#2d2d30]' : ''}`}
                    onClick={() => setSelectedEmailId(email.id)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="font-semibold">{email.sender_name || email.sender}</div>
                      <div className="text-xs text-muted">
                        {email.received_at ? new Date(email.received_at).toLocaleDateString() : ''}
                      </div>
                    </div>
                    <div className="text-sm font-medium mb-1 truncate">{email.subject}</div>
                    <div className="text-sm text-muted line-clamp-2 mb-2">{email.body}</div>
                    
                    {email.analysis ? (
                      <div className="flex items-center gap-2 mt-2">
                        <PriorityBadge priority={email.analysis.priority} />
                        {email.analysis.needs_reply && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-primary/20 text-primary">Needs Reply</span>
                        )}
                      </div>
                    ) : (
                      <div className="text-xs text-muted flex items-center gap-1 mt-2">
                        <span className="w-2 h-2 rounded-full border-2 border-muted border-t-transparent animate-spin inline-block"></span>
                        Analyzing...
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {selectedEmailId && (
        <div className="w-1/2 h-full bg-[#1e1e1e] border-l border-[#2d2d30] overflow-auto">
          <EmailDetail 
            emailId={selectedEmailId} 
            onClose={() => setSelectedEmailId(null)} 
          />
        </div>
      )}
    </div>
  );
}
