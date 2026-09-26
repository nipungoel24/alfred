import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { briefing as fetchBriefing } from '../../api/emails';
import { Mail } from 'lucide-react';
import { SourceEmailPreview } from '../../mail/SourceEmailPreview';
import { EmptyState, ErrorState } from '../../components/ui/States';
import { useRetryPreservingFocus } from '../../lib/focus';

interface DeadlinesPageProps {
  onOpenInMail?: (emailId: string) => void;
}

export function DeadlinesPage({ onOpenInMail }: DeadlinesPageProps) {
  const {
    data: brief,
    isLoading,
    isError,
    isFetching,
    refetch,
  } = useQuery({ queryKey: ['briefing'], queryFn: fetchBriefing });
  // A successful retry unmounts the button that had focus, so the view heading
  // takes it. On a persistent failure the error stays put and focus does not move.
  const retry = useRetryPreservingFocus(refetch);
  const [previewEmailId, setPreviewEmailId] = useState<string | null>(null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-head">
        <div>
          <h1 className="page-title">Deadlines</h1>
          <div className="page-subtitle">
            {isError ? 'Runtime information unavailable' : `${brief?.deadlines?.length ?? 0} upcoming`}
          </div>
        </div>
      </div>

      {/* A failed request must never be reported as "you have no deadlines".
          That is the one answer a user would act on and be wrong about. */}
      {isError ? (
        <ErrorState
          title="Deadlines couldn't load"
          body="Alfred could not read your briefing. This is a connection problem, not an empty result — your deadlines are unaffected."
          onRetry={retry}
          retrying={isFetching}
        />
      ) : isLoading ? (
        <div style={{ padding: 'var(--space-4) var(--space-6)' }} aria-busy="true">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton-row">
              <div className="skeleton skeleton-line-md skeleton-w-55" />
              <div className="skeleton skeleton-line-sm skeleton-w-40" />
            </div>
          ))}
        </div>
      ) : !brief?.deadlines?.length ? (
        <EmptyState
          title="No upcoming deadlines"
          body="Alfred has not found a dated commitment in your synced mail."
        />
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
                {item.email_id && (
                  <button
                    type="button"
                    className="icon-btn"
                    onClick={() => setPreviewEmailId(item.email_id)}
                    aria-label={`View source email for ${item.subject}`}
                    title="View email"
                  >
                    <Mail size={14} aria-hidden="true" />
                    <span className="btn-label">View email</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <SourceEmailPreview
        emailId={previewEmailId}
        onClose={() => setPreviewEmailId(null)}
        onOpenInMail={onOpenInMail}
      />
    </div>
  );
}
