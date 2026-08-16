import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { briefing, Briefing } from '../../api/emails';
import { PriorityBadge } from '../../components/PriorityBadge';

export function OverviewPage() {
  const queryClient = useQueryClient();
  const { data: brief, isLoading, error } = useQuery({
    queryKey: ['briefing'],
    queryFn: briefing,
  });

  const generateBriefing = useMutation({
    mutationFn: () => fetch('http://127.0.0.1:8765/api/briefing/generate', { method: 'POST' }).then(r => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['briefing'] });
    }
  });

  if (isLoading) return <div>Loading briefing...</div>;
  if (error) return <div className="text-danger">Error loading briefing.</div>;

  return (
    <div className="content p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1>Overview</h1>
        <button className="btn btn-primary" onClick={() => generateBriefing.mutate()} disabled={generateBriefing.isPending}>
          {generateBriefing.isPending ? 'Generating...' : 'Refresh Briefing'}
        </button>
      </div>

      {!brief ? (
        <div className="panel p-8 text-center text-muted">
          No briefing available yet.
        </div>
      ) : (
        <div className="briefing-container">
          <div className="panel p-6 mb-6">
            <h2 className="mb-4">Executive Summary</h2>
            <p className="text-lg leading-relaxed">{brief.executive_summary}</p>
          </div>

          <div className="stats-grid mb-8">
            <div className="stat-box">
              <div className="stat-value">{brief.total_emails}</div>
              <div className="stat-label">Total Analyzed</div>
            </div>
            <div className="stat-box">
              <div className="stat-value text-danger">{brief.urgent_count}</div>
              <div className="stat-label">Urgent</div>
            </div>
            <div className="stat-box">
              <div className="stat-value text-warning">{brief.high_priority_count}</div>
              <div className="stat-label">High Priority</div>
            </div>
            <div className="stat-box">
              <div className="stat-value text-primary">{brief.needs_reply_count}</div>
              <div className="stat-label">Needs Reply</div>
            </div>
            <div className="stat-box">
              <div className="stat-value text-purple">{brief.deadline_count}</div>
              <div className="stat-label">Deadlines</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="panel p-6">
              <h3 className="mb-4 text-warning">Top Attention Items</h3>
              {brief.top_attention_items?.length === 0 ? (
                <p className="text-muted">No high priority items right now.</p>
              ) : (
                <ul className="space-y-4">
                  {brief.top_attention_items?.map((item, idx) => (
                    <li key={idx} className="border-l-4 border-warning pl-4 py-1">
                      <div className="flex justify-between">
                        <strong>{item.sender}</strong>
                        <PriorityBadge priority={item.priority} />
                      </div>
                      <div className="text-sm text-muted mb-1">{item.subject}</div>
                      <div className="text-sm">{item.why_it_matters}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="panel p-6">
              <h3 className="mb-4 text-purple">Upcoming Deadlines</h3>
              {brief.deadlines?.length === 0 ? (
                <p className="text-muted">No upcoming deadlines detected.</p>
              ) : (
                <ul className="space-y-4">
                  {brief.deadlines?.map((item, idx) => (
                    <li key={idx} className="border-l-4 border-purple pl-4 py-1">
                      <div className="flex justify-between">
                        <strong>{item.sender}</strong>
                        <span className="text-purple font-semibold">{item.deadline}</span>
                      </div>
                      <div className="text-sm text-muted mb-1">{item.subject}</div>
                      <div className="text-sm">{item.why_it_matters}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
