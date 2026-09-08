import { useMemo } from 'react';
import type { ReactNode } from 'react';
import LinkifyIt from 'linkify-it';
import type { Match } from 'linkify-it';
import { isAllowedExternalUrl } from '../lib/urlSecurity';

const linkify = new LinkifyIt();

function isSafeUrl(url: string): boolean {
  return isAllowedExternalUrl(url);
}

interface LinkifiedBodyProps {
  text: string;
  className?: string;
}

export function LinkifiedBody({ text, className }: LinkifiedBodyProps) {
  const elements = useMemo(() => {
    if (!text) return null;

    const matches: Match[] = linkify.match(text) ?? [];
    if (matches.length === 0) return text;

    const parts: (string | ReactNode)[] = [];
    let lastIndex = 0;

    for (const match of matches) {
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }

      const url = match.url;
      if (!isSafeUrl(url)) {
        // Reject unsafe schemes — render as plain text, not a link
        parts.push(match.text);
        lastIndex = match.index + match.lastIndex;
        continue;
      }
      parts.push(
        <a
          key={`link-${match.index}`}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="reader-link"
          onClick={(e) => {
            e.preventDefault();
            openExternalLink(url);
          }}
        >
          {match.text}
        </a>
      );

      lastIndex = match.index + match.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts;
  }, [text]);

  return <div className={className}>{elements}</div>;
}

async function openExternalLink(url: string): Promise<void> {
  try {
    const { openUrl } = await import('@tauri-apps/plugin-opener');
    await openUrl(url);
  } catch {
    // Fallback for browser environment
    window.open(url, '_blank', 'noopener,noreferrer');
  }
}
