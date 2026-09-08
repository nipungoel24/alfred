/**
 * Production URL validation for link security.
 * Allows exactly: https, http, mailto, tel.
 * Rejects: ftp, file, javascript, data, custom schemes.
 */

const ALLOWED_SCHEMES = new Set(['https:', 'http:', 'mailto:', 'tel:']);

/**
 * Check if a URL is safe to open (allowed scheme only).
 * Must be imported by LinkifiedBody and tested by production tests.
 */
export function isAllowedExternalUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ALLOWED_SCHEMES.has(parsed.protocol);
  } catch {
    // Relative URLs or malformed input — reject
    return false;
  }
}
