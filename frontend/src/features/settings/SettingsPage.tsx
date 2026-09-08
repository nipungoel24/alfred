import { useQuery } from '@tanstack/react-query';
import { Cpu, Database, Palette, ShieldCheck, Info } from 'lucide-react';
import { ThemeToggle } from '../../theme/ThemeToggle';
import { health as fetchHealth, analysisStatus } from '../../api/emails';

const AI_LABELS: Record<string, string> = {
  ready: 'Ready',
  initializing: 'Starting',
  ollama_not_running: "Ollama isn't running",
  model_missing: 'Model missing',
  temporarily_unavailable: 'Temporarily unavailable',
  recovering: 'Recovering',
  error: 'Error',
};

export function SettingsPage() {
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: fetchHealth, retry: 0 });
  const { data: aiStatus } = useQuery({ queryKey: ['analysisStatus'], queryFn: analysisStatus, retry: 0 });
  const frontendBuild = typeof __ALFRED_BUILD__ !== 'undefined' ? __ALFRED_BUILD__ : 'unknown';

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
              {AI_LABELS[health?.ai ?? ''] ?? 'Starting'}
            </span>
          </div>
          {aiStatus && (
            <>
              <div className="settings-row">
                <span className="settings-label">Model installed</span>
                <span className="settings-value">{aiStatus.model_installed === null ? '—' : aiStatus.model_installed ? 'Yes' : 'No'}</span>
              </div>
              <div className="settings-row">
                <span className="settings-label">Ollama installed</span>
                <span className="settings-value">{aiStatus.ollama_installed ? 'Yes' : 'No'}</span>
              </div>
              <div className="settings-row">
                <span className="settings-label">Queue</span>
                <span className="settings-value">{aiStatus.pending} pending{aiStatus.queue_paused ? ' (paused)' : ''}</span>
              </div>
            </>
          )}
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

        <div className="settings-group reveal" style={{ ['--stagger' as string]: 5 }}>
          <div className="section-label" style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 'var(--space-3)' }}>
            <Info size={12} aria-hidden="true" /> About
          </div>
          <div className="settings-row">
            <span className="settings-label">Frontend build</span>
            <span className="settings-value settings-mono">{frontendBuild}</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Backend build</span>
            <span className="settings-value settings-mono">{health?.build ?? '—'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
