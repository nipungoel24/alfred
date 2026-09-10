import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, MailOpen } from 'lucide-react';
import { emailDetails } from '../api/emails';
import { LinkifiedBody } from './LinkifiedBody';

interface SourceEmailPreviewProps {
  /** Local email id to preview, or null when closed. */
  emailId: string | null;
  onClose: () => void;
  /** Optional task/deadline relationship section rendered above the body. */
  relationship?: ReactNode;
  /** Optional "Open in Mail" handler; hidden when omitted. */
  onOpenInMail?: (emailId: string) => void;
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString([], {
    weekday: 'short', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

/**
 * One reusable source-email preview for every derived object (tasks,
 * deadlines, briefing items). Plain React text + LinkifiedBody links —
 * never arbitrary email HTML.
 */
export function SourceEmailPreview({ emailId, onClose, relationship, onOpenInMail }: SourceEmailPreviewProps) {
  const { data: email, isLoading, isError } = useQuery({
    queryKey: ['email', emailId],
    queryFn: () => emailDetails(emailId ?? ''),
    enabled: Boolean(emailId),
    staleTime: 30_000,
  });

  const dialogRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const openerRef = useRef<Element | null>(null);

  // Capture the opener, move initial focus into the dialog, and restore
  // focus to the opener when the preview closes.
  useEffect(() => {
    if (!emailId) return;
    openerRef.current = document.activeElement;
    const frame = requestAnimationFrame(() => {
      closeRef.current?.focus();
    });
    return () => {
      cancelAnimationFrame(frame);
      const opener = openerRef.current as HTMLElement | null;
      opener?.focus?.();
    };
  }, [emailId]);

  // Escape closes; Tab/Shift+Tab cycle inside the modal (focus trap).
  useEffect(() => {
    if (!emailId) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }
      if (e.key !== 'Tab') return;
      const root = dialogRef.current;
      if (!root) return;
      const focusables = Array.from(
        root.querySelectorAll<HTMLElement>(
          'button:not([disabled]), [href], input:not([disabled]), ' +
          'select:not([disabled]), textarea:not([disabled]), ' +
          '[tabindex]:not([tabindex="-1"])'
        )
      );
      if (focusables.length === 0) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [emailId, onClose]);

  if (!emailId) return null;

  return (
    <div className="source-preview-backdrop" onClick={onClose}>
      <div
        ref={dialogRef}
        className="source-preview"
        role="dialog"
        aria-modal="true"
        aria-label={email ? `Source email: ${email.subject}` : 'Source email'}
        onClick={e => e.stopPropagation()}
      >
        <div className="source-preview-head">
          <span className="source-preview-kicker">Source email</span>
          <span className="spacer" />
          {email && onOpenInMail && (
            <button
              type="button"
              className="source-preview-action"
              onClick={() => onOpenInMail(email.id)}
            >
              <MailOpen size={13} aria-hidden="true" />
              Open in Mail
            </button>
          )}
          <button
            ref={closeRef}
            type="button"
            className="icon-btn"
            onClick={onClose}
            aria-label="Close source email preview"
          >
            <X size={15} aria-hidden="true" />
          </button>
        </div>

        {isError ? (
          <div className="source-preview-empty">
            <p className="text-danger">Couldn't load this message.</p>
            <p className="text-muted">It may have been removed from Gmail.</p>
          </div>
        ) : (
          <div className="source-preview-scroll">
            {relationship}
            {isLoading || !email ? (
              <div aria-busy="true">
                <div className="skeleton" style={{ width: '70%', height: 18, marginBottom: 12 }} />
                <div className="skeleton" style={{ width: '45%', height: 12, marginBottom: 16 }} />
                <div className="skeleton" style={{ width: '100%', height: 12, marginBottom: 8 }} />
                <div className="skeleton" style={{ width: '92%', height: 12 }} />
              </div>
            ) : (
              <>
                <h3 className="source-preview-subject">{email.subject}</h3>
                <div className="source-preview-meta">
                  <div className="source-preview-sender">{email.sender_name || email.sender}</div>
                  <div className="source-preview-mail">
                    {email.sender} · {formatDate(email.received_at)}
                    {email.account_id ? ` · ${email.account_id.replace(/^gmail_/, '')}` : ''}
                  </div>
                </div>

                <LinkifiedBody text={email.body} className="source-preview-body" />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
