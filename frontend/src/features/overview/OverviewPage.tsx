import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { briefing as fetchBriefing, emails as fetchEmails, regenerateBriefing } from '../../api/emails';
import { CheckSquare, Clock, Sparkles } from 'lucide-react';

interface OverviewPageProps {
  onNavigate: (page: 'inbox' | 'important' | 'reply' | 'tasks' | 'deadlines') => void;
}

export function OverviewPage({ onNavigate }: OverviewPageProps) {
  const queryClient = useQueryClient();
  const { data: brief, isLoading } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });
  const { data: emailsList = [] } = useQuery({ queryKey: ['emails', {}], queryFn: () => fetchEmails() });

  const generateBriefing = useMutation({
    mutationFn: regenerateBriefing,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['briefing'] }),
  });

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const importantCount = brief?.high_priority_count ?? 0;
  const replyCount = brief?.needs_reply_count ?? 0;
  const deadlineCount = brief?.deadline_count ?? 0;
  const totalEmails = brief?.total_emails ?? emailsList.length;
  const attentionItems = brief?.top_attention_items?.length
    ? brief.top_attention_items
    : emailsList
      .filter((email) => email.analysis?.priority === 'urgent' || email.analysis?.priority === 'high')
      .slice(0, 3)
      .map((email) => ({
        email_id: email.id,
        sender: email.sender_name || email.sender,
        subject: email.subject,
        priority: email.analysis!.priority,
        why_it_matters: email.analysis!.reason_for_priority,
        needs_reply: email.analysis!.needs_reply,
      }));

  // Loading skeleton
  if (isLoading) {
    return (
      <div style={{ padding: 'var(--space-6)' }}>
        <div className="skeleton" style={{ width: 280, height: 28, marginBottom: 8 }} />
        <div className="skeleton" style={{ width: 200, height: 16, marginBottom: 32 }} />
        <div className="metrics-strip">
          {[1,2,3,4].map(i => <div key={i} className="skeleton" style={{ height: 80 }} />)}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div className="page-header" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <div>
            <h1 className="greeting">{greeting}</h1>
            <p className="greeting-sub">Here's what needs your attention.</p>
          </div>
          <button
            className="btn btn-surface"
            onClick={() => generateBriefing.mutate()}
            disabled={generateBriefing.isPending}
          >
            <Sparkles size={14} />
            {generateBriefing.isPending ? 'Generating...' : 'Refresh Briefing'}
          </button>
        </div>
      </div>

      {/* Metrics */}
      <div style={{ padding: '0 var(--space-6)', marginBottom: 'var(--space-5)' }}>
        <div className="metrics-strip">
          <MetricCard value={totalEmails} label="Analyzed" />
          <MetricCard value={importantCount} label="Important" color="var(--warning)" onClick={() => onNavigate('important')} />
          <MetricCard value={replyCount} label="Needs Reply" color="var(--accent)" onClick={() => onNavigate('reply')} />
          <MetricCard value={deadlineCount} label="Deadlines" color="var(--info)" onClick={() => onNavigate('deadlines')} />
        </div>
      </div>

      {/* Content grid */}
      <div className="overview-grid" style={{ padding: '0 var(--space-6)', paddingBottom: 'var(--space-6)' }}>
        {/* Left — attention items */}
        <div className="overview-main">
          <div className="detail-section-title" style={{ marginBottom: 'var(--space-3)' }}>Needs Your Attention</div>
          {attentionItems.length ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {attentionItems.map((item, idx) => (
                <div key={idx} className="attention-item">
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 2 }}>
                      <span className={`badge badge-${item.priority}`}>{item.priority}</span>
                      {item.needs_reply && <span className="badge badge-reply">Reply</span>}
                    </div>
                    <div style={{ fontWeight: 500, fontSize: 'var(--text-sm)', marginBottom: 2 }}>{item.subject}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                      {item.sender} · {item.why_it_matters}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: 'var(--space-8)' }}>
              <CheckSquare />
              <p>All clear — nothing urgent right now.</p>
            </div>
          )}

          {/* Briefing */}
          {brief?.executive_summary && (
            <div className="briefing-box">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
                <Sparkles size={14} style={{ color: 'var(--accent-text)' }} />
                <span className="detail-section-title" style={{ margin: 0 }}>Alfred Briefing</span>
              </div>
              <p className="briefing-text">{brief.executive_summary}</p>
            </div>
          )}
        </div>

        {/* Right — deadlines */}
        <div className="overview-aside">
          <div className="detail-section-title" style={{ marginBottom: 'var(--space-3)' }}>Upcoming Deadlines</div>
          {brief?.deadlines?.length ? (
            <div className="glass-panel" style={{ overflow: 'hidden' }}>
              {brief.deadlines.map((item, idx) => (
                <div key={idx} className="deadline-item">
                  <span className="deadline-dot" />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, fontSize: 'var(--text-sm)' }}>{item.subject}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {item.sender}{item.deadline ? ` · ${item.deadline}` : ''}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: 'var(--space-6)' }}>
              <Clock />
              <p>No upcoming deadlines.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ value, label, color, onClick }: {
  value: number; label: string; color?: string; onClick?: () => void;
}) {
  return (
    <div
      className="metric-card"
      style={{ cursor: onClick ? 'pointer' : undefined }}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="metric-value" style={color ? { color } : undefined}>{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}
