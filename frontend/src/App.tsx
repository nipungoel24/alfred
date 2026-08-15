import { useEffect, useState } from 'react';
import {
  briefing,
  emails,
  analyze,
  draft,
  accounts,
  connectGmail,
  syncAccount,
  deleteAccount,
  tasks,
  toggleTask,
  deleteTask,
  Email,
  Briefing,
  EmailAccount,
  Task
} from './api/emails';
import { PriorityBadge } from './components/PriorityBadge';
import './styles.css';

const nav = ['Overview', 'Inbox', 'Tasks', 'Accounts', 'Settings'];

export default function App() {
  const [data, setData] = useState<Email[]>([]);
  const [brief, setBrief] = useState<Briefing>();
  const [accountsList, setAccountsList] = useState<EmailAccount[]>([]);
  const [taskList, setTaskList] = useState<Task[]>([]);
  const [selected, setSelected] = useState<Email>();
  const [selectedDraft, setSelectedDraft] = useState<string>('');
  const [generatingDraft, setGeneratingDraft] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState('Overview');
  
  // Filters for Inbox
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [needsReplyFilter, setNeedsReplyFilter] = useState<boolean | null>(null);
  const [activeAccount, setActiveAccount] = useState('all');
  
  // Sync state tracker
  const [syncingId, setSyncingId] = useState<string | null>(null);

  const load = async () => {
    try {
      // Load accounts
      const accs = await accounts();
      setAccountsList(accs);

      // Load tasks
      const ts = await tasks();
      setTaskList(ts);

      // Load emails (with filters)
      const filteredEmails = await emails(
        searchQuery,
        priorityFilter,
        needsReplyFilter,
        activeAccount === 'all' ? '' : activeAccount
      );
      setData(filteredEmails);

      // Load briefing
      const b = await briefing();
      setBrief(b);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  useEffect(() => {
    load();
    // Poll accounts/tasks every 10 seconds to reflect sync changes in background
    const interval = setInterval(() => {
      load();
    }, 10000);
    return () => clearInterval(interval);
  }, [searchQuery, priorityFilter, needsReplyFilter, activeAccount]);

  const handleSync = async (accountId: string) => {
    setSyncingId(accountId);
    setError('');
    try {
      const res = await syncAccount(accountId);
      // Run bulk analyze on new emails in background
      await load();
      alert(`Sync completed! Imported ${res.imported} new messages.`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSyncingId(null);
    }
  };

  const handleConnectGmail = async () => {
    setError('');
    try {
      const redirectUri = "http://localhost:8765/api/accounts/gmail/callback";
      const res = await connectGmail(redirectUri);
      window.open(res.url, '_blank');
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleDisconnect = async (accountId: string) => {
    if (!confirm('Are you sure you want to disconnect this email account? This will delete its locally cached emails.')) {
      return;
    }
    setError('');
    try {
      await deleteAccount(accountId);
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleToggleTask = async (taskId: string) => {
    try {
      await toggleTask(taskId);
      // Fast state update
      setTaskList(prev =>
        prev.map(t => (t.id === taskId ? { ...t, status: t.status === 'pending' ? 'completed' : 'pending' } : t))
      );
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTaskList(prev => prev.filter(t => t.id !== taskId));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const runAnalysis = async (emailId: string) => {
    setError('');
    try {
      await analyze(emailId);
      await load();
      // Update selected modal details if open
      const updatedEmail = await emails();
      const current = updatedEmail.find(e => e.id === emailId);
      if (current) {
        setSelected(current);
      }
    } catch (x) {
      setError((x as Error).message);
    }
  };

  const handleGenerateDraft = async (emailId: string) => {
    setGeneratingDraft(true);
    setSelectedDraft('');
    try {
      const res = await draft(emailId);
      setSelectedDraft(res.draft);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setGeneratingDraft(false);
    }
  };

  const handleOpenEmail = (emailId: string) => {
    const email = data.find(e => e.id === emailId);
    if (email) {
      setSelected(email);
      setSelectedDraft('');
    } else {
      // Fallback load details
      emails().then(all => {
        const found = all.find(e => e.id === emailId);
        if (found) {
          setSelected(found);
          setSelectedDraft('');
        }
      });
    }
  };

  return (
    <main>
      <aside>
        <div className="brand">
          ALFRED <small>PRIVATE INBOX</small>
        </div>
        {nav.map(n => (
          <button
            className={page === n ? 'active' : ''}
            onClick={() => setPage(n)}
            key={n}
          >
            {n === 'Tasks' ? `Tasks (${taskList.filter(t => t.status === 'pending').length})` : n}
          </button>
        ))}
        <p className="local">● Local-first AI<br />Ollama only</p>
      </aside>

      <section className="content">
        {error && <div className="error">{error}</div>}

        {/* 1. OVERVIEW PAGE */}
        {page === 'Overview' && (
          <>
            <header>
              <p className="eyebrow">YOUR PERSONAL BRIEFING</p>
              <h1>Here’s what needs your attention.</h1>
              <p>{brief?.executive_summary || 'Loading your private briefing…'}</p>
            </header>

            <div className="metrics">
              <div className="glass metric">
                <span>Total Emails</span>
                <strong>{brief?.total_emails ?? '—'}</strong>
              </div>
              <div className="glass metric">
                <span>Urgent</span>
                <strong>{brief?.urgent_count ?? '—'}</strong>
              </div>
              <div className="glass metric">
                <span>Needs Reply</span>
                <strong>{brief?.needs_reply_count ?? '—'}</strong>
              </div>
              <div className="glass metric">
                <span>Pending Tasks</span>
                <strong>{taskList.filter(t => t.status === 'pending').length}</strong>
              </div>
              <div className="glass metric">
                <span>Deadlines</span>
                <strong>{brief?.deadline_count ?? '—'}</strong>
              </div>
            </div>

            <h2>Top attention</h2>
            <div className="attention">
              {brief?.top_attention_items.map(i => (
                <article className="glass" key={i.email_id}>
                  <div>
                    <PriorityBadge priority={i.priority} />
                    <h3>{i.subject}</h3>
                    <b>{i.sender}</b>
                    <p>{i.short_summary}</p>
                    <small>Why it matters: {i.why_it_matters}</small>
                  </div>
                  <button onClick={() => handleOpenEmail(i.email_id)}>Open Email</button>
                </article>
              ))}
              {(!brief || brief.top_attention_items.length === 0) && (
                <p style={{ color: '#8990b6' }}>No urgent items currently pending in your inbox.</p>
              )}
            </div>

            {brief && brief.important_updates.length > 0 && (
              <>
                <h2>Important updates</h2>
                <div className="glass" style={{ padding: '20px' }}>
                  {brief.important_updates.map((update, idx) => (
                    <p key={idx} style={{ margin: '8px 0', borderBottom: '1px solid #ffffff08', paddingBottom: '8px' }}>
                      • {update}
                    </p>
                  ))}
                </div>
              </>
            )}
          </>
        )}

        {/* 2. INBOX PAGE */}
        {page === 'Inbox' && (
          <>
            <header>
              <p className="eyebrow">SYNCED MAILBOX</p>
              <h1>Inbox</h1>
            </header>

            <div className="inbox-header">
              <input
                type="text"
                className="search-input"
                placeholder="Search subject, sender, body..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />

              <select
                className="filter-select"
                value={activeAccount}
                onChange={e => setActiveAccount(e.target.value)}
              >
                <option value="all">All Accounts</option>
                {accountsList.map(acc => (
                  <option key={acc.id} value={acc.id}>{acc.email_address}</option>
                ))}
              </select>

              <select
                className="filter-select"
                value={priorityFilter}
                onChange={e => setPriorityFilter(e.target.value)}
              >
                <option value="">All Priorities</option>
                <option value="urgent">Urgent</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              <select
                className="filter-select"
                value={needsReplyFilter === null ? '' : String(needsReplyFilter)}
                onChange={e => {
                  const val = e.target.value;
                  setNeedsReplyFilter(val === '' ? null : val === 'true');
                }}
              >
                <option value="">Reply Status</option>
                <option value="true">Needs Reply</option>
                <option value="false">Read-only</option>
              </select>
            </div>

            <div className="inbox glass">
              {data.map(e => (
                <button className="email-row" onClick={() => handleOpenEmail(e.id)} key={e.id}>
                  <PriorityBadge priority={e.analysis?.priority || 'low'} />
                  <span>
                    <b>{e.sender_name || e.sender}</b>
                    <strong>{e.subject}</strong>
                    <small>{e.analysis?.short_summary || e.body.slice(0, 100) + '...'}</small>
                  </span>
                  {!e.analysis ? (
                    <i onClick={(x) => { x.stopPropagation(); runAnalysis(e.id); }}>Analyze</i>
                  ) : (
                    e.analysis.needs_reply && <i style={{ background: '#6a4bf730', color: '#c2acef' }}>Needs Reply</i>
                  )}
                </button>
              ))}
              {data.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', color: '#8990b6' }}>
                  No emails match your filter or search settings. Connect a Gmail account or import a CSV file to sync emails.
                </div>
              )}
            </div>
          </>
        )}

        {/* 3. TASKS PAGE */}
        {page === 'Tasks' && (
          <>
            <header>
              <p className="eyebrow">DERIVED ACTION ITEMS</p>
              <h1>Smart Tasks</h1>
            </header>

            <div className="glass">
              {taskList.map(t => (
                <div className={`task-item ${t.status === 'completed' ? 'completed' : ''}`} key={t.id}>
                  <input
                    type="checkbox"
                    className="task-checkbox"
                    checked={t.status === 'completed'}
                    onChange={() => handleToggleTask(t.id)}
                  />
                  <div className="task-content">
                    <span style={{ fontSize: '15px', fontWeight: '500' }}>{t.title}</span>
                    <div className="task-meta">
                      {t.due_at && <span>📅 Due: {t.due_at}</span>}
                      {t.priority && (
                        <span className={`priority ${t.priority}`} style={{ scale: '0.85', transformOrigin: 'left' }}>
                          {t.priority}
                        </span>
                      )}
                      {t.source_email_id && (
                        <span
                          style={{ cursor: 'pointer', textDecoration: 'underline', color: '#a999e9' }}
                          onClick={() => handleOpenEmail(t.source_email_id!)}
                        >
                          Source Email
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="task-actions">
                    <button className="btn-danger" style={{ padding: '4px 8px', fontSize: '12px' }} onClick={() => handleDeleteTask(t.id)}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
              {taskList.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', color: '#8990b6' }}>
                  No tasks found. Alfred extracts action items and deadlines automatically when emails are analyzed.
                </div>
              )}
            </div>
          </>
        )}

        {/* 4. ACCOUNTS PAGE */}
        {page === 'Accounts' && (
          <>
            <header>
              <p className="eyebrow">MAIL PROVIDERS</p>
              <h1>Connected Accounts</h1>
            </header>

            <div style={{ marginBottom: '20px' }}>
              <button className="btn-primary" onClick={handleConnectGmail}>
                Connect Gmail Account
              </button>
            </div>

            <div>
              {accountsList.map(acc => (
                <div className="glass account-card" key={acc.id}>
                  <div className="account-info">
                    <h3>{acc.display_name || acc.email_address}</h3>
                    <p>Provider: {acc.provider.toUpperCase()} | {acc.email_address}</p>
                    <p style={{ fontSize: '11px', color: '#8990b6' }}>
                      Last Sync: {acc.last_sync_at ? new Date(acc.last_sync_at).toLocaleString() : 'Never'}
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <span className={`status-badge status-${acc.connection_status}`}>
                      {acc.connection_status}
                    </span>
                    <button
                      className="btn-primary"
                      style={{ margin: 0 }}
                      disabled={syncingId === acc.id}
                      onClick={() => handleSync(acc.id)}
                    >
                      {syncingId === acc.id ? (
                        <>
                          <span className="sync-loader">⏳</span> Syncing...
                        </>
                      ) : (
                        'Sync Now'
                      )}
                    </button>
                    <button className="btn-danger" onClick={() => handleDisconnect(acc.id)}>
                      Disconnect
                    </button>
                  </div>
                </div>
              ))}

              {accountsList.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', color: '#8990b6' }} className="glass">
                  No connected mailboxes found. Click "Connect Gmail" to sync your Gmail messages securely.
                </div>
              )}
            </div>
          </>
        )}

        {/* 5. SETTINGS PAGE */}
        {page === 'Settings' && (
          <>
            <header>
              <p className="eyebrow">ALFRED CORE CONFIG</p>
              <h1>Settings</h1>
            </header>

            <div className="glass" style={{ padding: '30px', display: 'grid', gap: '20px' }}>
              <div>
                <h3 style={{ margin: '0 0 6px' }}>Local AI Settings</h3>
                <p style={{ margin: '4px 0', color: '#aeb6dc' }}>Model: qwen3:4b</p>
                <p style={{ margin: '4px 0', color: '#aeb6dc' }}>Ollama Base URL: http://127.0.0.1:11434</p>
              </div>

              <div>
                <h3 style={{ margin: '0 0 6px' }}>Local Storage Settings</h3>
                <p style={{ margin: '4px 0', color: '#aeb6dc' }}>Database: SQLite3</p>
                <p style={{ margin: '4px 0', color: '#aeb6dc' }}>Database Path: C:\Users\Nipun\AppData\Local\Alfred\alfred.sqlite3</p>
              </div>

              <div>
                <h3 style={{ margin: '0 0 6px' }}>Privacy & Trust Policy</h3>
                <p style={{ margin: '4px 0', color: '#bfc3df', lineHeight: '1.6' }}>
                  Alfred fetches your email messages directly from Google's Gmail API, but all AI analyses, key metrics briefings, and reply drafts are processed exclusively <b>locally on this computer</b> using Ollama. No email content is ever uploaded to OpenAI, Anthropic, or any cloud intelligence fallback.
                </p>
              </div>
            </div>
          </>
        )}

        {/* EMAIL DETAILS MODAL */}
        {selected && (
          <div className="modal" role="dialog">
            <article className="detail glass">
              <button className="close" onClick={() => setSelected(undefined)}>×</button>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <PriorityBadge priority={selected.analysis?.priority || 'low'} />
                {selected.received_at && (
                  <span style={{ fontSize: '12px', color: '#8990b6' }}>
                    {new Date(selected.received_at).toLocaleString()}
                  </span>
                )}
              </div>

              <h2>{selected.subject}</h2>
              <p style={{ margin: '4px 0' }}>From: <b>{selected.sender_name || selected.sender}</b> ({selected.sender})</p>
              {selected.recipients.length > 0 && (
                <p style={{ margin: '4px 0', fontSize: '13px', color: '#bfc3df' }}>
                  To: {selected.recipients.join(', ')}
                </p>
              )}

              <div className="body">{selected.body}</div>

              {selected.analysis ? (
                <>
                  <div className="detail-section">
                    <h4>Alfred's Insight</h4>
                    <p><b>Summary:</b> {selected.analysis.short_summary}</p>
                    <p><b>Reasoning:</b> {selected.analysis.reason_for_priority}</p>
                  </div>

                  {selected.analysis.action_items.length > 0 && (
                    <div className="detail-section">
                      <h4>Action Items</h4>
                      {selected.analysis.action_items.map((a, i) => (
                        <p key={i} style={{ margin: '4px 0' }}>
                          • {a.description} {a.owner ? `(Owner: ${a.owner})` : ''} {a.deadline ? `[Due: ${a.deadline}]` : ''}
                        </p>
                      ))}
                    </div>
                  )}

                  {selected.analysis.deadlines.length > 0 && (
                    <div className="detail-section">
                      <h4>Deadlines</h4>
                      {selected.analysis.deadlines.map((dl, i) => (
                        <p key={i} style={{ margin: '4px 0' }}>
                          • ⏰ {dl.description} (Due: <b>{dl.due_at}</b>) [{dl.confidence}]
                        </p>
                      ))}
                    </div>
                  )}

                  <div style={{ marginTop: '20px', borderTop: '1px solid #ffffff12', paddingTop: '15px' }}>
                    <button
                      className="btn-primary"
                      disabled={generatingDraft}
                      onClick={() => handleGenerateDraft(selected.id)}
                    >
                      {generatingDraft ? 'Generating Local Draft...' : 'Generate Reply Draft'}
                    </button>

                    {selectedDraft && (
                      <div className="detail-section" style={{ marginTop: '15px', background: '#6a4bf715', borderColor: '#6a4bf740' }}>
                        <h4>AI-Generated Draft (Read/Edit before sending)</h4>
                        <textarea
                          style={{
                            width: '100%',
                            height: '140px',
                            background: '#080914',
                            border: '1px solid #ffffff12',
                            color: 'white',
                            borderRadius: '8px',
                            padding: '12px',
                            fontFamily: 'inherit',
                            fontSize: '14px',
                            resize: 'vertical'
                          }}
                          value={selectedDraft}
                          onChange={e => setSelectedDraft(e.target.value)}
                        />
                        <p style={{ fontSize: '11px', color: '#ff9cac', marginTop: '6px' }}>
                          ⚠️ Explicit user confirmation is required before replying. Automatic sending is disabled.
                        </p>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div style={{ marginTop: '20px' }}>
                  <button className="btn-primary" onClick={() => runAnalysis(selected.id)}>
                    Analyze Email Locally
                  </button>
                </div>
              )}
            </article>
          </div>
        )}
      </section>
    </main>
  );
}
