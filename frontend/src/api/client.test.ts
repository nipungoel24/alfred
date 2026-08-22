import { beforeEach, describe, expect, it, vi } from 'vitest';

const invoke = vi.fn();

vi.mock('@tauri-apps/api/core', () => ({
  invoke,
}));

describe('api client bootstrap', () => {
  beforeEach(() => {
    vi.resetModules();
    invoke.mockReset();
    delete (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__;
  });

  it('does not fall back to the development port in packaged Tauri mode', async () => {
    (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ = {};
    invoke.mockRejectedValue(new Error('backend not started'));

    const { apiBase, initApi } = await import('./client');
    await initApi(1, 0);

    expect(apiBase()).toBe('http://127.0.0.1:0');
  });

  it('uses the native backend endpoint when Tauri provides one', async () => {
    (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ = {};
    invoke.mockResolvedValue({ port: 49152, token: 'runtime-token' });

    const { apiBase, initApi } = await import('./client');
    await initApi(1, 0);

    expect(apiBase()).toBe('http://127.0.0.1:49152');
  });
});
