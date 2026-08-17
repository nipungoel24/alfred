import { useQuery } from '@tanstack/react-query';
import { Cpu, Database, Palette, ShieldCheck } from 'lucide-react';
import { ThemeToggle } from '../../theme/ThemeToggle';
import { health as fetchHealth } from '../../api/emails';

export function SettingsPage() {
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: fetchHealth, retry: 0 });

  return (
    <div className="page-scroll">
      <div style={{ maxWidth: 640, margin: '0 auto', padding: 'var(--space-6) var(--space-6) var(--space-10)' }}>
        <div className="reveal">
          <h1 className="page-title" style={{ fontSize: 'var(--text-xl)' }}>Settings</h1>
          <p className="page-subtitle" style={{ marginBottom: 'var(--space-6)' }}>Preferences and runtime information</p>
        </div>

        <div className="settings-group reveal" style={{ ['--stagger' as string]: 1 }}>
          <div className="section-label" style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 'var(--space-3)' }}>
            <Palette size={12} aria-hidden="true" /> Appearance
          </div>
          <div className="settings-row">
            <span className="settings-label">Theme</span>
            <ThemeToggle />
          </div>
        </div>

        <div className="settings-group reveal" style={{ ['--stagger' as string]: 2 }}>
          <div className="section-label" style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 'var(--space-3)' }}>
            <Cpu size={12} aria-hidden="true" /> Local AI
          </div>
          <div className="settings-row">
            <span className="settings-label">Model</span>
            <span className="settings-value">qwen3:4b</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Runtime</span>
            <span className="settings-value">Ollama (local)</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Status</span>
            <span className="settings-value" style={{ color: health?.ai === 'ready' ? 'var(--success)' : 'var(--warning)' }}>
              {health?.ai === 'ready' ? 'Ready' : 'Unavailable'}
            </span>
          </div>
        </div>

        <div className="settings-group reveal" style={{ ['--stagger' as string]: 3 }}>
          <div className="section-label" style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 'var(--space-3)' }}>
            <Database size={12} aria-hidden="true" /> Data
          </div>
          <div className="settings-row">
            <span className="settings-label">Storage</span>
            <span className="settings-value">Local SQLite (AppData)</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Credentials</span>
            <span className="settings-value" style={{ color: 'var(--success)' }}>
              DPAPI encrypted
            </span>
          </div>
        </div>

        <div className="settings-group reveal" style={{ ['--stagger' as string]: 4 }}>
          <div className="section-label" style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 'var(--space-3)' }}>
            <ShieldCheck size={12} aria-hidden="true" /> Privacy
          </div>
          <div className="settings-row">
            <span className="settings-label">Analysis</span>
            <span className="settings-value" style={{ color: 'var(--success)' }}>
              All processing stays local
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
