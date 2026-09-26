import { useMemo } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Sparkles, AlertTriangle, Clock, ArrowUpRight, PenLine, Zap, X, MessagesSquare,
} from 'lucide-react';
import { draft as generateDraft } from '../api/emails';
import type { Email } from '../api/emails';
import { AiUnavailableState } from '../components/ui/States';

interface IntelligencePanelProps {
  email: Email;
  onClose?: () => void;
  /** Live AI runtime state, so an offline runtime is explained rather than
   *  shown as an indefinite "pending". */
  aiState?: string;
  onOpenSettings?: () => void;
}

/**
 * Alfred's intelligence for the selected message.
 *
 * Design rules, from docs/UI-DESIGN-SPEC.md §9.7:
 * - Every section is conditional. A section with no data is not rendered at
 *   all — not as an empty box, not as an em dash.
 * - Alfred never invents output. If there is no analysis, it says so and says
 *   whether more is coming.
 * - The panel supports the email. It never sits above the message body.
 */
export function IntelligencePanel({
  email,
  onClose,
  aiState,
  onOpenSettings,
}: IntelligencePanelProps) {
  const queryClient = useQueryClient();
  const analysis = email.analysis;

  const draftMutation = useMutation({
    mutationFn: () => generateDraft(email.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email', email.id] });
    },
  });

  const sections = useMemo(
    () => ({
      summary: Boolean(analysis?.short_summary?.trim()),
      why: Boolean(analysis?.reason_for_priority?.trim()),
      needsReply: Boolean(analysis?.needs_reply),
      deadlines: Boolean(analysis?.deadlines?.length),
      tasks: Boolean(analysis?.action_items?.length),
      priority: Boolean(analysis?.priority),
      details: Boolean(analysis?.important_details?.length),
    }),
    [analysis],
  );

  // Runtime unavailable is a real, explainable state — not "pending".
  const aiReason =
    aiState === 'model_missing'
      ? 'model_missing'
      : aiState && aiState !== 'ready'
        ? 'offline'
        : 'pending';

  const hasAnySection = Object.values(sections).some(Boolean);

  return (
    <aside className="intelligence-pane" aria-label="Alfred intelligence">
      <div className="intel-head">
        <h2 className="intel-title">
          <Sparkles size={14} aria-hidden="true" />
          Alfred
        </h2>
        {onClose && (
          <button
            type="button"
            className="icon-btn outlined"
            onClick={onClose}
            aria-label="Close Alfred panel"
          >
            <X size={14} aria-hidden="true" />
          </button>
        )}
      </div>

      <div className="intel-scroll">
        {!analysis ? (
          <AiUnavailableState
            reason={aiReason}
            onRetry={() => void queryClient.invalidateQueries({ queryKey: ['email', email.id] })}
            onOpenSettings={onOpenSettings}
          />
        ) : !hasAnySection ? (
          <div className="intel-pending">
            <p className="intel-pending-title">Nothing to add</p>
            <p className="text-muted">
              Alfred found no summary, tasks or deadlines in this message. That is
              a real result, not a failure.
            </p>
          </div>
        ) : (
          <>
            {sections.summary && (
              <section className="intel-section">
                <h3 className="intel-section-label">
                  <Zap size={12} aria-hidden="true" /> Summary
                </h3>
                <p className="intel-summary">{analysis.short_summary}</p>
              </section>
            )}

            {sections.why && (
              <section className="intel-section">
                <h3 className="intel-section-label">
                  <Sparkles size={12} aria-hidden="true" /> Why it matters
                </h3>
                <p className="intel-why">{analysis.reason_for_priority}</p>
              </section>
            )}

            {sections.needsReply && (
              <section className="intel-section">
                <h3 className="intel-section-label">
                  <PenLine size={12} aria-hidden="true" /> Needs reply
                </h3>
                <p className="intel-why">
                  Alfred judges this message expects a response from you.
                </p>
                <button
                  type="button"
                  className="btn btn-surface btn-sm btn-block"
                  onClick={() => draftMutation.mutate()}
                  disabled={draftMutation.isPending}
                >
                  <PenLine size={13} aria-hidden="true" />
                  <span className="btn-label">
                    {draftMutation.isPending ? 'Drafting' : 'Draft a reply'}
                  </span>
                </button>
                {draftMutation.isError && (
                  <div className="banner banner-danger" role="alert">
                    <AlertTriangle size={13} aria-hidden="true" />
                    <span>Could not draft a reply. Your mailbox is unaffected.</span>
                  </div>
                )}
                {typeof draftMutation.data?.draft === 'string' &&
                  draftMutation.data.draft.length > 0 && (
                    <div className="draft-panel">
                      <h4 className="intel-section-label">Draft reply</h4>
                      <p className="draft-body">{draftMutation.data.draft}</p>
                      <p className="text-muted">
                        Generated locally. Review it before sending — Alfred does not send mail.
                      </p>
                    </div>
                  )}
              </section>
            )}

            {sections.deadlines && (
              <section className="intel-section">
                <h3 className="intel-section-label">
                  <Clock size={12} aria-hidden="true" /> Deadlines
                </h3>
                <ul className="intel-list">
                  {analysis.deadlines!.map((d, i) => (
                    <li className="intel-item" key={`${d.description}-${i}`}>
                      <span className="intel-item-text">{d.description}</span>
                      {d.due_at && <span className="item-deadline">{d.due_at}</span>}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {sections.tasks && (
              <section className="intel-section">
                <h3 className="intel-section-label">
                  <ArrowUpRight size={12} aria-hidden="true" /> Tasks
                </h3>
                <ul className="intel-list">
                  {analysis.action_items!.map((a, i) => (
                    <li className="intel-item" key={`${a.description}-${i}`}>
                      <span className="intel-item-text">{a.description}</span>
                      {a.deadline && <span className="item-deadline">{a.deadline}</span>}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {sections.priority && (
              <section className="intel-section">
                <h3 className="intel-section-label">Priority</h3>
                <div className="intel-kv">
                  <span className="kv-key">Level</span>
                  <span className={`badge badge-${analysis.priority}`}>
                    {analysis.priority}
                  </span>
                </div>
                {typeof analysis.priority_score === 'number' && (
                  <div className="intel-kv">
                    <span className="kv-key">Score</span>
                    <span className="kv-value">{analysis.priority_score}/100</span>
                  </div>
                )}
              </section>
            )}

            {sections.details && (
              <section className="intel-section">
                <h3 className="intel-section-label">
                  <MessagesSquare size={12} aria-hidden="true" /> Context
                </h3>
                <ul className="intel-list">
                  {analysis.important_details!.map((detail, i) => (
                    <li className="intel-item" key={`${detail}-${i}`}>
                      <span className="intel-item-text">{detail}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
