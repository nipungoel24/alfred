import { beforeEach, describe, expect, it, vi } from 'vitest';
import { openExternalUrl } from './openExternal';

const openUrlMock = vi.fn();
vi.mock('@tauri-apps/plugin-opener', () => ({
  openUrl: (...args: unknown[]) => openUrlMock(...args),
}));

describe('openExternalUrl', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete (window as unknown as Record<string, unknown>).__TAURI_INTERNALS__;
    vi.spyOn(window, 'open').mockImplementation(() => null);
  });

  it('rejects disallowed schemes', async () => {
    await expect(openExternalUrl('javascript:alert(1)')).rejects.toThrow(
      'This link was not opened because its address is not allowed.'
    );
    await expect(openExternalUrl('file:///etc/passwd')).rejects.toThrow(
      'This link was not opened because its address is not allowed.'
    );
    await expect(openExternalUrl('data:text/html,test')).rejects.toThrow(
      'This link was not opened because its address is not allowed.'
    );
    await expect(openExternalUrl('/relative/url')).rejects.toThrow(
      'This link was not opened because its address is not allowed.'
    );
  });

  it('opens in new browser window with noopener,noreferrer in web mode', async () => {
    const windowOpenSpy = vi.spyOn(window, 'open');
    await openExternalUrl('https://accounts.google.com/o/oauth2/v2/auth?scope=email');
    expect(windowOpenSpy).toHaveBeenCalledWith(
      'https://accounts.google.com/o/oauth2/v2/auth?scope=email',
      '_blank',
      'noopener,noreferrer'
    );
    expect(openUrlMock).not.toHaveBeenCalled();
  });

  it('invokes Tauri opener plugin in Tauri runtime', async () => {
    (window as unknown as Record<string, unknown>).__TAURI_INTERNALS__ = {};
    const windowOpenSpy = vi.spyOn(window, 'open');

    await openExternalUrl('https://accounts.google.com/o/oauth2/v2/auth?scope=email');
    expect(openUrlMock).toHaveBeenCalledWith(
      'https://accounts.google.com/o/oauth2/v2/auth?scope=email'
    );
    expect(windowOpenSpy).not.toHaveBeenCalled();
  });
});
