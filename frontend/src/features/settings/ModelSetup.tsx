import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Download, X } from 'lucide-react';
import {
  aiModel,
  analysisStatus,
  selectAiModel,
  pullAiModel,
  cancelAiModelPull,
} from '../../api/emails';
import { SettingsRow, SettingsValue, StatusIndicator } from '../../components/ui/Settings';
import { aiStateMeta } from '../../lib/aiState';

/**
 * Model selection and download.
 *
 * Two queries, deliberately: `analysisStatus` carries the state machine and
 * live progress, `aiModel` carries the installed list and the machine
 * preflight. Polling the status query only while a download runs keeps an
 * idle Settings page quiet.
 */
export function ModelSetup() {
  const queryClient = useQueryClient();
  const [draftModel, setDraftModel] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['analysisStatus'],
    queryFn: analysisStatus,
    refetchInterval: (query) => {
      const state = query.state.data?.state;
      return state === 'model_downloading' ? 1000 : 10_000;
    },
  });
  const modelQuery = useQuery({ queryKey: ['aiModel'], queryFn: aiModel });

  const status = statusQuery.data;
  const info = modelQuery.data;
  const pull = status?.pull ?? null;
  const downloading = status?.state === 'model_downloading' || pull?.running === true;

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ['analysisStatus'] });
    void queryClient.invalidateQueries({ queryKey: ['aiModel'] });
  };

  const selectMutation = useMutation({
    mutationFn: selectAiModel,
    onSuccess: invalidate,
  });
  const pullMutation = useMutation({
    mutationFn: (model?: string) => pullAiModel(model),
    onSuccess: invalidate,
  });
  const cancelMutation = useMutation({
    mutationFn: cancelAiModelPull,
    onSuccess: invalidate,
  });

  if (statusQuery.isPending || modelQuery.isPending) {
    return (
      <div className="settings-skeleton" aria-busy="true">
        <div className="skeleton skeleton-line-md skeleton-w-full" />
        <div className="skeleton skeleton-line-md skeleton-w-80" />
      </div>
    );
  }

  if (statusQuery.isError || modelQuery.isError) {
    return (
      <SettingsRow label="Model">
        <SettingsValue>Unavailable — could not read the local AI runtime.</SettingsValue>
      </SettingsRow>
    );
  }

  const effective = draftModel ?? status?.model ?? info?.model ?? '';
  const installedNames = (info?.local_models ?? []).map((m) => m.name);
  const isInstalled = info?.installed === true;

  const applyModel = (model: string) => {
    setDraftModel(model);
    selectMutation.mutate(model);
  };

  return (
    <>
      <SettingsRow
        label="Model"
        hint="Summaries are produced by this model, on this machine."
      >
        <div className="model-picker">
          <select
            className="model-field model-select"
            value={installedNames.includes(effective) ? effective : ''}
            onChange={(e) => applyModel(e.target.value)}
            disabled={downloading || selectMutation.isPending}
            aria-label="Local model"
          >
            {!installedNames.includes(effective) && (
              <option value="">{effective || 'None selected'}</option>
            )}
            {installedNames.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
          <input
            className="model-field model-input"
            type="text"
            value={effective}
            onChange={(e) => setDraftModel(e.target.value)}
            onBlur={() => {
              if (draftModel && draftModel !== status?.model) applyModel(draftModel);
            }}
            placeholder="qwen3:4b"
            disabled={downloading || selectMutation.isPending}
            aria-label="Model tag"
          />
        </div>
      </SettingsRow>

      <SettingsRow label="Installed size">
        {/* Ollama reports this per model; an uninstalled model has no
            knowable size locally, and is named as such rather than guessed. */}
        <SettingsValue mono>{info?.human_size ?? 'Unknown'}</SettingsValue>
      </SettingsRow>

      <SettingsRow label="Free disk space">
        <SettingsValue mono>
          {info ? `${info.preflight.human_disk_free} on ${info.preflight.disk_path}` : 'Unknown'}
        </SettingsValue>
      </SettingsRow>

      <SettingsRow label="Memory">
        <SettingsValue mono>
          {info?.preflight.human_ram ?? 'Unknown'}
          {info?.preflight.ram_sufficient === false ? ' — below the 4 GB needed' : ''}
        </SettingsValue>
      </SettingsRow>

      <SettingsRow label="Status">
        <StatusIndicator
          tone={aiStateMeta(status?.state).tone}
          label={aiStateMeta(status?.state).word}
          hint={aiStateMeta(status?.state).hint}
        />
      </SettingsRow>

      {/* A preflight that blocks is reported before anything is offered. */}
      {info?.preflight.blocking && info.preflight.guidance && (
        <SettingsRow label="Before downloading">
          <p className="model-guidance" role="alert">{info.preflight.guidance}</p>
        </SettingsRow>
      )}

      {pull && (downloading || pull.error) && (
        <SettingsRow label="Download">
          <ModelDownload
            pull={pull}
            downloading={downloading}
            onCancel={() => cancelMutation.mutate()}
            cancelling={cancelMutation.isPending}
          />
        </SettingsRow>
      )}

      {!downloading && !isInstalled && !info?.preflight.blocking && (
        <SettingsRow label="Download">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => pullMutation.mutate(undefined)}
            disabled={pullMutation.isPending}
            aria-busy={pullMutation.isPending || undefined}
          >
            <Download size={13} aria-hidden="true" />
            {pullMutation.isPending ? 'Starting…' : `Download ${effective}`}
          </button>
          {pullMutation.isError && (
            <p className="model-guidance" role="alert">
              {pullMutation.error instanceof Error
                ? pullMutation.error.message
                : 'The download could not be started.'}
            </p>
          )}
        </SettingsRow>
      )}
    </>
  );
}

type ModelDownloadProps = {
  pull: NonNullable<Awaited<ReturnType<typeof analysisStatus>>['pull']>;
  downloading: boolean;
  onCancel: () => void;
  cancelling: boolean;
};

function ModelDownload({ pull, downloading, onCancel, cancelling }: ModelDownloadProps) {
  // fraction is null until Ollama announces a total, so the bar is
  // indeterminate rather than pinned to a number that is not known yet.
  const percent = pull.fraction === null ? null : Math.round(pull.fraction * 100);

  return (
    <div className="model-download">
      <div
        className={`model-download-track${percent === null ? ' indeterminate' : ''}`}
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent ?? undefined}
        aria-label="Model download progress"
      >
        <div
          className="model-download-fill"
          style={percent === null ? undefined : { width: `${percent}%` }}
        />
      </div>
      <div className="model-download-meta">
        <span>
          {downloading
            ? pull.human_total
              ? `${pull.human_completed ?? '0'} of ${pull.human_total}`
              : pull.human_completed
                ? `${pull.human_completed} pulled`
                : 'Starting download…'
            : pull.error ?? 'The download did not finish.'}
        </span>
        {downloading && (
          <button
            type="button"
            className="btn btn-surface btn-sm"
            onClick={onCancel}
            disabled={cancelling}
            aria-busy={cancelling || undefined}
          >
            <X size={13} aria-hidden="true" />
            {cancelling ? 'Cancelling…' : 'Cancel'}
          </button>
        )}
      </div>
    </div>
  );
}
