import type { ReactNode } from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, CircleDashed } from 'lucide-react';
import type { AiTone } from '../../lib/aiState';

/**
 * The small component layer the Accounts and Settings surfaces share.
 *
 * Each of these exists because the markup was duplicated or the absence caused a
 * defect, not for tidiness. `StatusIndicator` in particular is a spec
 * requirement: status is icon *and* label, never colour alone.
 */

const TONE_ICON: Record<AiTone, typeof CheckCircle2> = {
  ok: CheckCircle2,
  working: CircleDashed,
  warning: AlertTriangle,
  danger: AlertCircle,
};

/**
 * Status is never conveyed by colour alone (spec §3.5): the icon shape and the
 * text both carry it, so the control is legible in greyscale and to a screen
 * reader that ignores colour entirely.
 */
export function StatusIndicator({
  tone,
  label,
  hint,
}: {
  tone: AiTone;
  label: string;
  hint?: string;
}) {
  const Icon = TONE_ICON[tone];
  return (
    <span className={`status-indicator tone-${tone}`} title={hint}>
      <Icon size={14} strokeWidth={2} aria-hidden="true" />
      <span>{label}</span>
    </span>
  );
}

export function SettingsSection({
  title,
  icon,
  description,
  children,
  stagger,
}: {
  title: string;
  icon?: ReactNode;
  description?: string;
  children: ReactNode;
  stagger?: number;
}) {
  return (
    <section
      className="settings-group reveal"
      style={stagger === undefined ? undefined : ({ '--stagger': stagger } as React.CSSProperties)}
    >
      <h2 className="section-label settings-section-label">
        {icon}
        {title}
      </h2>
      {description && <p className="settings-section-description">{description}</p>}
      <div className="settings-rows">{children}</div>
    </section>
  );
}

/**
 * One labelled fact or control. `labelNode` is a `<span>` in a row and a
 * `<dt>`-equivalent in a description list; the caller decides, and this keeps
 * the two columns aligned either way.
 */
export function SettingsRow({
  label,
  hint,
  children,
  stacked,
}: {
  label: string;
  hint?: string;
  children?: ReactNode;
  stacked?: boolean;
}) {
  return (
    <div className={`settings-row${stacked ? ' stacked' : ''}`}>
      <div className="settings-row-text">
        <span className="settings-label">{label}</span>
        {hint && <span className="settings-hint">{hint}</span>}
      </div>
      {children !== undefined && <div className="settings-control">{children}</div>}
    </div>
  );
}

/** A plain read-only value, for facts that are not a status. */
export function SettingsValue({ children, mono }: { children: ReactNode; mono?: boolean }) {
  return <span className={`settings-value${mono ? ' settings-mono' : ''}`}>{children}</span>;
}
