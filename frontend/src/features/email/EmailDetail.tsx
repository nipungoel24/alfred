import { useQuery, useMutation } from '@tanstack/react-query';
import { emailDetails, draft as generateDraft } from '../../api/emails';
import { PriorityBadge } from '../../components/PriorityBadge';

interface EmailDetailProps {
  emailId: string;
  onClose: () => void;
}

export function EmailDetail({ emailId, onClose }: EmailDetailProps) {
  const { data: email, isLoading } = useQuery({
    queryKey: ['email', emailId],
    queryFn: () => emailDetails(emailId),
  });

  const draftMutation = useMutation({
    mutationFn: () => generateDraft(emailId),
  });

  if (isLoading) {
    return <div className="p-8 text-center text-muted">Loading email details...</div>;
  }

  if (!email) {
    return <div className="p-8 text-center text-danger">Email not found</div>;
  }

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e]">
      <div className="p-4 border-b border-[#2d2d30] flex justify-between items-center sticky top-0 bg-[#1e1e1e] z-10">
        <h2 className="text-lg font-semibold truncate pr-4">{email.subject}</h2>
        <button className="text-muted hover:text-white" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 pb-6 border-b border-[#2d2d30]">
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="font-semibold text-lg">{email.sender_name || email.sender}</div>
              <div className="text-muted text-sm">&lt;{email.sender}&gt;</div>
            </div>
            <div className="text-muted text-sm">
              {email.received_at ? new Date(email.received_at).toLocaleString() : ''}
            </div>
          </div>
          
          <div className="bg-[#121214] p-4 rounded-lg whitespace-pre-wrap font-sans text-[15px] leading-relaxed border border-[#2d2d30]">
            {email.body}
          </div>
        </div>

        {email.analysis ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm uppercase tracking-wider text-muted mb-3 font-semibold">AI Analysis</h3>
              <div className="panel p-5 bg-[#252526] border-l-4 border-primary rounded-l-none">
                <div className="flex items-center gap-3 mb-3">
                  <PriorityBadge priority={email.analysis.priority} />
                  {email.analysis.needs_reply && (
                    <span className="px-2 py-1 rounded text-xs font-bold uppercase tracking-wider bg-primary/20 text-primary">Needs Reply</span>
                  )}
                  <span className="text-xs text-muted ml-auto bg-[#1e1e1e] px-2 py-1 rounded">
                    Score: {email.analysis.priority_score}
                  </span>
                </div>
                <p className="font-medium text-lg mb-2">{email.analysis.short_summary}</p>
                <p className="text-muted text-sm">{email.analysis.reason_for_priority}</p>
              </div>
            </div>
            
            {email.analysis.action_items && email.analysis.action_items.length > 0 && (
              <div>
                <h4 className="text-sm uppercase tracking-wider text-muted mb-3 font-semibold">Action Items</h4>
                <ul className="space-y-2">
                  {email.analysis.action_items.map((item, idx) => (
                    <li key={idx} className="bg-[#2d2d30] p-3 rounded text-sm">
                      <div className="flex justify-between items-start">
                        <span>{item.description}</span>
                        {item.deadline && <span className="text-purple ml-2 flex-shrink-0 text-xs px-2 py-1 bg-purple/10 rounded">{item.deadline}</span>}
                      </div>
                      {item.owner && <div className="text-xs text-muted mt-1">Owner: {item.owner}</div>}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {email.analysis.deadlines && email.analysis.deadlines.length > 0 && (
              <div>
                <h4 className="text-sm uppercase tracking-wider text-muted mb-3 font-semibold">Deadlines</h4>
                <ul className="space-y-2">
                  {email.analysis.deadlines.map((item, idx) => (
                    <li key={idx} className="bg-[#2d2d30] border-l-2 border-purple p-3 rounded text-sm flex justify-between">
                      <span>{item.description}</span>
                      <span className="text-purple font-semibold">{item.due_at}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {email.analysis.needs_reply && (
              <div className="mt-8 pt-6 border-t border-[#2d2d30]">
                <button 
                  className="btn btn-primary w-full py-3 text-lg"
                  onClick={() => draftMutation.mutate()}
                  disabled={draftMutation.isPending}
                >
                  {draftMutation.isPending ? 'Generating Draft...' : 'Generate Reply Draft'}
                </button>
                
                {draftMutation.isError && (
                  <div className="mt-3 text-danger text-center">Failed to generate draft.</div>
                )}
                
                {draftMutation.isSuccess && (
                  <div className="mt-4">
                    <h4 className="text-sm uppercase tracking-wider text-muted mb-2 font-semibold">Draft Output</h4>
                    <div className="bg-[#121214] p-4 rounded border border-[#2d2d30] whitespace-pre-wrap font-sans">
                      {draftMutation.data.draft}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center text-muted border border-dashed border-[#2d2d30] rounded">
            Analysis pending...
          </div>
        )}
      </div>
    </div>
  );
}
