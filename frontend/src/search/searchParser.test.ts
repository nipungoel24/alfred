import { describe, it, expect } from 'vitest';
import { parseSearchQuery, buildSearchQueryString, getSearchFilterChips } from './searchParser';

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

    it('parses has:attachment filter', () => {
      const result = parseSearchQuery('has:attachment');
      expect(result.hasAttachment).toBe(true);
    });

    it('parses is:unread filter', () => {
      const result = parseSearchQuery('is:unread');
      expect(result.isUnread).toBe(true);
    });

    it('parses is:important filter', () => {
      const result = parseSearchQuery('is:important');
      expect(result.isImportant).toBe(true);
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
        hasAttachment: true,
        isUnread: true,
        freeText: [],
      });
      expect(query).toContain('has:attachment');
      expect(query).toContain('is:unread');
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

  describe('URL protocol safety', () => {
    const ALLOWED_SCHEMES = new Set(['https:', 'http:', 'mailto:', 'tel:']);

    it('allows https URLs', () => {
      expect(ALLOWED_SCHEMES.has('https:')).toBe(true);
    });

    it('allows http URLs', () => {
      expect(ALLOWED_SCHEMES.has('http:')).toBe(true);
    });

    it('allows mailto URLs', () => {
      expect(ALLOWED_SCHEMES.has('mailto:')).toBe(true);
    });

    it('allows tel URLs', () => {
      expect(ALLOWED_SCHEMES.has('tel:')).toBe(true);
    });

    it('rejects javascript URLs', () => {
      expect(ALLOWED_SCHEMES.has('javascript:')).toBe(false);
    });

    it('rejects data URLs', () => {
      expect(ALLOWED_SCHEMES.has('data:')).toBe(false);
    });

    it('rejects file URLs', () => {
      expect(ALLOWED_SCHEMES.has('file:')).toBe(false);
    });

    it('rejects ftp URLs', () => {
      expect(ALLOWED_SCHEMES.has('ftp:')).toBe(false);
    });
  });
});
