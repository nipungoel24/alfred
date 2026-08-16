import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accounts as fetchAccounts, connectGmail, syncAccount, deleteAccount } from '../../api/emails';
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
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['emails'] });
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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Connected Accounts</h1>
          <div className="page-subtitle">Manage your email providers</div>
        </div>
        {accounts.length === 0 && (
          <button
            className="btn btn-primary"
            onClick={() => connectMutation.mutate('http://127.0.0.1:8765/api/accounts/gmail/callback')}
            disabled={connectMutation.isPending}
          >
            <Mail size={14} />
            {connectMutation.isPending ? 'Connecting...' : 'Connect Gmail'}
          </button>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '0 var(--space-6)', paddingBottom: 'var(--space-6)' }}>
        {connectMutation.isError && (
          <div className="banner banner-danger">
            Failed to connect account. Ensure Google credentials are configured.
          </div>
        )}

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {[1,2].map(i => <div key={i} className="skeleton" style={{ height: 90, borderRadius: 'var(--radius-lg)' }} />)}
          </div>
        ) : accounts.length === 0 ? (
          <div className="empty-state">
            <UserCircle />
            <p>No accounts connected. Connect a Gmail account to get started.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {accounts.map(acc => (
              <div key={acc.id} className="account-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 'var(--radius-md)',
                    background: 'var(--accent-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Mail size={18} style={{ color: 'var(--accent)' }} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-md)' }}>
                      {acc.display_name || 'Gmail'}
                    </div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 2 }}>
                      <span>{acc.email_address}</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span className={`status-dot ${acc.connection_status === 'connected' ? 'online' : 'offline'}`} />
                        {acc.connection_status}
                      </span>
                      <span>Last sync: {acc.last_sync_at ? new Date(acc.last_sync_at).toLocaleString() : 'Never'}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                  <button
                    className="btn btn-surface"
                    onClick={() => syncMutation.mutate(acc.id)}
                    disabled={syncMutation.isPending && syncMutation.variables === acc.id}
                  >
                    <RefreshCw size={14} style={syncMutation.isPending && syncMutation.variables === acc.id ? { animation: 'spin 1s linear infinite' } : undefined} />
                    {syncMutation.isPending && syncMutation.variables === acc.id ? 'Syncing...' : 'Sync Now'}
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => deleteMutation.mutate(acc.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Unplug size={14} />
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
