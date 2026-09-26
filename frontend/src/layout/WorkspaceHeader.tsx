import { useEffect, useRef } from 'react';
import { Search, X, RefreshCw, Cpu } from 'lucide-react';

const AI_LABELS: Record<string, { label: string; online: boolean; hint: string }> = {
  ready: { label: 'AI ready', online: true, hint: 'Local AI is ready' },
  initializing: { label: 'AI starting', online: false, hint: 'Local AI is starting' },
  ollama_not_running: {
    label: 'AI offline',
    online: false,
    hint: 'Ollama is not running. Your mailbox works; summaries resume when it is.',
  },
  model_missing: {
    label: 'Model missing',
    online: false,
    hint: 'The local model is not installed. Choose one in Settings.',
  },
  temporarily_unavailable: { label: 'AI busy', online: false, hint: 'Local AI is busy' },
  recovering: { label: 'AI recovering', online: false, hint: 'Local AI is recovering' },
  error: { label: 'AI error', online: false, hint: 'Local AI reported an error' },
};

export interface WorkspaceHeaderProps {
  title: string;
  subtitle?: string;
  searchValue: string;
  onSearchChange: (value: string) => void;
  aiReady: boolean;
  aiState?: string;
  accountEmail?: string;
  onSync?: () => void;
  syncing?: boolean;
}

/** True on Windows/Linux, where the shortcut really is Ctrl. */
function modifierKey(): string {
  if (typeof navigator === 'undefined') return 'Ctrl';
  return /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent) ? 'Cmd' : 'Ctrl';
}

/**
 * Application header: context, global search, sync, and service state.
 *
 * Search is a first-class control here, not an afterthought in a corner.
 * It is the primary way to find one specific message in a large mailbox, so
 * it gets a real input, a clear affordance, and a discoverable shortcut that
 * reports the correct modifier for the platform.
 */
export function WorkspaceHeader({
  title,
  subtitle,
  searchValue,
  onSearchChange,
  aiReady,
  aiState,
  accountEmail,
  onSync,
  syncing,
}: WorkspaceHeaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const modifier = modifierKey();

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isShortcut = e.key.toLowerCase() === 'k' && (e.ctrlKey || e.metaKey);
      if (isShortcut) {
        e.preventDefault();
        inputRef.current?.focus();
        inputRef.current?.select();
        return;
      }
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        inputRef.current?.blur();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  const ai = AI_LABELS[aiState ?? ''] ?? (aiReady ? AI_LABELS.ready : AI_LABELS.ollama_not_running);
  const hasSearch = searchValue.trim().length > 0;

  return (
    <header className="workspace-header">
      <div className="header-context">
        <h1 className="context-title">{title}</h1>
        {subtitle && <p className="context-sub">{subtitle}</p>}
      </div>

      <div className="header-search" role="search">
        <label className="sr-only" htmlFor="global-search">
          Search all mail
        </label>
        <Search className="header-search-icon" size={14} aria-hidden="true" />
        <input
          id="global-search"
          ref={inputRef}
          className="header-search-input"
          type="search"
          value={searchValue}
          placeholder="Search all mail"
          autoComplete="off"
          spellCheck={false}
          aria-describedby="global-search-hint"
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {hasSearch ? (
          <button
            type="button"
            className="header-search-clear"
            aria-label="Clear search"
            onClick={() => {
              onSearchChange('');
              inputRef.current?.focus();
            }}
          >
            <X size={13} aria-hidden="true" />
          </button>
        ) : (
          <kbd className="header-search-hint" id="global-search-hint">
            {modifier} K
          </kbd>
        )}
      </div>

      <div className="header-actions">
        {onSync && (
          <button
            type="button"
            className="btn btn-surface btn-sm"
            onClick={onSync}
            disabled={syncing}
            aria-busy={syncing}
          >
            <RefreshCw size={13} aria-hidden="true" className={syncing ? 'is-spinning' : undefined} />
            <span className="btn-label">{syncing ? 'Syncing' : 'Sync'}</span>
          </button>
        )}

        <span className="status-chip" data-online={ai.online} title={ai.hint}>
          <Cpu size={13} aria-hidden="true" />
          <span className="status-chip-label">{ai.label}</span>
        </span>

        {accountEmail && (
          <span className="avatar-chip" title={accountEmail}>
            <span className="avatar-chip-initial" aria-hidden="true">
              {accountEmail[0]?.toUpperCase()}
            </span>
            <span className="sr-only">Connected as {accountEmail}</span>
          </span>
        )}
      </div>
    </header>
  );
}
