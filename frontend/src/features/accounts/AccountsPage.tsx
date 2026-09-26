import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Mail, RefreshCw, Unplug, UserCircle, KeyRound } from 'lucide-react';
import { accounts as fetchAccounts, connectGmail, syncAccount, deleteAccount } from '../../api/emails';
import type { EmailAccount } from '../../api/emails';
import { apiBase } from '../../api/client';
import { EmptyState, ErrorState } from '../../components/ui/States';
import { StatusIndicator } from '../../components/ui/Settings';

export function AccountsPage() {
  const queryClient = useQueryClient();

  const accountsQuery = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
  });
  const accounts = accountsQuery.data ?? [];

  const connectMutation = useMutation({
    mutationFn: connectGmail,
    onSuccess: (data) => {
      const width = 500;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;
      window.open(data.url, 'Alfred Connect', `width=${width},height=${height},left=${left},top=${top}`);
    },
  });

  const syncMutation = useMutation({
    mutationFn: (id: string) => syncAccount(id, false),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['accounts'] });
      void queryClient.invalidateQueries({ queryKey: ['emails'] });
      void queryClient.invalidateQueries({ queryKey: ['emailCounts'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  });

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data === 'auth_success') {
        queryClient.invalidateQueries({ queryKey: ['accounts'] });
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [queryClient]);

  const startConnect = () => connectMutation.mutate(`${apiBase()}/api/accounts/gmail/callback`);
  const connecting = connectMutation.isPending;

  return (
    <div className="page-scroll">
      <div className="page-container">
        <div className="reveal">
          <h1 className="page-title">Connected Accounts</h1>
          <p className="page-subtitle">
            Alfred reads your Gmail mailbox. Analysis stays on this device.
          </p>
        </div>

        {connectMutation.isError && (
          <ErrorState
            title="Couldn't start the Gmail connection"
            body="Alfred could not open the Google consent window. Check that Google credentials are configured, then try again."
            onRetry={startConnect}
            retrying={connecting}
          />
        )}

        {accountsQuery.isPending ? (
          <div className="account-list" aria-busy="true">
            {[1, 2].map((i) => (
              <div key={i} className="account-card">
                <div className="account-card-body">
                  <div className="skeleton skeleton-line-lg skeleton-w-40" />
                  <div className="skeleton skeleton-line-sm skeleton-w-70" />
                </div>
              </div>
            ))}
          </div>
        ) : accountsQuery.isError ? (
          <ErrorState
            title="Couldn't load your accounts"
            body="Alfred could not read the list of connected accounts. Nothing has changed."
            onRetry={() => void accountsQuery.refetch()}
            retrying={accountsQuery.isFetching}
          />
        ) : accounts.length === 0 ? (
          <EmptyState
            icon={UserCircle}
            title="No accounts connected"
            body="Connect a Gmail account to get started. Alfred never writes to your mailbox."
            action={
              <button type="button" className="btn btn-primary" onClick={startConnect} disabled={connecting}>
                <Mail size={14} aria-hidden="true" />
                {connecting ? 'Opening Google…' : 'Connect Gmail'}
              </button>
            }
          />
        ) : (
          <>
            <div className="account-list">
              {accounts.map((account) => (
                <AccountRow
                  key={account.id}
                  account={account}
                  syncing={syncMutation.isPending && syncMutation.variables === account.id}
                  syncFailed={syncMutation.isError && syncMutation.variables === account.id}
                  disconnecting={
                    deleteMutation.isPending && deleteMutation.variables === account.id
                  }
                  onSync={() => syncMutation.mutate(account.id)}
                  onReconnect={startConnect}
                  onDisconnect={() => deleteMutation.mutate(account.id)}
                />
              ))}
            </div>

            <div className="account-add">
              <button type="button" className="btn btn-surface" onClick={startConnect} disabled={connecting}>
                <Mail size={14} aria-hidden="true" />
                {connecting ? 'Opening Google…' : 'Add another Gmail account'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

type AccountRowProps = {
  account: EmailAccount;
  syncing: boolean;
  syncFailed: boolean;
  disconnecting: boolean;
  onSync: () => void;
  onReconnect: () => void;
  onDisconnect: () => void;
};

function AccountRow({
  account, syncing, syncFailed, disconnecting, onSync, onReconnect, onDisconnect,
}: AccountRowProps) {
  // The backend only ever writes 'connected' or 'error' (gmail.py sets 'error'
  // when the token refresh fails). Anything else is shown as reported rather
  // than guessed at.
  const connected = account.connection_status === 'connected';
  const needsAuth = !connected;

  return (
    <article className="account-card reveal">
      <div className="account-card-body">
        <div className="account-identity">
          <div className="account-name">{account.display_name || account.email_address}</div>
          {/* Only shown when it says something the name does not already say. */}
          {account.display_name && <div className="account-detail">{account.email_address}</div>}
        </div>

        <div className="account-facts">
          <div className="account-fact">
            <span className="account-fact-label">Provider</span>
            <span className="account-fact-value">{account.provider}</span>
          </div>
          <div className="account-fact">
            <span className="account-fact-label">Status</span>
            {connected ? (
              <StatusIndicator tone="ok" label="Connected" hint="This mailbox is linked to Alfred." />
            ) : (
              <StatusIndicator
                tone="danger"
                label="Authentication required"
                hint="Alfred needs to sign in to this mailbox again."
              />
            )}
          </div>
          <div className="account-fact">
            <span className="account-fact-label">Last sync</span>
            <span className="account-fact-value">
              {account.last_sync_at ? new Date(account.last_sync_at).toLocaleString() : 'Never'}
            </span>
          </div>
          {account.backfill && (
            <div className="account-fact">
              <span className="account-fact-label">Older mail</span>
              <span className="account-fact-value">
                {backfillSummary(account)}
              </span>
            </div>
          )}
        </div>
      </div>

      {syncFailed && (
        <p className="account-inline-error" role="alert">
          Sync failed. Your existing mail is unaffected.
        </p>
      )}

      <div className="account-actions">
        {needsAuth ? (
          <button type="button" className="btn btn-primary btn-sm" onClick={onReconnect}>
            <KeyRound size={13} aria-hidden="true" />
            Reconnect
          </button>
        ) : (
          <button
            type="button"
            className="btn btn-surface btn-sm"
            onClick={onSync}
            disabled={syncing}
            aria-busy={syncing || undefined}
          >
            {syncing ? (
              <span className="btn-spinner" aria-hidden="true" />
            ) : (
              <RefreshCw size={13} aria-hidden="true" />
            )}
            {syncing ? 'Syncing…' : 'Sync now'}
          </button>
        )}
        <button
          type="button"
          className="btn btn-danger btn-sm"
          onClick={onDisconnect}
          disabled={disconnecting}
          aria-busy={disconnecting || undefined}
        >
          <Unplug size={13} aria-hidden="true" />
          {disconnecting ? 'Disconnecting…' : 'Disconnect'}
        </button>
      </div>
    </article>
  );
}

/** Read-only. The resume and pause controls live in the mail pane, not here. */
function backfillSummary(account: EmailAccount): string {
  const b = account.backfill;
  if (!b) return 'Unknown';
  if (b.state === 'complete') return 'Complete';
  if (b.state === 'failed') return 'Failed';
  if (b.state === 'paused') return b.imported > 0 ? `Paused · ${b.imported} imported` : 'Paused';
  if (b.state === 'running') {
    return b.remaining_estimate !== null
      ? `Importing · about ${b.remaining_estimate} left`
      : 'Importing';
  }
  return b.imported > 0 ? `${b.imported} imported` : 'Not started';
}
