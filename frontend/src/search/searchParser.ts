/**
 * Structured search parser for Alfred mail search.
 * 
 * Parses search queries into structured filters that can be sent to the backend.
 * Backend validates and constructs safe FTS/SQL — never concatenates raw user text.
 * 
 * Syntax:
 * - Free text: "hello world" (searches subject, sender, body)
 * - from:alice@example.com (filter by sender)
 * - subject:meeting (filter by subject)
 * - has:attachment (filter by attachments)
 * - is:unread (filter by unread)
 * - is:important (filter by important)
 * - after:2024-01-01 (filter by date)
 * - before:2024-12-31 (filter by date)
 * - category:primary (filter by category)
 * - in:inbox (filter by mailbox state)
 */

export interface SearchFilters {
  freeText: string[];
  from?: string;
  subject?: string;
  hasAttachment?: boolean;
  isUnread?: boolean;
  isImportant?: boolean;
  after?: string;
  before?: string;
  category?: string;
  in?: string;
}

const FILTER_REGEX = /(\w+):(?:"([^"]+)"|(\S+))/g;

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
    const value = quotedValue || unquotedValue;

    switch (key.toLowerCase()) {
      case 'from':
        filters.from = value;
        remaining = remaining.replace(fullMatch, '');
        break;
      case 'subject':
        filters.subject = value;
        remaining = remaining.replace(fullMatch, '');
        break;
      case 'has':
        if (value.toLowerCase() === 'attachment') {
          filters.hasAttachment = true;
          remaining = remaining.replace(fullMatch, '');
        }
        break;
      case 'is':
        if (value.toLowerCase() === 'unread') {
          filters.isUnread = true;
          remaining = remaining.replace(fullMatch, '');
        } else if (value.toLowerCase() === 'important') {
          filters.isImportant = true;
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
        filters.in = value;
        remaining = remaining.replace(fullMatch, '');
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

export function buildSearchQueryString(filters: SearchFilters): string {
  const parts: string[] = [];

  if (filters.from) parts.push(`from:${filters.from}`);
  if (filters.subject) parts.push(`subject:${filters.subject}`);
  if (filters.hasAttachment) parts.push('has:attachment');
  if (filters.isUnread) parts.push('is:unread');
  if (filters.isImportant) parts.push('is:important');
  if (filters.after) parts.push(`after:${filters.after}`);
  if (filters.before) parts.push(`before:${filters.before}`);
  if (filters.category) parts.push(`category:${filters.category}`);
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
  if (filters.hasAttachment) chips.push({ key: 'has', label: 'Has', value: 'Attachment' });
  if (filters.isUnread) chips.push({ key: 'is', label: 'Is', value: 'Unread' });
  if (filters.isImportant) chips.push({ key: 'is', label: 'Is', value: 'Important' });
  if (filters.after) chips.push({ key: 'after', label: 'After', value: filters.after });
  if (filters.before) chips.push({ key: 'before', label: 'Before', value: filters.before });
  if (filters.category) chips.push({ key: 'category', label: 'Category', value: filters.category });
  if (filters.in) chips.push({ key: 'in', label: 'In', value: filters.in });

  return chips;
}
