import { isAllowedExternalUrl } from './urlSecurity';
import { isTauriRuntime } from '../api/client';

/**
 * Open a URL outside the app.
 *
 * In the packaged build this is the OS opener (never a shell string), so a
 * rejected opener permission stays rejected and there is no fallback that
 * would quietly turn a refusal into an execution path. In a browser the
 * popup is opened as a bare new tab: no features string, because the point
 * of the system browser is that the consent screen is not a window this app
 * drew and cannot style, position, or script.
 */
export async function openExternalUrl(url: string): Promise<void> {
  if (!isAllowedExternalUrl(url)) {
    throw new Error('This link was not opened because its address is not allowed.');
  }
  if (isTauriRuntime()) {
    const { openUrl } = await import('@tauri-apps/plugin-opener');
    await openUrl(url);
    return;
  }
  window.open(url, '_blank', 'noopener,noreferrer');
}
