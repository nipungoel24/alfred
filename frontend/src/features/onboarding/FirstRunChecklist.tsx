import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Check, CircleDashed, Loader2, X } from 'lucide-react';
import { accounts as fetchAccounts, analysisStatus } from '../../api/emails';
import type { AppPage } from '../../layout/IconRail';
import { aiStateMeta } from '../../lib/aiState';

const DISMISS_KEY = 'alfred.onboarding.dismissed';

type StepState = 'done' | 'active' | 'pending';

type Step = {
  id: string;
  title: string;
  body: string;
  action: { label: string; page: AppPage };
  state: StepState;
};

/**
 * First-run checklist.
 *
 * It reports only what the backend actually says: whether an account is
 * connected, whether Ollama is running, and whether the model passed its
 * readiness check. Nothing here is a hardcoded "step 2 of 3" — a machine
 * that already has Ollama and a model simply shows those steps done, and a
 * machine with no account shows the account step first.
 */
export function FirstRunChecklist({ onNavigate }: { onNavigate: (page: AppPage) => void }) {
  const [dismissed, setDismissed] = useState(
    () => localStorage.getItem(DISMISS_KEY) === '1',
  );

  const accountsQuery = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  // Poll only while a step is still outstanding, so a finished setup is quiet.
  const statusQuery = useQuery({
    queryKey: ['analysisStatus'],
    queryFn: analysisStatus,
    refetchInterval: (query) => {
      const state = query.state.data?.state;
      return state === 'ready' ? false : 10_000;
    },
  });

  if (dismissed) return null;
  // Nothing to say until both answers are in: guessing would show a
  // checklist that flickers between states.
  if (accountsQuery.isPending || statusQuery.isPending) return null;
  if (accountsQuery.isError || statusQuery.isError) return null;

  const connected = (accountsQuery.data ?? []).length > 0;
  const status = statusQuery.data;
  const ollamaRunning = status.ollama_running;
  const modelReady = status.state === 'ready';

  const steps: Step[] = [
    {
      id: 'account',
      title: 'Connect your Gmail account',
      body: connected
        ? 'Alfred reads this mailbox locally and never writes to it.'
        : 'Alfred needs read access to your Gmail mailbox. Analysis stays on this device.',
      action: { label: connected ? 'Manage accounts' : 'Connect Gmail', page: 'accounts' },
      state: connected ? 'done' : 'active',
    },
    {
      id: 'ollama',
      title: 'Make sure Ollama is running',
      body: ollamaRunning
        ? 'The local runtime is up.'
        : status.ollama_installed
          ? 'Ollama is installed but not running. Alfred can start it for you from Settings.'
          : 'Install Ollama from ollama.com, then return here. Your mailbox still works without it.',
      action: { label: 'Open Settings', page: 'settings' },
      state: ollamaRunning ? 'done' : connected ? 'active' : 'pending',
    },
    {
      id: 'model',
      title: 'Download a local model',
      body: modelReady
        ? 'Local AI is ready. Summaries and actions are produced on this machine.'
        : aiStateMeta(status.state).hint,
      action: { label: 'Open Settings', page: 'settings' },
      state: modelReady ? 'done' : ollamaRunning ? 'active' : 'pending',
    },
  ];

  const allDone = steps.every((s) => s.state === 'done');

  const dismiss = () => {
    localStorage.setItem(DISMISS_KEY, '1');
    setDismissed(true);
  };

  return (
    <section className="firstrun" aria-labelledby="firstrun-title">
      <div className="firstrun-head">
        <h2 id="firstrun-title" className="firstrun-title">Finish setting up Alfred</h2>
        {/* A finished checklist is still dismissible: the user may prefer
            to leave it and come back, and hiding it is not a lie. */}
        <button type="button" className="firstrun-dismiss" onClick={dismiss} aria-label="Dismiss setup checklist">
          <X size={14} aria-hidden="true" />
        </button>
      </div>

      <ol className="firstrun-steps">
        {steps.map((step) => (
          <li key={step.id} className={`firstrun-step is-${step.state}`}>
            <span className="firstrun-marker" aria-hidden="true">
              {step.state === 'done' ? (
                <Check size={13} />
              ) : step.state === 'active' && status.state === 'model_downloading' && step.id === 'model' ? (
                <Loader2 size={13} className="firstrun-spin" />
              ) : (
                <CircleDashed size={13} />
              )}
            </span>
            <div className="firstrun-body">
              <p className="firstrun-step-title">{step.title}</p>
              <p className="firstrun-step-detail">{step.body}</p>
            </div>
            {step.state !== 'done' && (
              <button
                type="button"
                className="btn btn-surface btn-sm"
                onClick={() => onNavigate(step.action.page)}
              >
                {step.action.label}
              </button>
            )}
          </li>
        ))}
      </ol>

      {allDone && (
        <p className="firstrun-done">Setup complete. Your mail is ready.</p>
      )}
    </section>
  );
}
