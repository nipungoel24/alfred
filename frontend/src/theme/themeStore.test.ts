import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readStoredPreference, storePreference, resolveTheme, applyTheme } from './themeStore';

function mockSystemTheme(dark: boolean) {
  vi.spyOn(window, 'matchMedia').mockImplementation(query => ({
    matches: query.includes('dark') && dark,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }) as MediaQueryList);
}

describe('themeStore', () => {
  beforeEach(() => {
    localStorage.clear();
    delete document.documentElement.dataset.theme;
  });
  afterEach(() => vi.restoreAllMocks());

  it('defaults to system when nothing is stored', () => {
    expect(readStoredPreference()).toBe('system');
  });

  it('persists the preference', () => {
    storePreference('dark');
    expect(localStorage.getItem('alfred-theme')).toBe('dark');
    expect(readStoredPreference()).toBe('dark');
  });

  it('rejects unknown stored values', () => {
    localStorage.setItem('alfred-theme', 'neon');
    expect(readStoredPreference()).toBe('system');
  });

  it('resolves system → dark when OS is dark', () => {
    mockSystemTheme(true);
    expect(resolveTheme('system')).toBe('dark');
  });

  it('resolves system → light when OS is light', () => {
    mockSystemTheme(false);
    expect(resolveTheme('system')).toBe('light');
  });

  it('explicit preference wins over OS', () => {
    mockSystemTheme(true);
    expect(resolveTheme('light')).toBe('light');
    expect(resolveTheme('dark')).toBe('dark');
  });

  it('applies the resolved theme to the document', () => {
    applyTheme('dark');
    expect(document.documentElement.dataset.theme).toBe('dark');
    applyTheme('light');
    expect(document.documentElement.dataset.theme).toBe('light');
  });
});
