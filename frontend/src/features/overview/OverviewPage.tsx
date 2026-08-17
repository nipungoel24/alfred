import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { briefing as fetchBriefing, regenerateBriefing, emails as fetchEmails, emailCounts } from '../../api/emails';
import { CheckSquare, Clock, Sparkles, ArrowUpRight, MessageSquareReply } from 'lucide-react';
import type { AppPage } from '../../layout/IconRail';

interface OverviewPageProps {
  onNavigate: (page: AppPage) => void;
}

export function OverviewPage({ onNavigate }: OverviewPageProps) {
  const queryClient = useQueryClient();
  const { data: brief } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });
  const { data: emailsList = [] } = useQuery({ queryKey: ['emails', { category: null, filter: 'overview' }], queryFn: () => fetchEmails({ limit: 200 }) });
  const { data: counts } = useQuery({ queryKey: ['emailCounts'], queryFn: emailCounts });

  const generateBriefing = useMutation({
    mutationFn: regenerateBriefing,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['briefing'] }),
  });

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const importantCount = brief?.high_priority_count ?? 0;
  const replyCount = brief?.needs_reply_count ?? 0;
  const deadlineCount = brief?.deadline_count ?? 0;
  const inboxTotal = counts?.active_inbox ?? emailsList.length;

  const attentionItems = brief?.top_attention_items?.length
    ? brief.top_attention_items.slice(0, 5)
    : emailsList
      .filter(e => e.analysis?.priority === 'urgent' || e.analysis?.priority === 'high')
      .slice(0, 5)
      .map(e => ({
        email_id: e.id,
        sender: e.sender_name || e.sender,
        subject: e.subject,
        priority: e.analysis!.priority,
        why_it_matters: e.analysis!.reason_for_priority,
        needs_reply: e.analysis!.needs_reply,
      }));

  return (
    <div className="page-scroll">
      <div style={{ maxWidth: 1080, margin: '0 auto', padding: 'var(--space-6) var(--space-6) var(--space-10)' }}>
        {/* Header */}
        <div className="reveal" style={{ ['--stagger' as string]: 0 }}>
          <h1 className="page-title" style={{ fontSize: 'var(--text-xl)' }}>{greeting}</h1>
          <p className="page-subtitle" style={{ marginBottom: 'var(--space-5)' }}>
            {inboxTotal} active inbox messages · {counts?.excluded ?? 0} excluded (spam/trash/archive)
          </p>
        </div>

        {/* Metrics — flat brutalist strip */}
        <div className="metrics-strip reveal" style={{ ['--stagger' as string]: 1, marginBottom: 'var(--space-6)' }}>
          <MetricCell value={inboxTotal} label="Inbox" onClick={() => onNavigate('mail')} />
          <MetricCell value={importantCount} label="Important" color="var(--warning)" onClick={() => onNavigate('mail')} />
          <MetricCell value={replyCount} label="Needs Reply" color="var(--accent)" onClick={() => onNavigate('mail')} />
          <MetricCell value={deadlineCount} label="Deadlines" color="var(--info)" onClick={() => onNavigate('deadlines')} />
        </div>

        <div className="overview-grid">
          {/* Left — attention */}
          <div className="overview-main">
            <div className="reveal" style={{ ['--stagger' as string]: 2 }}>
              <div className="section-label" style={{ marginBottom: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Sparkles size={12} aria-hidden="true" /> Needs Your Attention
              </div>
              {attentionItems.length ? (
                <div className="structured-list">
                  {attentionItems.map(item => (
                    <button
                      key={item.email_id}
                      type="button"
                      className="attention-item"
                      onClick={() => onNavigate('mail')}
                      aria-label={`${item.sender}: ${item.subject}`}
                    >
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
                          <span className={`badge badge-${item.priority}`}>{item.priority}</span>
                          {item.needs_reply && <span className="badge badge-reply">Reply</span>}
                        </div>
                        <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {item.subject}
                        </div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {item.sender} · {item.why_it_matters}
                        </div>
                      </div>
                      <ArrowUpRight size={14} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: 4 }} aria-hidden="true" />
                    </button>
                  ))}
                </div>
              ) : (
                <div className="empty-state" style={{ padding: 'var(--space-8)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                  <CheckSquare aria-hidden="true" />
                  <p>All clear — nothing urgent right now.</p>
                </div>
              )}
            </div>

            {/* Briefing */}
            {brief?.executive_summary && (
              <div className="reveal" style={{ ['--stagger' as string]: 3, marginTop: 'var(--space-6)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
                  <div className="section-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <MessageSquareReply size={12} aria-hidden="true" /> Alfred Briefing
                  </div>
                  <button
                    type="button"
                    className="btn btn-surface btn-sm"
                    onClick={() => generateBriefing.mutate()}
                    disabled={generateBriefing.isPending}
                  >
                    {generateBriefing.isPending ? <span className="btn-spinner" aria-hidden="true" /> : <Sparkles size={13} aria-hidden="true" />}
                    {generateBriefing.isPending ? 'Generating…' : 'Refresh'}
                  </button>
                </div>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)' }}>
                  {brief.executive_summary}
                </p>
              </div>
            )}
          </div>

          {/* Right — deadlines */}
          <aside className="overview-aside">
            <div className="reveal" style={{ ['--stagger' as string]: 2 }}>
              <div className="section-label" style={{ marginBottom: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Clock size={12} aria-hidden="true" /> Upcoming Deadlines
              </div>
              {brief?.deadlines?.length ? (
                <div className="structured-list">
                  {brief.deadlines.map((item, idx) => (
                    <div key={idx} className="list-row">
                      <span className="deadline-dot" aria-hidden="true" />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {item.subject}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                          {item.sender}
                          {item.deadline ? ` · ${item.deadline}` : ''}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state" style={{ padding: 'var(--space-6)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                  <Clock aria-hidden="true" />
                  <p>No upcoming deadlines.</p>
                </div>
              )}
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

function MetricCell({ value, label, color, onClick }: {
  value: number; label: string; color?: string; onClick?: () => void;
}) {
  const interactive = Boolean(onClick);
  const inner = (
    <>
      <div className="metric-value" style={color ? { color } : undefined}>{value}</div>
      <div className="metric-label">{label}</div>
    </>
  );
  return interactive ? (
    <button type="button" className="metric-cell" onClick={onClick} aria-label={`${label}: ${value}`}>
      {inner}
    </button>
  ) : (
    <div className="metric-cell">{inner}</div>
  );
}
