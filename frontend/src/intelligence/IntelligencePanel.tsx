import { useMemo } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Sparkles, AlertTriangle, Clock, ArrowUpRight, PenLine, Zap, X,
} from 'lucide-react';
import { draft as generateDraft } from '../api/emails';
import type { Email } from '../api/emails';

interface IntelligencePanelProps {
  email: Email;
  onClose?: () => void;
}

export function IntelligencePanel({ email, onClose }: IntelligencePanelProps) {
  const queryClient = useQueryClient();
  const analysis = email.analysis;

  const draftMutation = useMutation({
    mutationFn: () => generateDraft(email.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email', email.id] });
    },
  });

  const sections = useMemo(() => ({
    summary: Boolean(analysis?.short_summary),
    why: Boolean(analysis?.reason_for_priority),
    actions: Boolean(analysis?.action_items?.length),
    deadlines: Boolean(analysis?.deadlines?.length),
  }), [analysis]);

  const isEmpty = !analysis || (!sections.summary && !sections.why && !sections.actions && !sections.deadlines);

  return (
    <aside className="intelligence-pane" aria-label="Alfred intelligence">
      <div className="intel-head">
        <span className="intel-title">
          <Sparkles aria-hidden="true" />
          Alfred Intelligence
        </span>
        {onClose && (
          <button type="button" className="icon-btn outlined" onClick={onClose} aria-label="Close intelligence panel">
            <X size={14} aria-hidden="true" />
          </button>
        )}
      </div>

      <div className="intel-scroll">
        {isEmpty ? (
          <div className="intel-pending">
            <span className="btn-spinner" aria-hidden="true" />
            <p>Analysis pending for this message.</p>
            <p className="text-muted">Alfred analyzes inbox mail in the background. Priority mail is analyzed first.</p>
          </div>
        ) : (
          <>
            {sections.summary && (
              <section className="intel-section reveal" style={{ ['--stagger' as string]: 0 }}>
                <div className="intel-section-label"><Zap aria-hidden="true" /> Summary</div>
                <p className="intel-summary">{analysis?.short_summary}</p>
              </section>
            )}

            {sections.why && (
              <section className="intel-section reveal" style={{ ['--stagger' as string]: 1 }}>
                <div className="intel-section-label"><Sparkles aria-hidden="true" /> Why it matters</div>
                <p className="intel-why">{analysis?.reason_for_priority}</p>
              </section>
            )}

            <section className="intel-section reveal" style={{ ['--stagger' as string]: 2 }}>
              <div className="intel-section-label"><AlertTriangle aria-hidden="true" /> Priority</div>
              <div className="intel-kv">
                <span className="kv-key">Level</span>
                <span className={`badge badge-${analysis?.priority ?? 'low'}`}>{analysis?.priority}</span>
              </div>
              {typeof analysis?.priority_score === 'number' && (
                <div className="intel-kv">
                  <span className="kv-key">Score</span>
                  <span className="kv-value">{analysis.priority_score}/100</span>
                </div>
              )}
              <div className="intel-kv">
                <span className="kv-key">Needs Reply</span>
                <span className="kv-value">{analysis?.needs_reply ? 'Yes' : 'No'}</span>
              </div>
            </section>

            {sections.deadlines && (
              <section className="intel-section reveal" style={{ ['--stagger' as string]: 3 }}>
                <div className="intel-section-label"><Clock aria-hidden="true" /> Deadline</div>
                {analysis?.deadlines.map((dl, idx) => (
                  <div key={idx} className="intel-item">
                    <Clock aria-hidden="true" />
                    <span>
                      {dl.description}
                      {dl.due_at && <span className="item-deadline"> · {dl.due_at}</span>}
                    </span>
                  </div>
                ))}
              </section>
            )}

            {sections.actions && (
              <section className="intel-section reveal" style={{ ['--stagger' as string]: 4 }}>
                <div className="intel-section-label"><ArrowUpRight aria-hidden="true" /> Tasks</div>
                {analysis?.action_items.map((item, idx) => (
                  <div key={idx} className="intel-item">
                    <ArrowUpRight aria-hidden="true" />
                    <span>
                      {item.description}
                      {item.deadline && <span className="item-deadline"> · Due {item.deadline}</span>}
                    </span>
                  </div>
                ))}
              </section>
            )}

            {analysis?.needs_reply && (
              <section className="intel-section reveal" style={{ ['--stagger' as string]: 5 }}>
                <div className="intel-section-label"><PenLine aria-hidden="true" /> Reply</div>
                <button
                  type="button"
                  className="btn btn-primary btn-block"
                  onClick={() => draftMutation.mutate()}
                  disabled={draftMutation.isPending}
                >
                  {draftMutation.isPending ? (
                    <>
                      <span className="btn-spinner" aria-hidden="true" />
                      Generating…
                    </>
                  ) : (
                    <>
                      <PenLine size={14} aria-hidden="true" />
                      Generate Draft
                    </>
                  )}
                </button>

                {draftMutation.isError && (
                  <div className="banner banner-danger" style={{ marginTop: 'var(--space-3)' }}>
                    Draft failed — is the local AI runtime running?
                  </div>
                )}

                {draftMutation.isSuccess && (
                  <div className="reveal" style={{ marginTop: 'var(--space-3)' }}>
                    <div className="intel-section-label">Draft reply</div>
                    <div className="draft-panel">
                      {draftMutation.data.draft}
                    </div>
                  </div>
                )}
              </section>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
