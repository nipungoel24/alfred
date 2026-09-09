import { describe, it, expect } from 'vitest';
import { parseSearchQuery, buildSearchQueryString, getSearchFilterChips } from './searchParser';
import { isAllowedExternalUrl } from '../lib/urlSecurity';

describe('searchParser', () => {
  describe('parseSearchQuery', () => {
    it('parses simple free text', () => {
      const result = parseSearchQuery('hello world');
      expect(result.freeText).toEqual(['hello', 'world']);
      expect(result.from).toBeUndefined();
    });

    it('parses from: filter', () => {
      const result = parseSearchQuery('from:alice@example.com');
      expect(result.from).toBe('alice@example.com');
      expect(result.freeText).toEqual([]);
    });

    it('parses subject: filter', () => {
      const result = parseSearchQuery('subject:meeting');
      expect(result.subject).toBe('meeting');
    });

    it('parses is:unread filter', () => {
      const result = parseSearchQuery('is:unread');
      expect(result.isUnread).toBe(true);
    });

    it('parses is:read filter', () => {
      const result = parseSearchQuery('is:read');
      expect(result.isRead).toBe(true);
    });

    it('parses is:reply filter', () => {
      const result = parseSearchQuery('is:reply');
      expect(result.isReply).toBe(true);
    });

    it('parses is:important filter', () => {
      const result = parseSearchQuery('is:important');
      expect(result.isImportant).toBe(true);
    });

    it('does not advertise unsupported has:attachment operator', () => {
      // has:attachment is NOT a supported operator (attachments are not
      // stored locally) — it degrades to free text, never a fake filter.
      const result = parseSearchQuery('has:attachment');
      expect(result.freeText).toContain('has:attachment');
    });

    it('parses after: date filter', () => {
      const result = parseSearchQuery('after:2024-01-01');
      expect(result.after).toBe('2024-01-01');
    });

    it('parses before: date filter', () => {
      const result = parseSearchQuery('before:2024-12-31');
      expect(result.before).toBe('2024-12-31');
    });

    it('parses category: filter', () => {
      const result = parseSearchQuery('category:primary');
      expect(result.category).toBe('primary');
    });

    it('parses in: filter', () => {
      const result = parseSearchQuery('in:inbox');
      expect(result.in).toBe('inbox');
    });

    it('keeps unknown in: scopes as free text', () => {
      const result = parseSearchQuery('in:everywhere hello');
      expect(result.in).toBeUndefined();
      expect(result.freeText).toContain('in:everywhere');
      expect(result.freeText).toContain('hello');
    });

    it('parses complex query with multiple filters', () => {
      const result = parseSearchQuery('from:alice subject:meeting is:unread hello');
      expect(result.from).toBe('alice');
      expect(result.subject).toBe('meeting');
      expect(result.isUnread).toBe(true);
      expect(result.freeText).toEqual(['hello']);
    });

    it('handles quoted values', () => {
      const result = parseSearchQuery('subject:"quarterly report"');
      expect(result.subject).toBe('quarterly report');
    });

    it('ignores invalid dates', () => {
      const result = parseSearchQuery('after:not-a-date');
      expect(result.after).toBeUndefined();
      expect(result.freeText).toContain('after:not-a-date');
    });
  });

  describe('buildSearchQueryString', () => {
    it('builds query from filters', () => {
      const query = buildSearchQueryString({
        from: 'alice@example.com',
        subject: 'meeting',
        freeText: ['hello'],
      });
      expect(query).toContain('from:alice@example.com');
      expect(query).toContain('subject:meeting');
      expect(query).toContain('hello');
    });

    it('handles boolean filters', () => {
      const query = buildSearchQueryString({
        isUnread: true,
        isRead: false,
        isReply: true,
        freeText: [],
      });
      expect(query).toContain('is:unread');
      expect(query).toContain('is:reply');
      expect(query).not.toContain('is:read');
    });

    it('quotes structured values containing spaces', () => {
      const query = buildSearchQueryString({
        subject: 'quarterly report',
        isUnread: true,
        freeText: [],
      });
      expect(query).toBe('subject:"quarterly report" is:unread');
    });

    it('round-trips quoted values with spaces and embedded quotes', () => {
      const original = 'subject:"quarterly report" is:unread';
      const parsed = parseSearchQuery(original);
      expect(parsed.subject).toBe('quarterly report');
      expect(buildSearchQueryString(parsed)).toBe(original);
    });

    it('escapes embedded quotes in structured values', () => {
      const query = buildSearchQueryString({
        subject: 'say "hi" loudly',
        freeText: [],
      });
      expect(query).toBe('subject:"say \\"hi\\" loudly"');
      const parsed = parseSearchQuery(query);
      expect(parsed.subject).toBe('say "hi" loudly');
    });
  });

  describe('getSearchFilterChips', () => {
    it('returns chips for active filters', () => {
      const chips = getSearchFilterChips({
        from: 'alice@example.com',
        subject: 'meeting',
        freeText: [],
      });
      expect(chips).toHaveLength(2);
      expect(chips[0]).toEqual({ key: 'from', label: 'From', value: 'alice@example.com' });
      expect(chips[1]).toEqual({ key: 'subject', label: 'Subject', value: 'meeting' });
    });

    it('returns empty array for free text only', () => {
      const chips = getSearchFilterChips({
        freeText: ['hello'],
      });
      expect(chips).toHaveLength(0);
    });
  });

  describe('URL protocol safety (production validator)', () => {
    it('allows https URLs', () => {
      expect(isAllowedExternalUrl('https://example.com')).toBe(true);
    });

    it('allows http URLs', () => {
      expect(isAllowedExternalUrl('http://example.com')).toBe(true);
    });

    it('allows mailto URLs', () => {
      expect(isAllowedExternalUrl('mailto:user@example.com')).toBe(true);
    });

    it('allows tel URLs', () => {
      expect(isAllowedExternalUrl('tel:+1234567890')).toBe(true);
    });

    it('rejects javascript URLs', () => {
      expect(isAllowedExternalUrl('javascript:alert(1)')).toBe(false);
    });

    it('rejects data URLs', () => {
      expect(isAllowedExternalUrl('data:text/html,<h1>hi</h1>')).toBe(false);
    });

    it('rejects file URLs', () => {
      expect(isAllowedExternalUrl('file:///etc/passwd')).toBe(false);
    });

    it('rejects ftp URLs', () => {
      expect(isAllowedExternalUrl('ftp://example.com')).toBe(false);
    });

    it('rejects custom scheme', () => {
      expect(isAllowedExternalUrl('myapp://deep/link')).toBe(false);
    });

    it('rejects relative URLs', () => {
      expect(isAllowedExternalUrl('/relative/path')).toBe(false);
    });
  });
});
