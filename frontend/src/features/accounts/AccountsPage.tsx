import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accounts as fetchAccounts, connectGmail, syncAccount, deleteAccount } from '../../api/emails';
import { apiBase } from '../../api/client';
import { Mail, RefreshCw, Unplug, UserCircle } from 'lucide-react';

export function AccountsPage() {
  const queryClient = useQueryClient();

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
  });

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

  return (
    <div className="page-scroll">
      <div style={{ maxWidth: 760, margin: '0 auto', padding: 'var(--space-6) var(--space-6) var(--space-10)' }}>
        <div className="reveal">
          <h1 className="page-title" style={{ fontSize: 'var(--text-xl)' }}>Connected Accounts</h1>
          <p className="page-subtitle" style={{ marginBottom: 'var(--space-5)' }}>
            Alfred reads your Gmail mailbox. Analysis stays on this device.
          </p>
        </div>

        {connectMutation.isError && (
          <div className="banner banner-danger" style={{ marginBottom: 'var(--space-4)' }}>
            Failed to connect account. Ensure Google credentials are configured.
          </div>
        )}

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {[1, 2].map(i => <div key={i} className="skeleton" style={{ height: 84 }} />)}
          </div>
        ) : accounts.length === 0 ? (
          <div className="empty-state" style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
            <UserCircle aria-hidden="true" />
            <p>No accounts connected. Connect a Gmail account to get started.</p>
            <button
              type="button"
              className="btn btn-primary"
              style={{ marginTop: 'var(--space-3)' }}
              onClick={() => connectMutation.mutate(`${apiBase()}/api/accounts/gmail/callback`)}
              disabled={connectMutation.isPending}
            >
              <Mail size={14} aria-hidden="true" />
              {connectMutation.isPending ? 'Connecting…' : 'Connect Gmail'}
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {accounts.map(acc => (
              <div key={acc.id} className="account-card reveal">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', minWidth: 0 }}>
                  <div style={{
                    width: 38, height: 38, borderRadius: 'var(--radius-md)',
                    background: 'var(--accent-soft)', display: 'grid', placeItems: 'center', flexShrink: 0,
                  }}>
                    <Mail size={17} style={{ color: 'var(--accent)' }} aria-hidden="true" />
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-md)' }}>
                      {acc.display_name || 'Gmail'}
                    </div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 2, flexWrap: 'wrap' }}>
                      <span>{acc.email_address}</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                        <span className={`status-dot ${acc.connection_status === 'connected' ? 'online' : 'offline'}`} />
                        {acc.connection_status}
                      </span>
                      <span>Last sync: {acc.last_sync_at ? new Date(acc.last_sync_at).toLocaleString() : 'Never'}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 'var(--space-2)', flexShrink: 0 }}>
                  <button
                    type="button"
                    className="btn btn-surface btn-sm"
                    onClick={() => syncMutation.mutate(acc.id)}
                    disabled={syncMutation.isPending && syncMutation.variables === acc.id}
                  >
                    {syncMutation.isPending && syncMutation.variables === acc.id
                      ? <span className="btn-spinner" aria-hidden="true" />
                      : <RefreshCw size={13} aria-hidden="true" />}
                    {syncMutation.isPending && syncMutation.variables === acc.id ? 'Syncing…' : 'Sync Now'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => deleteMutation.mutate(acc.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Unplug size={13} aria-hidden="true" />
                    Disconnect
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
