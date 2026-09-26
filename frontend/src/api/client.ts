let BASE: string = import.meta.env.VITE_ALFRED_API_URL ?? 'http://127.0.0.1:8765';
let TOKEN: string | null = null;

export type BackendRuntimeInfo = { port: number; token: string };

/**
 * The startup state machine, mirrored from the Rust shell.
 *
 * `BOOT` .. `RESTORING_SESSION` are progress states. `READY` and `RECOVERY`
 * both mean the workspace may be shown; `RECOVERY` means something optional
 * (the local AI runtime or the model) is unavailable. `FATAL_ERROR` blocks
 * the workspace and requires user action.
 */
export const STARTUP_PHASES = [
  'BOOT',
  'INITIALIZING',
  'STARTING_BACKEND',
  'WAITING_FOR_BACKEND',
  'CHECKING_DATABASE',
  'CHECKING_AI_RUNTIME',
  'CHECKING_MODEL',
  'RESTORING_SESSION',
  'READY',
  'RECOVERY',
  'FATAL_ERROR',
] as const;

export type StartupPhase = (typeof STARTUP_PHASES)[number];

export type StartupStatus = {
  phase: StartupPhase;
  /** Stable machine-readable code, e.g. BACKEND_HEALTH_TIMEOUT. */
  code: string;
  /** User-facing sentence. Empty while healthy. */
  detail: string;
  guidance: string;
  ready: boolean;
  degraded: boolean;
  phase_elapsed_ms: number;
  build: string;
  version: string;
};

/** A startup failure, carrying the shell's diagnostic code and guidance. */
export class StartupError extends Error {
  readonly code: string;
  readonly guidance: string;
  readonly fatal: boolean;

  constructor(code: string, guidance: string, fatal: boolean) {
    super(guidance || code);
    this.name = 'StartupError';
    this.code = code;
    this.guidance = guidance;
    this.fatal = fatal;
  }
}

export const STARTUP_PHASE_EVENT = 'alfred://startup-phase';

function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

/** True when running inside the packaged Tauri WebView. */
export function isTauriRuntime(): boolean {
  return isTauri();
}

/** Set backend credentials directly (used by retry handler). */
export function setApiCredentials(port: number, token: string) {
  BASE = `http://127.0.0.1:${port}`;
  TOKEN = token;
}

/**
 * Parse a rejected Tauri command into a `StartupError`.
 *
 * The shell returns a JSON envelope so the UI can render a stable code and
 * real guidance. Older or unexpected shapes degrade to a generic error rather
 * than showing a raw exception string to the user.
 */
export function parseStartupFailure(raw: unknown): StartupError {
  const message = raw instanceof Error ? raw.message : String(raw);
  try {
    const parsed = JSON.parse(message) as {
      code?: string;
      guidance?: string;
      fatal?: boolean;
    };
    if (parsed && typeof parsed.code === 'string') {
      return new StartupError(
        parsed.code,
        typeof parsed.guidance === 'string' ? parsed.guidance : '',
        parsed.fatal !== false,
      );
    }
  } catch {
    // Not JSON. Fall through.
  }
  return new StartupError('UNEXPECTED_STARTUP_FAILURE', message, true);
}

/** Read the authoritative startup snapshot from the shell. */
export async function fetchStartupStatus(): Promise<StartupStatus | null> {
  if (!isTauri()) return null;
  const { invoke } = await import('@tauri-apps/api/core');
  return invoke<StartupStatus>('startup_phase');
}

/** Log file location and build identity, for the failure screen. */
export async function fetchStartupDiagnostics(): Promise<{
  log_path: string;
  build: string;
  version: string;
} | null> {
  if (!isTauri()) return null;
  const { invoke } = await import('@tauri-apps/api/core');
  return invoke('startup_diagnostics');
}

/**
 * Initialize the API client.
 *
 * Packaged Tauri: calls `await_backend_ready` once — a durable Rust-owned
 * command that blocks until the BackendSupervisor confirms the sidecar is
 * genuinely serving, or fails with a structured diagnostic envelope. No
 * frontend polling, no retry loops, no fallback to a dev port.
 *
 * Browser dev: uses VITE_ALFRED_API_URL directly.
 */
export async function initApi(): Promise<void> {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    let info: BackendRuntimeInfo;
    try {
      info = await invoke<BackendRuntimeInfo>('await_backend_ready');
    } catch (err) {
      throw parseStartupFailure(err);
    }
    BASE = `http://127.0.0.1:${info.port}`;
    TOKEN = info.token;
    return;
  }
  BASE = import.meta.env.VITE_ALFRED_API_URL ?? 'http://127.0.0.1:8765';
  TOKEN = null;
}

/**
 * Restart the backend and wait for it to become ready again.
 *
 * Owned by the API layer so the UI never has to know that a restart is two
 * Tauri commands. The shell's generation guard makes the restart safe even if
 * a previous readiness poller is still in flight.
 */
export async function retryStartup(): Promise<void> {
  const { invoke } = await import('@tauri-apps/api/core');
  try {
    await invoke('restart_backend');
    const info = await invoke<BackendRuntimeInfo>('await_backend_ready');
    setApiCredentials(info.port, info.token);
  } catch (err) {
    throw parseStartupFailure(err);
  }
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
