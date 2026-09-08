import { useEffect, useRef } from 'react';
import { Search } from 'lucide-react';

const AI_LABELS: Record<string, { label: string; online: boolean; hint: string }> = {
  ready: { label: 'AI Ready', online: true, hint: 'Local AI · qwen3:4b' },
  initializing: { label: 'AI Starting', online: false, hint: 'Local AI starting…' },
  ollama_not_running: { label: 'AI Offline', online: false, hint: 'Ollama isn\'t running — Alfred retries automatically' },
  model_missing: { label: 'Model Missing', online: false, hint: 'qwen3:4b needs to be installed' },
  temporarily_unavailable: { label: 'AI Busy', online: false, hint: 'Local AI temporarily unavailable — retrying' },
  recovering: { label: 'AI Recovering', online: false, hint: 'Local AI recovering…' },
  error: { label: 'AI Error', online: false, hint: 'Local AI error — open Settings for details' },
};

interface WorkspaceHeaderProps {
  title: string;
  subtitle?: string;
  searchValue: string;
  onSearchChange: (value: string) => void;
  aiReady: boolean;
  aiState?: string;
  accountInitial?: string;
}

export function WorkspaceHeader({
  title, subtitle, searchValue, onSearchChange, aiReady, aiState, accountInitial,
}: WorkspaceHeaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  // Ctrl/Cmd+K focuses search from anywhere in the app
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        inputRef.current?.select();
      }
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        inputRef.current?.blur();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  const ai = AI_LABELS[aiState ?? ''] ?? (aiReady
    ? AI_LABELS.ready
    : AI_LABELS.ollama_not_running);

  return (
    <header className="workspace-header">
      <div className="header-context">
        <span className="context-title">{title}</span>
        {subtitle && <span className="context-sub">{subtitle}</span>}
      </div>

      <div className="search-box" role="search">
        <Search size={14} aria-hidden="true" />
        <input
          ref={inputRef}
          id="global-search"
          type="search"
          placeholder="Search all mail…"
          value={searchValue}
          onChange={e => onSearchChange(e.target.value)}
          aria-label="Search all mail"
        />
        <span className="search-shortcut">Ctrl K</span>
      </div>

      <div className="header-actions">
        <span
          className="status-chip"
          title={ai.hint}
        >
          <span className={`status-dot ${ai.online ? 'online' : 'offline'}`} />
          {ai.label}
        </span>
        {accountInitial && (
          <span className="avatar-chip" title="Connected account">
            {accountInitial}
          </span>
        )}
      </div>
    </header>
  );
}
