import { useQuery } from '@tanstack/react-query';
import { Cpu, Database, Palette, ShieldCheck, Info, HardDrive } from 'lucide-react';
import { ThemeToggle } from '../../theme/ThemeToggle';
import { health as fetchHealth, analysisStatus } from '../../api/emails';
import { ErrorState } from '../../components/ui/States';
import { SettingsSection, SettingsRow, SettingsValue, StatusIndicator } from '../../components/ui/Settings';
import { aiStateMeta } from '../../lib/aiState';

export function SettingsPage() {
  const healthQuery = useQuery({ queryKey: ['health'], queryFn: fetchHealth, retry: 0 });
  const aiStatusQuery = useQuery({
    queryKey: ['analysisStatus'],
    queryFn: analysisStatus,
    retry: 0,
  });
  const health = healthQuery.data;
  const aiStatus = aiStatusQuery.data;
  const runtimeFailed = healthQuery.isError || aiStatusQuery.isError;
  const runtimeRetrying = healthQuery.isFetching || aiStatusQuery.isFetching;
  const runtimePending = healthQuery.isPending || aiStatusQuery.isPending;

  const retryRuntime = () => {
    void healthQuery.refetch();
    void aiStatusQuery.refetch();
  };

  const frontendBuild = typeof __ALFRED_BUILD__ !== 'undefined' ? __ALFRED_BUILD__ : 'unknown';

  return (
    <div className="page-scroll">
      <div className="page-container page-container-narrow">
        <div className="reveal">
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">Preferences and runtime information</p>
        </div>

        <SettingsSection
          title="Appearance"
          icon={<Palette size={12} aria-hidden="true" />}
          stagger={1}
        >
          <SettingsRow label="Theme" hint="Follows your system setting unless you choose one.">
            <ThemeToggle />
          </SettingsRow>
        </SettingsSection>

        <SettingsSection
          title="Local AI"
          icon={<Cpu size={12} aria-hidden="true" />}
          description="Summaries and actions are produced on this machine. Nothing is sent to a server."
          stagger={2}
        >
          {/* Scoped, not page-level: Theme, Data, Privacy and About all work
              without this query, so a failure here must not hide them. */}
          {runtimeFailed ? (
            <ErrorState
              title="Runtime status unavailable"
              body="Alfred could not read the local AI runtime. Your settings below are unaffected."
              onRetry={retryRuntime}
              retrying={runtimeRetrying}
            />
          ) : runtimePending ? (
            <div className="settings-skeleton" aria-busy="true">
              <div className="skeleton skeleton-line-md skeleton-w-full" />
              <div className="skeleton skeleton-line-md skeleton-w-80" />
              <div className="skeleton skeleton-line-md skeleton-w-55" />
            </div>
          ) : (
            <>
              <SettingsRow label="Model">
                {/* The supervisor reports the model it is actually using. */}
                <SettingsValue mono>{aiStatus?.model ?? 'Unknown'}</SettingsValue>
              </SettingsRow>
              <SettingsRow label="Runtime">
                <SettingsValue>Ollama (local)</SettingsValue>
              </SettingsRow>
              <SettingsRow label="Status">
                <StatusIndicator
                  tone={aiStateMeta(aiStatus?.state ?? health?.ai).tone}
                  label={aiStateMeta(aiStatus?.state ?? health?.ai).word}
                  hint={aiStateMeta(aiStatus?.state ?? health?.ai).hint}
                />
              </SettingsRow>
              {aiStatus && (
                <>
                  <SettingsRow label="Model installed">
                    <SettingsValue>
                      {aiStatus.model_installed === null ? 'Unknown' : aiStatus.model_installed ? 'Yes' : 'No'}
                    </SettingsValue>
                  </SettingsRow>
                  <SettingsRow label="Ollama installed">
                    <SettingsValue>{aiStatus.ollama_installed ? 'Yes' : 'No'}</SettingsValue>
                  </SettingsRow>
                  <SettingsRow label="Ollama running">
                    <SettingsValue>{aiStatus.ollama_running ? 'Yes' : 'No'}</SettingsValue>
                  </SettingsRow>
                  <SettingsRow label="Analysis queue">
                    <SettingsValue>
                      {aiStatus.pending} pending
                      {aiStatus.queue_paused ? ' · paused' : ''}
                      {aiStatus.queue_paused ? '' : aiStatus.worker_running ? ' · running' : ' · idle'}
                    </SettingsValue>
                  </SettingsRow>
                </>
              )}
            </>
          )}
        </SettingsSection>

        <SettingsSection
          title="Data"
          icon={<Database size={12} aria-hidden="true" />}
          stagger={3}
        >
          <SettingsRow label="Storage">
            <SettingsValue>Local SQLite (AppData)</SettingsValue>
          </SettingsRow>
          <SettingsRow label="Credentials">
            <StatusIndicator
              tone="ok"
              label="Encrypted with DPAPI"
              hint="Tokens are encrypted per Windows user and never leave this machine."
            />
          </SettingsRow>
        </SettingsSection>

        <SettingsSection
          title="Privacy"
          icon={<ShieldCheck size={12} aria-hidden="true" />}
          stagger={4}
        >
          <SettingsRow label="Analysis">
            <StatusIndicator
              tone="ok"
              label="All processing stays local"
              hint="No message content is sent anywhere."
            />
          </SettingsRow>
        </SettingsSection>

        <SettingsSection
          title="About"
          icon={<Info size={12} aria-hidden="true" />}
          stagger={5}
        >
          <SettingsRow label="Frontend build">
            <SettingsValue mono>{frontendBuild}</SettingsValue>
          </SettingsRow>
          <SettingsRow label="Backend build">
            <SettingsValue mono>{health?.build ?? 'Unavailable'}</SettingsValue>
          </SettingsRow>
        </SettingsSection>

        <p className="settings-footnote">
          <HardDrive size={12} aria-hidden="true" />
          Alfred stores everything locally and sends no telemetry.
        </p>
      </div>
    </div>
  );
}
