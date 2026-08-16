import { useQuery, useMutation } from '@tanstack/react-query';
import { emailDetails, draft as generateDraft } from '../../api/emails';
import { X, Sparkles, Clock, ArrowUpRight, CheckCircle2 } from 'lucide-react';

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
    return (
      <div className="detail-panel">
        <div className="detail-header">
          <div className="skeleton" style={{ width: 200, height: 18 }} />
          <button className="icon-btn" onClick={onClose}><X size={16} /></button>
        </div>
        <div className="detail-body">
          <div className="skeleton" style={{ width: '100%', height: 120, marginBottom: 16 }} />
          <div className="skeleton" style={{ width: '60%', height: 14, marginBottom: 8 }} />
          <div className="skeleton" style={{ width: '80%', height: 14 }} />
        </div>
      </div>
    );
  }

  if (!email) {
    return (
      <div className="detail-panel">
        <div className="detail-header">
          <span style={{ color: 'var(--danger)' }}>Email not found</span>
          <button className="icon-btn" onClick={onClose}><X size={16} /></button>
        </div>
      </div>
    );
  }

  const analysis = email.analysis;

  return (
    <div className="detail-panel">
      {/* Header */}
      <div className="detail-header">
        <h2 style={{ fontSize: 'var(--text-md)', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', paddingRight: 'var(--space-4)' }}>
          {email.subject}
        </h2>
        <button className="icon-btn" onClick={onClose} aria-label="Close"><X size={16} /></button>
      </div>

      {/* Body */}
      <div className="detail-body">
        {/* Sender info */}
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <div style={{ fontWeight: 600, fontSize: 'var(--text-md)' }}>{email.sender_name || email.sender}</div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
            &lt;{email.sender}&gt; · {email.received_at ? new Date(email.received_at).toLocaleString() : ''}
          </div>
        </div>

        {/* Email body */}
        <div style={{
          background: 'var(--bg-input)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-4)',
          fontSize: 'var(--text-sm)',
          lineHeight: 'var(--leading-relaxed)',
          color: 'var(--text-secondary)',
          whiteSpace: 'pre-wrap',
          maxHeight: 280,
          overflowY: 'auto',
          marginBottom: 'var(--space-5)',
        }}>
          {email.body}
        </div>

        {/* AI Analysis */}
        {analysis ? (
          <div>
            <div className="detail-section-title" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Sparkles size={12} style={{ color: 'var(--accent-text)' }} />
              Alfred Intelligence
            </div>

            <div className="intelligence-panel">
              {/* Summary */}
              <div style={{ padding: 'var(--space-2) 0', marginBottom: 'var(--space-2)' }}>
                <div style={{ fontWeight: 500, fontSize: 'var(--text-md)', marginBottom: 4 }}>{analysis.short_summary}</div>
                {analysis.reason_for_priority && (
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>{analysis.reason_for_priority}</div>
                )}
              </div>

              {/* Meta row */}
              <div className="intelligence-row">
                <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>Priority</span>
                <span className={`badge badge-${analysis.priority}`}>{analysis.priority}</span>
              </div>

              {analysis.needs_reply && (
                <div className="intelligence-row">
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>Needs Reply</span>
                  <span className="badge badge-reply">Yes</span>
                </div>
              )}

              {analysis.priority_score > 0 && (
                <div className="intelligence-row">
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>Score</span>
                  <span style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}>{analysis.priority_score}/100</span>
                </div>
              )}
            </div>

            {/* Action items */}
            {analysis.action_items?.length > 0 && (
              <div style={{ marginTop: 'var(--space-4)' }}>
                <div className="detail-section-title">
                  <ArrowUpRight size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
                  Action Items
                </div>
                {analysis.action_items.map((item, idx) => (
                  <div key={idx} style={{
                    display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)',
                    padding: 'var(--space-2) 0', borderBottom: '1px solid var(--border-subtle)',
                    fontSize: 'var(--text-sm)',
                  }}>
                    <CheckCircle2 size={14} style={{ color: 'var(--accent)', marginTop: 2, flexShrink: 0 }} />
                    <div style={{ flex: 1 }}>
                      <div>{item.description}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', gap: 'var(--space-2)' }}>
                        {item.owner && <span>Owner: {item.owner}</span>}
                        {item.deadline && <span style={{ color: 'var(--accent-text)' }}>Due: {item.deadline}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Deadlines */}
            {analysis.deadlines?.length > 0 && (
              <div style={{ marginTop: 'var(--space-4)' }}>
                <div className="detail-section-title">
                  <Clock size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
                  Deadlines
                </div>
                {analysis.deadlines.map((item, idx) => (
                  <div key={idx} className="deadline-item" style={{ paddingLeft: 0 }}>
                    <span className="deadline-dot" />
                    <span style={{ flex: 1 }}>{item.description}</span>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--accent-text)', fontWeight: 600 }}>{item.due_at}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Draft button */}
            {analysis.needs_reply && (
              <div style={{ marginTop: 'var(--space-5)', paddingTop: 'var(--space-4)', borderTop: '1px solid var(--border-subtle)' }}>
                <button
                  className="btn btn-primary"
                  style={{ width: '100%' }}
                  onClick={() => draftMutation.mutate()}
                  disabled={draftMutation.isPending}
                >
                  <Sparkles size={14} />
                  {draftMutation.isPending ? 'Generating Draft...' : 'Generate Reply Draft'}
                </button>

                {draftMutation.isError && (
                  <div className="banner banner-danger" style={{ marginTop: 'var(--space-3)' }}>
                    Failed to generate draft. Is Ollama running?
                  </div>
                )}

                {draftMutation.isSuccess && (
                  <div style={{ marginTop: 'var(--space-4)' }}>
                    <div className="detail-section-title">Draft Reply</div>
                    <div style={{
                      background: 'var(--bg-input)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      padding: 'var(--space-4)',
                      fontSize: 'var(--text-sm)',
                      lineHeight: 'var(--leading-relaxed)',
                      whiteSpace: 'pre-wrap',
                    }}>
                      {draftMutation.data.draft}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-6)' }}>
            <Sparkles />
            <p>Analysis pending...</p>
          </div>
        )}
      </div>
    </div>
  );
}
