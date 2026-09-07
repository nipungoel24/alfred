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

  it('calls await_backend_ready in packaged Tauri mode', async () => {
    (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ = {};
    invoke.mockResolvedValue({ port: 49152, token: 'runtime-token' });

    const { apiBase, initApi } = await import('./client');
    await initApi();

    expect(apiBase()).toBe('http://127.0.0.1:49152');
    expect(invoke).toHaveBeenCalledWith('await_backend_ready');
  });

  it('throws when await_backend_ready fails', async () => {
    (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ = {};
    invoke.mockRejectedValue(new Error('sidecar exited'));

    const { initApi } = await import('./client');
    await expect(initApi()).rejects.toThrow('sidecar exited');
  });

  it('uses dev URL in browser mode', async () => {
    const { apiBase, initApi } = await import('./client');
    await initApi();

    expect(apiBase()).toContain('127.0.0.1');
    expect(invoke).not.toHaveBeenCalled();
  });
});
