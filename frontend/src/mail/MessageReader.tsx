import { useQuery } from '@tanstack/react-query';
import { Paperclip, MailOpen, PanelRight } from 'lucide-react';
import { emailDetails } from '../api/emails';
import type { Email } from '../api/emails';

interface MessageReaderProps {
  emailId: string | null;
  intelVisible: boolean;
  onToggleIntel: () => void;
}

export function MessageReader({ emailId, intelVisible, onToggleIntel }: MessageReaderProps) {
  const { data: email, isLoading, isError } = useQuery({
    queryKey: ['email', emailId],
    queryFn: () => emailDetails(emailId ?? ''),
    enabled: Boolean(emailId),
    staleTime: 30_000,
  });

  return (
    <section className="reader-pane" aria-label="Message reader">
      <div className="reader-strip">
        <span className="strip-title">Message</span>
        <span className="spacer" />
        {emailId && (
          <button
            type="button"
            className={`icon-btn outlined ${intelVisible ? 'active' : ''}`}
            onClick={onToggleIntel}
            aria-label={intelVisible ? 'Hide Alfred intelligence' : 'Show Alfred intelligence'}
            aria-pressed={intelVisible}
            title="Toggle Alfred Intelligence"
          >
            <PanelRight />
          </button>
        )}
      </div>

      {!emailId ? (
        <div className="reader-empty">
          <div>
            <MailOpen aria-hidden="true" />
            <p>Select a message to read it.</p>
          </div>
        </div>
      ) : isError ? (
        <div className="reader-empty">
          <div>
            <p className="text-danger">Couldn't load this message.</p>
            <p className="text-muted" style={{ marginTop: 4 }}>It may have been removed from Gmail.</p>
          </div>
        </div>
      ) : isLoading || !email ? (
        <div className="reader-scroll" aria-busy="true">
          <div className="reader-inner">
            <div className="skeleton" style={{ width: '75%', height: 22, marginBottom: 16 }} />
            <div className="skeleton" style={{ width: 160, height: 14, marginBottom: 24 }} />
            <div className="skeleton" style={{ width: '100%', height: 12, marginBottom: 8 }} />
            <div className="skeleton" style={{ width: '92%', height: 12, marginBottom: 8 }} />
            <div className="skeleton" style={{ width: '85%', height: 12 }} />
          </div>
        </div>
      ) : (
        <div className="reader-scroll">
          <article className="reader-inner reveal">
            <h2 className="reader-subject">{email.subject}</h2>
            <div className="reader-meta">
              <span
                className="reader-sender-avatar"
                aria-hidden="true"
                style={{ background: avatarGradient(email.sender) }}
              >
                {initialOf(email.sender_name || email.sender)}
              </span>
              <div>
                <div className="reader-sender">{email.sender_name || email.sender}</div>
                <div className="reader-sender-mail">
                  {email.sender} · to {email.recipients?.join(', ') || 'you'}
                </div>
              </div>
              <span className="reader-date">{formatTimeLong(email.received_at)}</span>
            </div>

            <div className="reader-body">{email.body || '(Empty message)'}</div>

            {hasAttachments(email) && (
              <div className="attachment-row" title="Attachment metadata from Gmail">
                <Paperclip aria-hidden="true" />
                <span>{attachmentLabel(email)}</span>
                <span className="attachment-meta">Gmail attachment</span>
              </div>
            )}
          </article>
        </div>
      )}
    </section>
  );
}

function initialOf(sender: string): string {
  const trimmed = sender.trim();
  return trimmed ? trimmed[0].toUpperCase() : '?';
}

/* Deterministic gradient identity per sender — quiet chromatic energy,
   never random per render. */
export function avatarGradient(sender: string): string {
  let hash = 0;
  const key = sender.trim().toLowerCase();
  for (let i = 0; i < key.length; i++) {
    hash = (hash * 31 + key.charCodeAt(i)) | 0;
  }
  const hue = ((hash % 360) + 360) % 360;
  return `linear-gradient(135deg, hsl(${hue} 68% 56%) 0%, hsl(${(hue + 46) % 360} 72% 46%) 100%)`;
}

function formatTimeLong(dateStr?: string | null): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString([], {
    weekday: 'short', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function hasAttachments(email: Email): boolean {
  const meta = (email as Email & { source_metadata?: Record<string, unknown> }).source_metadata;
  if (!meta) return false;
  const raw = meta.gmail_raw as { sizeEstimate?: number; labelIds?: string[] } | undefined;
  if (raw?.sizeEstimate && raw.sizeEstimate > 250_000) return true;
  if (typeof meta.has_attachment === 'boolean') return meta.has_attachment;
  return false;
}

function attachmentLabel(email: Email): string {
  const meta = (email as Email & { source_metadata?: { gmail_raw?: { sizeEstimate?: number } } }).source_metadata;
  const size = meta?.gmail_raw?.sizeEstimate;
  if (typeof size === 'number' && size > 0) {
    if (size > 1_048_576) return `Attachment · ${(size / 1_048_576).toFixed(1)} MB`;
    return `Attachment · ${Math.max(1, Math.round(size / 1024))} KB`;
  }
  return 'Attachment';
}
