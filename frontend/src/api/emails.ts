import { api } from './client';

export type Priority = 'urgent' | 'high' | 'medium' | 'low';
export type MailCategory = 'primary' | 'promotions' | 'social' | 'updates' | 'forums';
export type MailScope = 'inbox' | 'all';
export type MailKind = 'received' | 'sent' | 'archived';

export const CATEGORY_ORDER: MailCategory[] = ['primary', 'promotions', 'social', 'updates', 'forums'];

export type BackfillStatus = {
  state: 'not_started' | 'running' | 'paused' | 'complete' | 'failed';
  complete: boolean;
  estimate: number | null;
  imported: number;
  pages: number;
  remaining_estimate: number | null;
  last_page_at: string | null;
  last_error: string | null;
};

export type EmailCounts = {
  active_inbox: number;
  all_mail: number;
  excluded: number;
  categories: Record<MailCategory, number>;
};

export type Analysis = {
  short_summary: string;
  category: string;
  priority: Priority;
  priority_score: number;
  reason_for_priority: string;
  needs_reply: boolean;
  action_items: { description: string; owner?: string | null; deadline?: string | null }[];
  deadlines: { description: string; due_at?: string | null; confidence?: string }[];
  important_details: string[]
};

export type Email = {
  id: string;
  thread_id?: string | null;
  account_id?: string | null;
  sender: string;
  sender_name?: string | null;
  recipients: string[];
  subject: string;
  body: string;
  received_at?: string | null;
  label_ids: string[];
  analysis?: Analysis | null
};

export type BriefingItem = {
  email_id: string;
  sender: string;
  subject: string;
  short_summary: string;
  priority: Priority;
  why_it_matters: string;
  deadline?: string | null;
  needs_reply: boolean
};

export type Briefing = {
  executive_summary: string;
  total_emails: number;
  urgent_count: number;
  high_priority_count: number;
  needs_reply_count: number;
  deadline_count: number;
  top_attention_items: BriefingItem[];
  deadlines: BriefingItem[];
  important_updates: string[];
  can_wait_or_review_later: string[]
};

export type EmailAccount = {
  id: string;
  provider: string;
  email_address: string;
  display_name?: string | null;
  connection_status: string; // 'connected', 'disconnected', 'error'
  last_sync_at?: string | null;
  sync_cursor?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  backfill_complete?: boolean;
  backfill?: BackfillStatus
};

export type Task = {
  id: string;
  source_email_id?: string | null;
  source_thread_id?: string | null;
  title: string;
  description?: string | null;
  due_at?: string | null;
  priority?: string | null;
  status: string; // 'pending', 'completed'
  created_at?: string | null
};

export const emails = (options: {
  query?: string;
  priority?: string;
  needsReply?: boolean | null;
  accountId?: string;
  category?: MailCategory | null;
  scope?: MailScope;
  kind?: MailKind | null;
  limit?: number;
  offset?: number;
} = {}) => {
  const params: string[] = [];
  if (options.query) params.push(`q=${encodeURIComponent(options.query)}`);
  if (options.priority) params.push(`priority=${encodeURIComponent(options.priority)}`);
  if (options.needsReply !== null && options.needsReply !== undefined) params.push(`needs_reply=${options.needsReply}`);
  if (options.accountId) params.push(`account_id=${encodeURIComponent(options.accountId)}`);
  if (options.category) params.push(`category=${encodeURIComponent(options.category)}`);
  if (options.scope && options.scope !== 'inbox') params.push(`scope=${encodeURIComponent(options.scope)}`);
  if (options.kind) params.push(`kind=${encodeURIComponent(options.kind)}`);
  if (options.limit !== undefined) params.push(`limit=${options.limit}`);
  if (options.offset !== undefined) params.push(`offset=${options.offset}`);
  const queryStr = params.length ? `?${params.join('&')}` : '';
  return api<Email[]>(`/api/emails${queryStr}`);
};

export const emailCounts = (accountId?: string) => {
  const params = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return api<EmailCounts>(`/api/emails/counts${params}`);
};

export const emailDetails = (id: string) => api<Email>(`/api/emails/${id}`);
export const analyze = (id: string) => api<{ analysis: Analysis; cached: boolean }>(`/api/emails/${id}/analyze`, { method: 'POST' });
export const draft = (id: string) => api<{ draft: string }>(`/api/emails/${id}/draft`, { method: 'POST' });
export const briefing = () => api<Briefing>('/api/briefing');
export const regenerateBriefing = () => api<Briefing>('/api/briefing/generate', { method: 'POST' });
export type Health = { status: 'ok' | 'error'; ai?: string; build?: string | null };
export const health = () => api<Health>('/health');

// AI state machine (backend.app.ai.supervisor states)
export type AIState =
  | 'initializing'
  | 'ready'
  | 'ollama_not_running'
  | 'model_missing'
  | 'temporarily_unavailable'
  | 'recovering'
  | 'error';

export type AnalysisStatus = {
  state: AIState;
  model: string;
  model_installed: boolean | null;
  ollama_installed: boolean;
  ollama_running: boolean;
  last_error: string | null;
  detail: string | null;
  pending: number;
  worker_running: boolean;
  queue_paused: boolean;
};

export const analysisStatus = () => api<AnalysisStatus>('/api/analysis/status');
export const analysisRetry = () => api<AnalysisStatus>('/api/analysis/retry', { method: 'POST' });

// Account management
export const accounts = () => api<EmailAccount[]>('/api/accounts');
export const connectGmail = (redirectUri: string) => api<{ url: string }>(`/api/accounts/gmail/connect?redirect_uri=${encodeURIComponent(redirectUri)}`, { method: 'POST' });
export const syncAccount = (id: string, loadOlder = false) => api<{ imported: number; skipped_duplicates: number; has_more?: boolean }>(`/api/accounts/${id}/sync?load_older=${loadOlder}`, { method: 'POST' });
export const backfillAccount = (id: string) => api<{ status: BackfillStatus; action: string }>(`/api/accounts/${id}/backfill`, { method: 'POST' });
export const pauseBackfill = (id: string) => api<{ status: BackfillStatus; action: string }>(`/api/accounts/${id}/backfill/pause`, { method: 'POST' });
export const deleteAccount = (id: string) => api<{ status: string }>(`/api/accounts/${id}`, { method: 'DELETE' });

// Task management
export const tasks = () => api<Task[]>('/api/tasks');
export const toggleTask = (id: string) => api<Task>(`/api/tasks/${id}/toggle`, { method: 'POST' });
export const deleteTask = (id: string) => api<{ status: string }>(`/api/tasks/${id}`, { method: 'DELETE' });

// Structured search — mirrors backend.app.schemas.SearchFilters.
export type SearchFilters = {
  free_text: string[];
  sender?: string;
  subject?: string;
  is_unread?: boolean;
  is_read?: boolean;
  is_important?: boolean;
  needs_reply?: boolean;
  after?: string;
  before?: string;
  category?: string;
  mailbox_state?: string;
};

export const searchEmailsStructured = (filters: SearchFilters, options: {
  accountId?: string;
  limit?: number;
  offset?: number;
} = {}) => {
  const params: string[] = [];
  if (options.accountId) params.push(`account_id=${encodeURIComponent(options.accountId)}`);
  if (options.limit !== undefined) params.push(`limit=${options.limit}`);
  if (options.offset !== undefined) params.push(`offset=${options.offset}`);
  const queryStr = params.length ? `?${params.join('&')}` : '';
  return api<Email[]>(`/api/emails/search${queryStr}`, {
    method: 'POST',
    body: JSON.stringify(filters),
  });
};
