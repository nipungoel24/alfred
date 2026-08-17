import { useQuery } from '@tanstack/react-query';
import { briefing as fetchBriefing } from '../../api/emails';
import { Clock } from 'lucide-react';

export function DeadlinesPage() {
  const { data: brief, isLoading } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-head">
        <div>
          <h1 className="page-title">Deadlines</h1>
          <div className="page-subtitle">{brief?.deadlines?.length ?? 0} upcoming</div>
        </div>
      </div>

      {isLoading ? (
        <div style={{ padding: 'var(--space-4) var(--space-6)' }} aria-busy="true">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton-row">
              <div className="skeleton" style={{ width: '55%', height: 13 }} />
              <div className="skeleton" style={{ width: '35%', height: 11 }} />
            </div>
          ))}
        </div>
      ) : !brief?.deadlines?.length ? (
        <div className="empty-state">
          <Clock aria-hidden="true" />
          <p>No upcoming deadlines detected.</p>
        </div>
      ) : (
        <div style={{ flex: 1, overflowY: 'auto', minHeight: 0, padding: 'var(--space-4) var(--space-6)' }}>
          <div className="structured-list">
            {brief.deadlines.map((item, idx) => (
              <div key={idx} className="list-row">
                <span className="deadline-dot" aria-hidden="true" />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{item.subject}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                    {item.sender}{item.why_it_matters ? ` · ${item.why_it_matters}` : ''}
                  </div>
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--accent-text)', fontWeight: 700, flexShrink: 0 }}>
                  {item.deadline || ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
