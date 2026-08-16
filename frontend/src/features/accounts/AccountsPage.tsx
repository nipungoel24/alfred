import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accounts as fetchAccounts, connectGmail, syncAccount, deleteAccount } from '../../api/emails';

export function AccountsPage() {
  const queryClient = useQueryClient();
  
  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
  });

  const connectMutation = useMutation({
    mutationFn: connectGmail,
    onSuccess: (data) => {
      // Open OAuth popup
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
      // Background analysis will trigger SSE progress events which will invalidate queries
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['emails'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  });

  useEffect(() => {
    // Listen for auth_success message from popup
    const handleMessage = (event: MessageEvent) => {
      if (event.data === 'auth_success') {
        queryClient.invalidateQueries({ queryKey: ['accounts'] });
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [queryClient]);

  if (isLoading) return <div className="p-8 text-center text-muted">Loading accounts...</div>;

  return (
    <div className="content p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1>Connected Accounts</h1>
        <button
          className="btn btn-primary"
          onClick={() => connectMutation.mutate('http://127.0.0.1:8765/api/accounts/gmail/callback')}
          disabled={connectMutation.isPending}
        >
          {connectMutation.isPending ? 'Connecting...' : 'Connect Gmail'}
        </button>
      </div>
      
      {connectMutation.isError && (
        <div className="text-danger mb-4 p-4 bg-danger/10 rounded">
          Failed to connect account. Ensure Google credentials are in .env
        </div>
      )}

      {accounts.length === 0 ? (
        <div className="panel p-8 text-center text-muted">
          No accounts connected. Connect a Gmail account to start.
        </div>
      ) : (
        <div className="space-y-4">
          {accounts.map(acc => (
            <div key={acc.id} className="panel p-6 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold mb-1">{acc.display_name || acc.email_address}</h3>
                <div className="text-muted text-sm flex gap-4">
                  <span>{acc.email_address}</span>
                  <span className={acc.connection_status === 'connected' ? 'text-primary' : 'text-danger'}>
                    {acc.connection_status.toUpperCase()}
                  </span>
                  <span>Last sync: {acc.last_sync_at ? new Date(acc.last_sync_at).toLocaleString() : 'Never'}</span>
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  className="btn bg-[#2d2d30] text-white hover:bg-[#3d3d40]"
                  onClick={() => syncMutation.mutate(acc.id)}
                  disabled={syncMutation.isPending && syncMutation.variables === acc.id}
                >
                  {syncMutation.isPending && syncMutation.variables === acc.id ? 'Syncing...' : 'Sync Now'}
                </button>
                <button
                  className="btn bg-danger/20 text-danger hover:bg-danger/30"
                  onClick={() => deleteMutation.mutate(acc.id)}
                  disabled={deleteMutation.isPending}
                >
                  Disconnect
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
