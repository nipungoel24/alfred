import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Paperclip, MailOpen, Archive, ArchiveRestore, Copy, Check, PanelRight } from 'lucide-react';
import { emailDetails } from '../api/emails';
import type { Email } from '../api/emails';
import { LinkifiedBody } from './LinkifiedBody';

interface MessageReaderProps {
  emailId: string | null;
  intelVisible: boolean;
  onToggleIntel: () => void;
  laterIds: ReadonlySet<string>;
  onToggleLater: (id: string) => void;
}

export function MessageReader({
  emailId, intelVisible, onToggleIntel, laterIds, onToggleLater,
}: MessageReaderProps) {
  const [copied, setCopied] = useState(false);

  const { data: email, isLoading, isError } = useQuery({
    queryKey: ['email', emailId],
    queryFn: () => emailDetails(emailId ?? ''),
    enabled: Boolean(emailId),
    staleTime: 30_000,
  });

  const isLater = Boolean(emailId && laterIds.has(emailId));

  const handleCopy = async () => {
    if (!email) return;
    const text = `Subject: ${email.subject}\nFrom: ${email.sender_name || email.sender} <${email.sender}>\nDate: ${formatTimeLong(email.received_at)}\n\n${email.body}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  return (
    <section className="reader-pane" aria-label="Message reader">
      {/* Sticky toolbar — real actions only */}
      <div className="reader-toolbar" role="toolbar" aria-label="Reader actions">
        <span className="toolbar-title">Message</span>
        <span className="spacer" />
        {emailId && email && (
          <>
            <button
              type="button"
              className={`toolbar-action ${isLater ? 'active' : ''}`}
              onClick={() => onToggleLater(email.id)}
              aria-pressed={isLater}
              title={isLater ? 'Remove from Later' : 'Save for Later'}
            >
              {isLater ? <ArchiveRestore aria-hidden="true" /> : <Archive aria-hidden="true" />}
              Later
            </button>
            <button
              type="button"
              className={`toolbar-action ${copied ? 'copied' : ''}`}
              onClick={handleCopy}
              title="Copy message text"
            >
              {copied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </>
        )}
        <button
          type="button"
          className={`toolbar-action ${intelVisible ? 'active' : ''}`}
          onClick={onToggleIntel}
          aria-pressed={intelVisible}
          title={intelVisible ? 'Hide Alfred Intelligence' : 'Show Alfred Intelligence'}
        >
          <PanelRight aria-hidden="true" />
          Intelligence
        </button>
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
          <div className="reader-surface">
            <div className="reader-document">
              <div className="skeleton" style={{ width: '78%', height: 24, marginBottom: 24 }} />
              <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 20 }}>
                <div className="skeleton" style={{ width: 40, height: 40, borderRadius: 10 }} />
                <div style={{ flex: 1 }}>
                  <div className="skeleton" style={{ width: 140, height: 14, marginBottom: 6 }} />
                  <div className="skeleton" style={{ width: 220, height: 12 }} />
                </div>
              </div>
              <div className="skeleton" style={{ width: '100%', height: 14, marginBottom: 10 }} />
              <div className="skeleton" style={{ width: '94%', height: 14, marginBottom: 10 }} />
              <div className="skeleton" style={{ width: '88%', height: 14 }} />
            </div>
          </div>
        </div>
      ) : (
        <div className="reader-scroll">
          <article className="reader-surface">
            <div className="reader-document">
              <h2 className="reader-subject">{email.subject}</h2>
              <div className="reader-meta">
                <span
                  className="reader-sender-avatar"
                  aria-hidden="true"
                  style={{ background: avatarGradient(email.sender) }}
                >
                  {initialOf(email.sender_name || email.sender)}
                </span>
                <div style={{ minWidth: 0 }}>
                  <div className="reader-sender">{email.sender_name || email.sender}</div>
                  <div className="reader-sender-mail">
                    {email.sender} · to {email.recipients?.join(', ') || 'you'}
                  </div>
                </div>
                <span className="reader-date">{formatTimeLong(email.received_at)}</span>
              </div>

              <LinkifiedBody text={email.body} className="reader-body" />

              {hasAttachments(email) && (
                <div className="attachment-row" title="Attachment metadata from Gmail">
                  <Paperclip aria-hidden="true" />
                  <span>{attachmentLabel(email)}</span>
                  <span className="attachment-meta">Gmail attachment</span>
                </div>
              )}
            </div>
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
