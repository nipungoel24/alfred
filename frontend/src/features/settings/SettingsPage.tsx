import { Cpu, Database, Palette } from 'lucide-react';

export function SettingsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings</h1>
          <div className="page-subtitle">Application configuration</div>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '0 var(--space-6)', paddingBottom: 'var(--space-6)', maxWidth: 640 }}>
        <div className="settings-group">
          <div className="settings-group-title">
            <Cpu size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
            Local AI
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
            <span className="settings-label">Privacy</span>
            <span className="settings-value" style={{ color: 'var(--success)', fontSize: 'var(--text-xs)' }}>
              All analysis runs locally
            </span>
          </div>
        </div>

        <div className="settings-group">
          <div className="settings-group-title">
            <Database size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
            Data
          </div>
          <div className="settings-row">
            <span className="settings-label">Storage</span>
            <span className="settings-value">Local SQLite (AppData)</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Credentials</span>
            <span className="settings-value" style={{ color: 'var(--success)', fontSize: 'var(--text-xs)' }}>
              DPAPI encrypted
            </span>
          </div>
        </div>

        <div className="settings-group">
          <div className="settings-group-title">
            <Palette size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
            Appearance
          </div>
          <div className="settings-row">
            <span className="settings-label">Theme</span>
            <span className="settings-value">Dark</span>
          </div>
        </div>
      </div>
    </div>
  );
}
