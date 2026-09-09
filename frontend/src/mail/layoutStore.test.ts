import { describe, it, expect, beforeEach } from 'vitest';
import {
  validateLayout, readSavedLayout, persistLayout, DEFAULT_LAYOUT, LAYOUT_KEY,
  PANEL_CONSTRAINTS,
} from './layoutStore';

describe('layoutStore', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('accepts a sane layout', () => {
    expect(validateLayout({ mail: 30, reader: 45, intel: 25 })).toEqual({
      mail: 30, reader: 45, intel: 25,
    });
  });

  it('accepts a collapsed intelligence pane', () => {
    expect(validateLayout({ mail: 40, reader: 60, intel: 0 })).toEqual({
      mail: 40, reader: 60, intel: 0,
    });
  });

  it('rejects non-objects and null', () => {
    expect(validateLayout(null)).toBeNull();
    expect(validateLayout('30,45,25')).toBeNull();
    expect(validateLayout([30, 45, 25])).toBeNull();
  });

  it('rejects non-numeric and non-finite panes', () => {
    expect(validateLayout({ mail: '30', reader: 45, intel: 25 })).toBeNull();
    expect(validateLayout({ mail: NaN, reader: 45, intel: 25 })).toBeNull();
    expect(validateLayout({ mail: 30, reader: Infinity, intel: 25 })).toBeNull();
    expect(validateLayout({ mail: 30, reader: 45 })).toBeNull();
  });

  it('rejects out-of-range panes', () => {
    expect(validateLayout({ mail: -5, reader: 80, intel: 25 })).toBeNull();
    expect(validateLayout({ mail: 5, reader: 45, intel: 25 })).toBeNull();
    expect(validateLayout({ mail: 30, reader: 45, intel: 90 })).toBeNull();
    expect(validateLayout({ mail: 90, reader: 5, intel: 5 })).toBeNull();
  });

  it('uses percentage strings for Panel constraints (v4: numbers are pixels)', () => {
    expect(PANEL_CONSTRAINTS.mail.minSize).toBe('20%');
    expect(PANEL_CONSTRAINTS.mail.maxSize).toBe('45%');
    expect(PANEL_CONSTRAINTS.reader.minSize).toBe('30%');
    expect(PANEL_CONSTRAINTS.intel.minSize).toBe('0%');
    expect(PANEL_CONSTRAINTS.intel.maxSize).toBe('40%');
    expect(PANEL_CONSTRAINTS.intel.collapsedSize).toBe('0%');
    for (const panel of Object.values(PANEL_CONSTRAINTS)) {
      for (const value of Object.values(panel)) {
        expect(typeof value).toBe('string');
        expect(value.endsWith('%')).toBe(true);
      }
    }
  });

  it('ignores stale v1 layout values stored under the old key', () => {
    localStorage.setItem('alfred-pane-layout', JSON.stringify({ mail: 20, reader: 30, intel: 0 }));
    expect(readSavedLayout()).toBeNull();
  });

  it('rejects insane totals', () => {
    expect(validateLayout({ mail: 15, reader: 20, intel: 0 })).toBeNull();
    expect(validateLayout({ mail: 60, reader: 70, intel: 50 })).toBeNull();
  });

  it('ignores corrupted JSON', () => {
    localStorage.setItem(LAYOUT_KEY, '{not json');
    expect(readSavedLayout()).toBeNull();
  });

  it('ignores out-of-range persisted values', () => {
    localStorage.setItem(LAYOUT_KEY, JSON.stringify({ mail: 200, reader: -50, intel: 25 }));
    expect(readSavedLayout()).toBeNull();
  });

  it('round-trips a valid layout', () => {
    persistLayout({ mail: 35, reader: 45, intel: 20 });
    expect(readSavedLayout()).toEqual({ mail: 35, reader: 45, intel: 20 });
  });

  it('refuses to persist a broken layout', () => {
    persistLayout({ mail: 35, reader: 45, intel: 20 });
    persistLayout({ mail: 500, reader: 45, intel: 20 });
    expect(readSavedLayout()).toEqual({ mail: 35, reader: 45, intel: 20 });
  });

  it('defaults sum to 100', () => {
    const total = DEFAULT_LAYOUT.mail + DEFAULT_LAYOUT.reader + DEFAULT_LAYOUT.intel;
    expect(total).toBe(100);
  });
});
