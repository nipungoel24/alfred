let BASE: string = import.meta.env.VITE_ALFRED_API_URL ?? 'http://127.0.0.1:8765';
let TOKEN: string | null = null;

export type BackendRuntimeInfo = { port: number; token: string };

function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

/**
 * Resolve the backend endpoint at startup.
 * - Under Tauri: asks the shell for the dynamic loopback port + the
 *   per-launch runtime token (backend_info command).
 * - In dev: uses VITE_ALFRED_API_URL; no token (the backend only enforces
 *   a token when ALFRED_RUNTIME_TOKEN is set).
 */
export async function initApi(): Promise<void> {
  if (isTauri()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      const info = await invoke<BackendRuntimeInfo>('backend_info');
      BASE = `http://127.0.0.1:${info.port}`;
      TOKEN = info.token;
      return;
    } catch {
      /* fall through to defaults; StartupGate will surface the failure */
    }
  }
  BASE = import.meta.env.VITE_ALFRED_API_URL ?? 'http://127.0.0.1:8765';
  TOKEN = null;
}

export function apiBase(): string {
  return BASE;
}

export function sseUrl(path: string): string {
  const sep = path.includes('?') ? '&' : '?';
  return TOKEN ? `${BASE}${path}${sep}token=${encodeURIComponent(TOKEN)}` : `${BASE}${path}`;
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (TOKEN) headers.set('X-Alfred-Token', TOKEN);
  const r = await fetch(BASE + path, { ...init, headers });
  if (!r.ok) {
    const body = await r.json().catch(() => null);
    throw new Error(body?.error?.message || body?.detail || 'Request failed');
  }
  return r.json();
}
