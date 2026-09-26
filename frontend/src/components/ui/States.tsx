import type { ReactNode } from 'react';
import {
  Inbox,
  SearchX,
  AlertTriangle,
  PlugZap,
  FileQuestion,
  type LucideIcon,
} from 'lucide-react';

/**
 * Shared state surfaces.
 *
 * Every screen that queries needs three outcomes beyond "has data": loading,
 * empty, and failed. Before this existed, four pages conflated "the request
 * failed" with "there is nothing here", so a lost backend looked exactly like
 * an empty mailbox. See docs/UI-DESIGN-SPEC.md §10.
 *
 * These are added because their absence was a defect, not for symmetry.
 */

type Tone = 'neutral' | 'error' | 'info';

function StateBlock({
  icon: Icon,
  tone = 'neutral',
  title,
  body,
  code,
  actions,
}: {
  icon: LucideIcon;
  tone?: Tone;
  title: string;
  body?: ReactNode;
  code?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="state-block" data-tone={tone}>
      <span className="state-icon">
        <Icon size={18} strokeWidth={1.75} aria-hidden="true" />
      </span>
      <p className="state-title">{title}</p>
      {body && <p className="state-body">{body}</p>}
      {code && <p className="state-code">{code}</p>}
      {actions && <div className="state-actions">{actions}</div>}
    </div>
  );
}

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <StateBlock icon={Inbox} title={title} body={body} actions={action} />
  );
}

export function EmptySearchState({
  query,
  onClear,
}: {
  query: string;
  onClear: () => void;
}) {
  return (
    <StateBlock
      icon={SearchX}
      title="No messages match your search"
      body={
        <>
          Nothing in your local mailbox matches <strong>{query}</strong>. Alfred
          searches mail it has already synced.
        </>
      }
      actions={
        <button type="button" className="btn btn-surface btn-sm" onClick={onClear}>
          Clear search
        </button>
      }
    />
  );
}

/**
 * A request that failed. Always offers a retry, and names the reason in
 * plain language rather than surfacing a raw exception.
 */
export function ErrorState({
  title = "This didn't load",
  body,
  code,
  onRetry,
}: {
  title?: string;
  body?: ReactNode;
  code?: string;
  onRetry?: () => void;
}) {
  return (
    <StateBlock
      icon={AlertTriangle}
      tone="error"
      title={title}
      body={
        body ?? (
          <>
            Alfred could not reach its local service. Your mail and settings are
            untouched.
          </>
        )
      }
      code={code}
      actions={
        onRetry ? (
          <button type="button" className="btn btn-surface btn-sm" onClick={onRetry}>
            Try again
          </button>
        ) : undefined
      }
    />
  );
}

/** The local AI runtime is not answering. The mailbox still works. */
export function AiUnavailableState({
  reason,
  onRetry,
  onOpenSettings,
}: {
  reason: 'offline' | 'model_missing' | 'pending';
  onRetry?: () => void;
  onOpenSettings?: () => void;
}) {
  if (reason === 'pending') {
    return (
      <StateBlock
        icon={FileQuestion}
        tone="info"
        title="Analysing this message"
        body="Alfred reads each new inbox message on your own machine. This one is still in the queue."
      />
    );
  }
  if (reason === 'model_missing') {
    return (
      <StateBlock
        icon={PlugZap}
        tone="info"
        title="No local model installed"
        body="Your mailbox works fully. Summaries, tasks and deadlines need a local model."
        actions={
          onOpenSettings ? (
            <button type="button" className="btn btn-surface btn-sm" onClick={onOpenSettings}>
              Open Settings
            </button>
          ) : undefined
        }
      />
    );
  }
  return (
    <StateBlock
      icon={PlugZap}
      tone="info"
      title="Local AI is offline"
      body="Your mailbox works fully. Summaries, tasks and deadlines resume automatically when the local runtime is running."
      actions={
        onRetry ? (
          <button type="button" className="btn btn-surface btn-sm" onClick={onRetry}>
            Check again
          </button>
        ) : undefined
      }
    />
  );
}

/** No Gmail account is connected yet. */
export function NoAccountState({ onConnect }: { onConnect: () => void }) {
  return (
    <StateBlock
      icon={Inbox}
      title="No mailbox connected"
      body="Connect a Gmail account to start mirroring your mail locally. Alfred never writes to your mailbox."
      actions={
        <button type="button" className="btn btn-primary btn-sm" onClick={onConnect}>
          Connect Gmail
        </button>
      }
    />
  );
}
