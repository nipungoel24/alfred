let BASE: string = import.meta.env.VITE_ALFRED_API_URL ?? 'http://127.0.0.1:8765';
let TOKEN: string | null = null;

export type BackendRuntimeInfo = { port: number; token: string };

function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

/** Set backend credentials directly (used by retry handler). */
export function setApiCredentials(port: number, token: string) {
  BASE = `http://127.0.0.1:${port}`;
  TOKEN = token;
}

/**
 * Initialize the API client.
 *
 * Packaged Tauri: calls `await_backend_ready` once — a durable Rust-owned
 * command that blocks until the BackendSupervisor confirms the sidecar is
 * healthy (FastAPI listening, runtime auth active, SQLite usable) or fails
 * with a structured error. No retry loops, no event dependencies, no
 * fallback to dev port.
 *
 * Browser dev: uses VITE_ALFRED_API_URL directly.
 */
export async function initApi(): Promise<void> {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    const info = await invoke<BackendRuntimeInfo>('await_backend_ready');
    BASE = `http://127.0.0.1:${info.port}`;
    TOKEN = info.token;
    return;
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
