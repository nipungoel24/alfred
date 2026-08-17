import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  briefing as fetchBriefing, regenerateBriefing, emails as fetchEmails, emailCounts,
} from '../../api/emails';
import { CheckSquare, Clock, Sparkles, ArrowUpRight } from 'lucide-react';
import type { AppPage } from '../../layout/IconRail';

interface OverviewPageProps {
  onNavigate: (page: AppPage) => void;
}

export function OverviewPage({ onNavigate }: OverviewPageProps) {
  const queryClient = useQueryClient();
  const { data: brief } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });
  const { data: emailsList = [] } = useQuery({
    queryKey: ['emails', { scope: 'overview' }],
    queryFn: () => fetchEmails({ limit: 200 }),
  });
  const { data: counts } = useQuery({ queryKey: ['emailCounts'], queryFn: emailCounts });

  const generateBriefing = useMutation({
    mutationFn: regenerateBriefing,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['briefing'] }),
  });

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const inboxCount = counts?.active_inbox ?? emailsList.length;
  const allMailCount = counts?.all_mail ?? inboxCount;

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
      <div className="overview-inner">
        {/* Editorial header */}
        <header className="reveal" style={{ ['--stagger' as string]: 0 }}>
          <h1 className="overview-greeting">{greeting}</h1>
          <p className="overview-subline">
            {inboxCount} messages in Inbox{allMailCount > inboxCount ? ` · ${allMailCount} in All Mail` : ''}
          </p>
        </header>

        {/* Flat metric strip — premium glass tiles */}
        <div className="metrics-strip-flat reveal" style={{ ['--stagger' as string]: 1 }}>
          <Metric value={brief?.high_priority_count ?? 0} label="Important" onClick={() => onNavigate('mail')} />
          <Metric value={brief?.needs_reply_count ?? 0} label="Needs Reply" accent onClick={() => onNavigate('mail')} />
          <Metric value={brief?.deadline_count ?? 0} label="Deadlines" onClick={() => onNavigate('deadlines')} />
          <Metric value={inboxCount} label="Inbox" onClick={() => onNavigate('mail')} />
        </div>

        <div className="overview-columns">
          {/* Left column */}
          <div className="overview-main">
            <section className="overview-section reveal" style={{ ['--stagger' as string]: 2 }}>
              <div className="overview-section-head">
                <span className="section-label">Needs attention</span>
                {attentionItems.length > 0 && (
                  <button type="button" className="overview-link" onClick={() => onNavigate('mail')}>
                    Open mail <ArrowUpRight size={12} aria-hidden="true" />
                  </button>
                )}
              </div>
              {attentionItems.length ? (
                <div className="overview-panel">
                  <div className="overview-rows">
                    {attentionItems.map(item => (
                      <button
                        key={item.email_id}
                        type="button"
                        className="overview-row"
                        onClick={() => onNavigate('mail')}
                        aria-label={`${item.sender}: ${item.subject}`}
                      >
                        <span className="overview-row-main">
                          <span className="overview-row-title">{item.subject}</span>
                          <span className="overview-row-meta">
                            {item.sender}
                            {item.why_it_matters ? ` · ${item.why_it_matters}` : ''}
                          </span>
                        </span>
                        <span className="overview-row-side">
                          <span className={`badge badge-${item.priority}`}>{item.priority}</span>
                          {item.needs_reply && <span className="badge badge-reply">Reply</span>}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="overview-panel">
                  <p className="overview-empty"><CheckSquare size={15} aria-hidden="true" /> All clear — nothing urgent right now.</p>
                </div>
              )}
            </section>

            {brief?.executive_summary && (
              <section className="overview-section reveal" style={{ ['--stagger' as string]: 3 }}>
                <div className="overview-section-head">
                  <span className="section-label">Alfred briefing</span>
                  <button
                    type="button"
                    className="overview-link"
                    onClick={() => generateBriefing.mutate()}
                    disabled={generateBriefing.isPending}
                  >
                    {generateBriefing.isPending ? <span className="btn-spinner" aria-hidden="true" /> : <Sparkles size={12} aria-hidden="true" />}
                    {generateBriefing.isPending ? 'Generating…' : 'Refresh'}
                  </button>
                </div>
                <div className="accent-wash overview-briefing-panel">
                  <p className="overview-briefing">{brief.executive_summary}</p>
                </div>
              </section>
            )}
          </div>

          {/* Right column — upcoming */}
          <aside className="overview-aside">
            <section className="overview-section reveal" style={{ ['--stagger' as string]: 2 }}>
              <div className="overview-section-head">
                <span className="section-label">Upcoming</span>
                {brief?.deadlines?.length ? (
                  <button type="button" className="overview-link" onClick={() => onNavigate('deadlines')}>
                    All deadlines <ArrowUpRight size={12} aria-hidden="true" />
                  </button>
                ) : null}
              </div>
              {brief?.deadlines?.length ? (
                <div className="overview-panel">
                  <div className="overview-rows">
                    {brief.deadlines.slice(0, 6).map((item, idx) => (
                      <div key={idx} className="overview-row overview-row-static">
                        <span className="overview-row-main">
                          <span className="overview-row-title">{item.subject}</span>
                          <span className="overview-row-meta">{item.sender}</span>
                        </span>
                        <span className="overview-row-side">
                          <span className="overview-due">{item.deadline}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="overview-panel">
                  <p className="overview-empty"><Clock size={15} aria-hidden="true" /> No upcoming deadlines.</p>
                </div>
              )}
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}

function Metric({ value, label, accent, onClick }: {
  value: number; label: string; accent?: boolean; onClick: () => void;
}) {
  return (
    <button type="button" className="metric-cell" onClick={onClick} aria-label={`${label}: ${value}`}>
      <div className="metric-value" style={accent ? { color: 'var(--accent)' } : undefined}>{value}</div>
      <div className="metric-label">{label}</div>
    </button>
  );
}
