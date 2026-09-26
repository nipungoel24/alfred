import { useEffect, useRef, useState } from 'react';
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
  const copyTimer = useRef<number | null>(null);

  const { data: email, isLoading, isError } = useQuery({
    queryKey: ['email', emailId],
    queryFn: () => emailDetails(emailId ?? ''),
    enabled: Boolean(emailId),
    staleTime: 30_000,
  });

  const isLater = Boolean(emailId && laterIds.has(emailId));

  // Selecting another message must not leave a stale "Copied" acknowledgement
  // pointing at the previous one.
  useEffect(() => {
    setCopied(false);
    if (copyTimer.current !== null) {
      window.clearTimeout(copyTimer.current);
      copyTimer.current = null;
    }
  }, [emailId]);

  useEffect(() => () => {
    if (copyTimer.current !== null) window.clearTimeout(copyTimer.current);
  }, []);

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
    if (copyTimer.current !== null) window.clearTimeout(copyTimer.current);
    copyTimer.current = window.setTimeout(() => setCopied(false), 1600);
  };

  const recipients = (email?.recipients ?? []).filter((r) => r.trim().length > 0);
  const timestamp = formatTimeLong(email?.received_at);
  const attachments = email ? describeAttachments(email) : null;

  return (
    <section className="reader-pane" aria-label="Message reader">
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
            <p className="reader-empty-detail">It may have been removed from Gmail.</p>
          </div>
        </div>
      ) : isLoading || !email ? (
        <div className="reader-scroll" aria-busy="true">
          <div className="reader-surface">
            <div className="reader-document">
              <div className="skeleton skeleton-line-xl skeleton-w-80" />
              <div className="reader-skeleton-meta">
                <div className="skeleton skeleton-line-sm skeleton-w-40" />
                <div className="skeleton skeleton-line-sm skeleton-w-55" />
              </div>
              <div className="skeleton skeleton-line-lg skeleton-w-full" />
              <div className="skeleton skeleton-line-lg skeleton-w-90" />
              <div className="skeleton skeleton-line-lg skeleton-w-70" />
            </div>
          </div>
        </div>
      ) : (
        <div className="reader-scroll">
          <article className="reader-surface">
            <div className="reader-document">
              {/* 1 — Subject: the only large type in the pane. */}
              <h2 className="reader-subject">{email.subject}</h2>

              {/* 2, 3, 4 — Sender, recipients, timestamp. Each is its own
                  labelled field so a long value wraps instead of pushing the
                  rest of the row off the pane. */}
              <dl className="reader-fields">
                <div className="reader-field">
                  <dt className="reader-field-label">From</dt>
                  <dd className="reader-field-value reader-field-sender">
                    {email.sender_name ? (
                      <>
                        <span className="reader-sender">{email.sender_name}</span>
                        <span className="reader-sender-mail">{email.sender}</span>
                      </>
                    ) : (
                      <span className="reader-sender">{email.sender}</span>
                    )}
                  </dd>
                </div>

                {recipients.length > 0 && (
                  <div className="reader-field">
                    <dt className="reader-field-label">To</dt>
                    <dd className="reader-field-value">{recipients.join(', ')}</dd>
                  </div>
                )}

                {timestamp && (
                  <div className="reader-field">
                    <dt className="reader-field-label">Date</dt>
                    <dd className="reader-field-value">
                      <time className="reader-timestamp" dateTime={email.received_at ?? undefined}>
                        {timestamp}
                      </time>
                    </dd>
                  </div>
                )}
              </dl>

              {/* 5 — Body. */}
              <LinkifiedBody text={email.body} className="reader-body" />

              {/* 6 — Attachments. */}
              {attachments && (
                <section className="reader-attachments" aria-label="Attachments">
                  <Paperclip aria-hidden="true" />
                  <span className="reader-attachment-text">
                    {attachments.count === null
                      ? 'Attachments'
                      : `${attachments.count} attachment${attachments.count === 1 ? '' : 's'}`}
                  </span>
                  {attachments.sizeLabel && (
                    <span className="reader-attachment-size">{attachments.sizeLabel}</span>
                  )}
                </section>
              )}

              {/* 7 — Actions. */}
              <div className="reader-actions" role="toolbar" aria-label="Message actions">
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
            </div>
          </article>
        </div>
      )}
    </section>
  );
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

type AttachmentInfo = {
  /** null when the provider gives no count — never a fabricated number. */
  count: number | null;
  sizeLabel: string | null;
};

type RawMeta = {
  has_attachment?: unknown;
  gmail_raw?: { sizeEstimate?: number; attachmentCount?: number } | null;
};

function readMeta(email: Email): RawMeta | null {
  return (email as Email & { source_metadata?: RawMeta | null }).source_metadata ?? null;
}

/**
 * Gmail's `sizeEstimate` is the size of the whole RFC822 message, not of its
 * attachments, so it can only ever be a fallback signal. The provider's own
 * `has_attachment` flag is authoritative and is checked first: a large plain
 * message is not an attachment. No per-file metadata is persisted by the
 * backend, so no filenames or counts are invented here.
 */
function describeAttachments(email: Email): AttachmentInfo | null {
  const meta = readMeta(email);
  if (!meta) return null;

  const flag = meta.has_attachment;
  const present =
    typeof flag === 'boolean'
      ? flag
      : Boolean(meta.gmail_raw?.sizeEstimate && meta.gmail_raw.sizeEstimate > 250_000);
  if (!present) return null;

  const declared = meta.gmail_raw?.attachmentCount;
  const count = typeof declared === 'number' && declared > 0 ? declared : null;

  return { count, sizeLabel: formatSize(meta.gmail_raw?.sizeEstimate) };
}

function formatSize(bytes?: number): string | null {
  if (typeof bytes !== 'number' || bytes <= 0) return null;
  if (bytes > 1_048_576) return `${(bytes / 1_048_576).toFixed(1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}
