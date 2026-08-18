import { useEffect, useRef } from 'react';
import { Search } from 'lucide-react';

interface WorkspaceHeaderProps {
  title: string;
  subtitle?: string;
  searchValue: string;
  onSearchChange: (value: string) => void;
  aiReady: boolean;
  accountInitial?: string;
}

export function WorkspaceHeader({
  title, subtitle, searchValue, onSearchChange, aiReady, accountInitial,
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
          title={aiReady ? 'Local AI · qwen3:4b' : 'Local AI unavailable — start Ollama to resume analysis'}
        >
          <span className={`status-dot ${aiReady ? 'online' : 'offline'}`} />
          {aiReady ? 'AI Ready' : 'AI Offline'}
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
