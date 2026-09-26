import { useEffect, useRef } from 'react';
import { Search, X, RefreshCw, Cpu } from 'lucide-react';
import { aiStateMeta } from '../lib/aiState';

export interface WorkspaceHeaderProps {
  title: string;
  subtitle?: string;
  /**
   * The view's <h1>. Focusable but not tabbable, so a deliberate navigation can
   * hand focus here without adding a stop to the tab order.
   */
  headingRef?: React.Ref<HTMLHeadingElement>;
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
  headingRef,
  searchValue,
  onSearchChange,
  aiReady,
  aiState,
  accountEmail,
  onSync,
  syncing,
}: WorkspaceHeaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  // Where focus came from before the search took it, so Escape can hand it back
  // instead of dropping the user on <body> with nothing selected.
  const preSearchFocus = useRef<HTMLElement | null>(null);
  const modifier = modifierKey();

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isShortcut = e.key.toLowerCase() === 'k' && (e.ctrlKey || e.metaKey);
      if (isShortcut) {
        e.preventDefault();
        const active = document.activeElement;
        preSearchFocus.current =
          active instanceof HTMLElement && active !== inputRef.current ? active : null;
        inputRef.current?.focus();
        inputRef.current?.select();
        return;
      }
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        // Blurring alone strands focus on <body>. Return it to whatever held it
        // before the shortcut, when that element is still on the page.
        const previous = preSearchFocus.current;
        preSearchFocus.current = null;
        inputRef.current?.blur();
        if (previous && previous.isConnected) previous.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  // One shared description of the AI state machine, so this chip and the
  // Settings page can never disagree about what a state is called.
  const ai = aiStateMeta(aiState ?? (aiReady ? 'ready' : 'ollama_not_running'));
  const aiOnline = ai.tone === 'ok';
  const hasSearch = searchValue.trim().length > 0;

  return (
    <header className="workspace-header">
      <div className="header-context">
        <h1 className="context-title" tabIndex={-1} ref={headingRef}>
          {title}
        </h1>
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

        <span className="status-chip" data-online={aiOnline} title={ai.hint}>
          <Cpu size={13} aria-hidden="true" />
          <span className="status-chip-label">{ai.chip}</span>
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
