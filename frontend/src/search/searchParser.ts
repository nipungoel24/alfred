/**
 * Structured search parser for Alfred mail search.
 * 
 * Parses search queries into structured filters that can be sent to the backend.
 * Backend validates and constructs safe FTS/SQL — never concatenates raw user text.
 * 
 * Syntax (only operators the backend truly supports):
 * - Free text: "hello world" (FTS5 + BM25 over subject, sender, body)
 * - from:alice@example.com (filter by sender)
 * - subject:meeting (filter by subject)
 * - is:unread / is:read (label-based read state)
 * - is:important (Gmail IMPORTANT label)
 * - is:reply (analysis says a reply is needed)
 * - after:2024-01-01 / before:2024-12-31 (received date)
 * - category:primary (Gmail category tab)
 * - in:inbox / in:all / in:archived / in:sent (mailbox state)
 */

export interface SearchFilters {
  freeText: string[];
  from?: string;
  subject?: string;
  isUnread?: boolean;
  isRead?: boolean;
  isImportant?: boolean;
  isReply?: boolean;
  after?: string;
  before?: string;
  category?: string;
  in?: string;
}

const FILTER_REGEX = /(\w+):(?:"((?:[^"\\]|\\.)+)"|(\S+))/g;

// User-facing `in:` scopes. Unknown values stay free text (never sent to
// the backend, which validates strictly and 422s on anything else).
const KNOWN_IN_SCOPES = new Set(['inbox', 'all', 'archived', 'sent']);

function unescapeValue(value: string): string {
  return value.replace(/\\(.)/g, '$1');
}

export function parseSearchQuery(query: string): SearchFilters {
  const filters: SearchFilters = {
    freeText: [],
  };

  let remaining = query;
  let match: RegExpExecArray | null;

  // Reset regex state
  FILTER_REGEX.lastIndex = 0;

  // Extract structured filters
  while ((match = FILTER_REGEX.exec(query)) !== null) {
    const [fullMatch, key, quotedValue, unquotedValue] = match;
    const value = unescapeValue(quotedValue || unquotedValue);

    switch (key.toLowerCase()) {
      case 'from':
        filters.from = value;
        remaining = remaining.replace(fullMatch, '');
        break;
      case 'subject':
        filters.subject = value;
        remaining = remaining.replace(fullMatch, '');
        break;
      case 'is':
        if (value.toLowerCase() === 'unread') {
          filters.isUnread = true;
          remaining = remaining.replace(fullMatch, '');
        } else if (value.toLowerCase() === 'read') {
          filters.isRead = true;
          remaining = remaining.replace(fullMatch, '');
        } else if (value.toLowerCase() === 'important') {
          filters.isImportant = true;
          remaining = remaining.replace(fullMatch, '');
        } else if (value.toLowerCase() === 'reply') {
          filters.isReply = true;
          remaining = remaining.replace(fullMatch, '');
        }
        break;
      case 'after':
        if (isValidDate(value)) {
          filters.after = value;
          remaining = remaining.replace(fullMatch, '');
        }
        // If invalid date, don't remove from remaining (treat as free text)
        break;
      case 'before':
        if (isValidDate(value)) {
          filters.before = value;
          remaining = remaining.replace(fullMatch, '');
        }
        // If invalid date, don't remove from remaining (treat as free text)
        break;
      case 'category':
        filters.category = value;
        remaining = remaining.replace(fullMatch, '');
        break;
      case 'in':
        if (KNOWN_IN_SCOPES.has(value.toLowerCase())) {
          filters.in = value.toLowerCase();
          remaining = remaining.replace(fullMatch, '');
        }
        // Unknown scope stays free text (backend would 422).
        break;
    }
  }

  // Extract free text (remaining words)
  const words = remaining.trim().split(/\s+/).filter(Boolean);
  filters.freeText = words;

  return filters;
}

function isValidDate(dateStr: string): boolean {
  const date = new Date(dateStr);
  return !Number.isNaN(date.getTime());
}

function escapeValue(value: string): string {
  // Quote structured values containing whitespace or quotes so a rebuild
  // round-trips: subject:"quarterly report", not subject:quarterly report.
  // Embedded quotes are backslash-escaped (parse unescapes them).
  if (/[\s"]/.test(value)) {
    return `"${value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
  }
  return value;
}

export function buildSearchQueryString(filters: SearchFilters): string {
  const parts: string[] = [];

  if (filters.from) parts.push(`from:${escapeValue(filters.from)}`);
  if (filters.subject) parts.push(`subject:${escapeValue(filters.subject)}`);
  if (filters.isUnread) parts.push('is:unread');
  if (filters.isRead) parts.push('is:read');
  if (filters.isImportant) parts.push('is:important');
  if (filters.isReply) parts.push('is:reply');
  if (filters.after) parts.push(`after:${filters.after}`);
  if (filters.before) parts.push(`before:${filters.before}`);
  if (filters.category) parts.push(`category:${escapeValue(filters.category)}`);
  if (filters.in) parts.push(`in:${filters.in}`);

  if (filters.freeText.length > 0) {
    parts.push(filters.freeText.join(' '));
  }

  return parts.join(' ');
}

export function getSearchFilterChips(filters: SearchFilters): Array<{ key: string; label: string; value: string }> {
  const chips: Array<{ key: string; label: string; value: string }> = [];

  if (filters.from) chips.push({ key: 'from', label: 'From', value: filters.from });
  if (filters.subject) chips.push({ key: 'subject', label: 'Subject', value: filters.subject });
  if (filters.isUnread) chips.push({ key: 'isUnread', label: 'Is', value: 'Unread' });
  if (filters.isRead) chips.push({ key: 'isRead', label: 'Is', value: 'Read' });
  if (filters.isImportant) chips.push({ key: 'isImportant', label: 'Is', value: 'Important' });
  if (filters.isReply) chips.push({ key: 'isReply', label: 'Is', value: 'Needs reply' });
  if (filters.after) chips.push({ key: 'after', label: 'After', value: filters.after });
  if (filters.before) chips.push({ key: 'before', label: 'Before', value: filters.before });
  if (filters.category) chips.push({ key: 'category', label: 'Category', value: filters.category });
  if (filters.in) chips.push({ key: 'in', label: 'In', value: filters.in });

  return chips;
}
