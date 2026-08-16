import { useQuery } from '@tanstack/react-query';
import { briefing as fetchBriefing } from '../../api/emails';
import { Clock } from 'lucide-react';

export function DeadlinesPage() {
  const { data: brief, isLoading } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });

  if (isLoading) {
    return (
      <div style={{ padding: 'var(--space-6)' }}>
        <div className="skeleton" style={{ width: 140, height: 22, marginBottom: 'var(--space-6)' }} />
        {[...Array(4)].map((_, i) => (
          <div key={i} style={{ display: 'flex', gap: 'var(--space-3)', padding: '12px 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <div className="skeleton" style={{ width: 8, height: 8, borderRadius: '50%' }} />
            <div className="skeleton" style={{ flex: 1, height: 14 }} />
          </div>
        ))}
      </div>
    );
  }

  const deadlines = brief?.deadlines ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Deadlines</h1>
          <div className="page-subtitle">{deadlines.length} upcoming</div>
        </div>
      </div>

      {deadlines.length === 0 ? (
        <div className="empty-state">
          <Clock />
          <p>No upcoming deadlines detected.</p>
        </div>
      ) : (
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 var(--space-6)' }}>
          {deadlines.map((item, idx) => (
            <div key={idx} className="deadline-item">
              <span className="deadline-dot" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 500, fontSize: 'var(--text-sm)' }}>{item.subject}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {item.sender}{item.why_it_matters ? ` · ${item.why_it_matters}` : ''}
                </div>
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--accent-text)', fontWeight: 600, flexShrink: 0 }}>
                {item.deadline || ''}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
