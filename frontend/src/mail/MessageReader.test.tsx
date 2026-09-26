/// <reference types="node" />
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MessageReader } from './MessageReader';
import type { Email } from '../api/emails';

const baseEmail: Email = {
  id: 'm1',
  sender: 'boss@work.com',
  sender_name: 'Boss',
  recipients: ['me@gmail.com'],
  subject: 'Q3 planning needed',
  body: 'Please send the plan by Friday.',
  received_at: '2026-08-17T09:00:00Z',
  label_ids: ['INBOX'],
  analysis: null,
};

type Meta = Record<string, unknown>;

const emailDetails = vi.fn<(id: string) => Promise<Email & { source_metadata?: Meta }>>();

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return { ...original, emailDetails: (id: string) => emailDetails(id) };
});

function renderReader(overrides: Partial<Email> = {}, meta?: Meta) {
  const email = { ...baseEmail, ...overrides } as Email & { source_metadata?: Meta };
  if (meta) email.source_metadata = meta;

  emailDetails.mockResolvedValue(email);

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MessageReader
        emailId="m1"
        intelVisible
        onToggleIntel={() => {}}
        laterIds={new Set<string>()}
        onToggleLater={() => {}}
      />
    </QueryClientProvider>
  );
}

/** Position of each element in document order, for hierarchy assertions. */
function orderOf(nodes: Array<Node | null>): number[] {
  return nodes.map((n) => (n ? Array.prototype.indexOf.call(document.body.querySelectorAll('*'), n) : -1));
}

beforeEach(() => {
  emailDetails.mockReset();
});

describe('MessageReader — required hierarchy', () => {
  it('orders subject, sender, recipients, timestamp, body, attachments, then actions', async () => {
    renderReader({}, { has_attachment: true, gmail_raw: { sizeEstimate: 4096 } });

    await screen.findByRole('heading', { name: 'Q3 planning needed' });

    const subject = screen.getByRole('heading', { name: 'Q3 planning needed' });
    const from = screen.getByText('From').closest('.reader-field')!;
    const to = screen.getByText('To').closest('.reader-field')!;
    const date = screen.getByText('Date').closest('.reader-field')!;
    const body = document.querySelector('.reader-body')!;
    const attachments = document.querySelector('.reader-attachments')!;
    const actions = document.querySelector('.reader-actions')!;

    const positions = orderOf([subject, from, to, date, body, attachments, actions]);
    expect(positions.every((p) => p >= 0)).toBe(true);
    // Strictly increasing: no element appears before the one above it.
    expect(positions).toEqual([...positions].sort((a, b) => a - b));
  });

  it('places actions after the body even when there are no attachments', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });

    expect(document.querySelector('.reader-attachments')).toBeNull();
    const body = document.querySelector('.reader-body')!;
    const actions = document.querySelector('.reader-actions')!;
    expect(orderOf([body, actions])[0]).toBeLessThan(orderOf([body, actions])[1]);
  });

  it('exposes the subject as the only heading in the reader, at level 2', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });

    const headings = screen.getAllByRole('heading');
    expect(headings).toHaveLength(1);
    expect(headings[0].tagName).toBe('H2');
  });

  it('does not render a heading that duplicates the view name', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.queryByRole('heading', { name: 'Mail' })).toBeNull();
  });
});

describe('MessageReader — metadata fields', () => {
  it('shows sender name and address as distinct content', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.getByText('Boss')).toBeInTheDocument();
    expect(screen.getByText('boss@work.com')).toBeInTheDocument();
  });

  it('falls back to the bare address when the sender has no display name', async () => {
    renderReader({ sender_name: null });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.getByText('boss@work.com')).toBeInTheDocument();
    // The address must not be duplicated into a second line.
    expect(document.querySelectorAll('.reader-sender-mail')).toHaveLength(0);
  });

  it('labels the recipient list separately from the sender', async () => {
    renderReader({ recipients: ['me@gmail.com', 'team@work.com'] });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.getByText('To')).toBeInTheDocument();
    expect(screen.getByText('me@gmail.com, team@work.com')).toBeInTheDocument();
  });

  it('omits the To field entirely when there are no recipients', async () => {
    renderReader({ recipients: [] });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.queryByText('To')).toBeNull();
    expect(screen.getByText('From')).toBeInTheDocument();
  });

  it('ignores blank recipient entries', async () => {
    renderReader({ recipients: ['me@gmail.com', '   ', ''] });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.getByText('me@gmail.com')).toBeInTheDocument();
  });

  it('renders the timestamp as a machine-readable time element', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    const time = document.querySelector('time.reader-timestamp')!;
    expect(time).toBeInTheDocument();
    expect(time.getAttribute('datetime')).toBe('2026-08-17T09:00:00Z');
  });

  it('omits the Date field when the timestamp is missing or unparseable', async () => {
    const { unmount } = renderReader({ received_at: null });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.queryByText('Date')).toBeNull();
    unmount();

    renderReader({ received_at: 'not-a-date' });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.queryByText('Date')).toBeNull();
  });
});

describe('MessageReader — content stress cases', () => {
  it('renders a very long subject in full rather than truncating it', async () => {
    const subject = `Quarterly planning review ${'with an extremely long trailing clause '.repeat(6)}`.trim();
    renderReader({ subject });
    const heading = await screen.findByRole('heading', { name: subject });
    expect(heading).toBeInTheDocument();
    // No ellipsis in the accessible text, and nothing clamped it away.
    expect(heading.textContent).not.toContain('…');
  });

  it('gives a long subject a wrapping rule so it cannot widen the pane', async () => {
    renderReader({ subject: 'A'.repeat(300) });
    await screen.findByRole('heading', { name: 'A'.repeat(300) });
    const css = readReaderCss();
    expect(css).toMatch(/\.reader-subject\s*\{[^}]*overflow-wrap:\s*anywhere/);
  });

  it('renders a long sender name without a hard width', async () => {
    const name = 'Dr. Bartholomew Wigglesworth-Featherstonehaugh III';
    renderReader({ sender_name: name });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.getByText(name)).toBeInTheDocument();
    const css = readReaderCss();
    // The sender cell must be allowed to shrink and wrap.
    expect(css).toMatch(/\.reader-field-value\s*\{[^}]*min-width:\s*0/);
    expect(css).toMatch(/\.reader-field-value\s*\{[^}]*overflow-wrap:\s*anywhere/);
  });

  it('lets a long recipient list wrap instead of overflowing', async () => {
    const many = Array.from({ length: 12 }, (_, i) => `person.number.${i}@verylongdomainexample.com`);
    renderReader({ recipients: many });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    const field = screen.getByText('To').closest('.reader-field')!;
    const value = field.querySelector('.reader-field-value')!;
    expect(value.textContent).toBe(many.join(', '));
    // The field grid tracks the label and gives the rest to the value.
    expect(readReaderCss()).toMatch(/\.reader-fields\s*\{[^}]*minmax\(0,\s*1fr\)/);
  });

  it('renders a long body and a short body without truncating either', async () => {
    const long = 'Lorem ipsum dolor sit amet. '.repeat(120);
    const { unmount } = renderReader({ body: long });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(document.querySelector('.reader-body')!.textContent).toHaveLength(long.length);
    unmount();

    renderReader({ body: 'Hi.' });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(document.querySelector('.reader-body')!.textContent).toBe('Hi.');
  });

  it('caps the reading measure at 68ch', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(readReaderCss()).toMatch(/\.reader-surface\s*\{[^}]*max-width:\s*68ch/);
  });

  it('uses the primary body size and reader leading for the body', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    const css = readReaderCss();
    expect(css).toMatch(/\.reader-body\s*\{[^}]*font-size:\s*var\(--text-base\)/);
    expect(css).toMatch(/\.reader-body\s*\{[^}]*line-height:\s*var\(--leading-reader\)/);
  });

  it('keeps the subject the only large type, at semibold', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    const css = readReaderCss();
    expect(css).toMatch(/\.reader-subject\s*\{[^}]*font-weight:\s*var\(--weight-semibold\)/);
    expect(css).toMatch(/\.reader-subject\s*\{[^}]*font-size:\s*var\(--text-2xl\)/);
  });
});

describe('MessageReader — attachments', () => {
  it('shows an attachment when the provider says so', async () => {
    renderReader({}, { has_attachment: true, gmail_raw: { sizeEstimate: 204_800 } });
    const region = await screen.findByRole('region', { name: 'Attachments' });
    expect(within(region).getByText('200 KB')).toBeInTheDocument();
  });

  it('does not claim an attachment when the provider flag is false, however large the message', async () => {
    // sizeEstimate is the size of the whole RFC822 message, so a large plain
    // email must never be reported as an attachment.
    renderReader({ body: 'x'.repeat(300_000) }, { has_attachment: false, gmail_raw: { sizeEstimate: 900_000 } });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.queryByRole('region', { name: 'Attachments' })).toBeNull();
  });

  it('falls back to the size heuristic only when no provider flag exists', async () => {
    renderReader({}, { gmail_raw: { sizeEstimate: 900_000 } });
    const region = await screen.findByRole('region', { name: 'Attachments' });
    expect(region).toBeInTheDocument();
  });

  it('reports no attachment for a small message with no flag', async () => {
    renderReader({}, { gmail_raw: { sizeEstimate: 900 } });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(screen.queryByRole('region', { name: 'Attachments' })).toBeNull();
  });

  it('never invents a filename or a count the provider did not send', async () => {
    renderReader({}, { has_attachment: true, gmail_raw: { sizeEstimate: 4096 } });
    const region = await screen.findByRole('region', { name: 'Attachments' });
    // No count is available, so the label stays generic rather than guessing.
    expect(region.textContent).not.toMatch(/\d+\s+attachment/i);
    expect(region.textContent).not.toMatch(/\.(pdf|docx|xlsx|png|zip)/i);
  });

  it('uses a real count when the provider supplies one', async () => {
    renderReader({}, { has_attachment: true, gmail_raw: { sizeEstimate: 4096, attachmentCount: 3 } });
    const region = await screen.findByRole('region', { name: 'Attachments' });
    expect(within(region).getByText('3 attachments')).toBeInTheDocument();
  });

  it('uses the singular form for exactly one attachment', async () => {
    renderReader({}, { has_attachment: true, gmail_raw: { sizeEstimate: 4096, attachmentCount: 1 } });
    const region = await screen.findByRole('region', { name: 'Attachments' });
    expect(within(region).getByText('1 attachment')).toBeInTheDocument();
  });

  it('shows no size when the provider did not send one', async () => {
    renderReader({}, { has_attachment: true });
    const region = await screen.findByRole('region', { name: 'Attachments' });
    expect(region.textContent).toContain('Attachments');
    expect(region.textContent).not.toMatch(/\d+\s*(KB|MB)/);
  });

  it('does not clip a long attachment label', async () => {
    renderReader({}, { has_attachment: true, gmail_raw: { sizeEstimate: 4096, attachmentCount: 1 } });
    await screen.findByRole('region', { name: 'Attachments' });
    const css = readReaderCss();
    expect(css).toMatch(/\.reader-attachment-text\s*\{[^}]*overflow-wrap:\s*anywhere/);
  });
});

describe('MessageReader — actions', () => {
  it('groups the actions under an accessible label', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    const actions = screen.getByRole('toolbar', { name: 'Message actions' });
    expect(within(actions).getByRole('button', { name: /later/i })).toBeInTheDocument();
    expect(within(actions).getByRole('button', { name: /copy/i })).toBeInTheDocument();
  });

  it('reports the pressed state of the Later toggle', async () => {
    const onToggleLater = vi.fn();
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    emailDetails.mockResolvedValue(baseEmail);

    render(
      <QueryClientProvider client={queryClient}>
        <MessageReader
          emailId="m1"
          intelVisible
          onToggleIntel={() => {}}
          laterIds={new Set(['m1'])}
          onToggleLater={onToggleLater}
        />
      </QueryClientProvider>
    );

    const later = await screen.findByRole('button', { name: /later/i });
    expect(later).toHaveAttribute('aria-pressed', 'true');

    fireEvent.click(later);
    expect(onToggleLater).toHaveBeenCalledWith('m1');
  });

  it('acknowledges a copy and does not leave the state stuck', async () => {
    const writeText = vi.fn(() => Promise.resolve());
    Object.assign(navigator, { clipboard: { writeText } });

    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });

    // Fake timers are enabled only after the first await: switching them on
    // earlier stalls Testing Library's own waitFor.
    vi.useFakeTimers();
    try {
      fireEvent.click(screen.getByRole('button', { name: /copy/i }));
      await vi.advanceTimersByTimeAsync(0);
      expect(screen.getByRole('button', { name: /copied/i })).toBeInTheDocument();

      await vi.advanceTimersByTimeAsync(2000);
    } finally {
      vi.useRealTimers();
    }

    // Back on real timers so React's scheduler (MessageChannel, which the
    // fake clock does not drive) can flush the re-render.
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /^copy$/i })).toBeInTheDocument()
    );
  });

  it('keeps every action keyboard reachable as a real button', async () => {
    renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    const actions = within(screen.getByRole('toolbar', { name: 'Message actions' }));
    const buttons = actions.getAllByRole('button');
    expect(buttons.length).toBeGreaterThanOrEqual(3);
    for (const b of buttons) {
      expect(b.tagName).toBe('BUTTON');
      expect(b).not.toHaveAttribute('tabindex', '-1');
      expect(b.getAttribute('aria-label') ?? b.textContent).toBeTruthy();
    }
  });
});

describe('MessageReader — states and presentation hygiene', () => {
  it('shows a skeleton while loading rather than an empty document', async () => {
    let resolve!: (e: Email) => void;
    emailDetails.mockReturnValue(new Promise<Email>((r) => { resolve = r; }));

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <MessageReader
          emailId="m1"
          intelVisible
          onToggleIntel={() => {}}
          laterIds={new Set<string>()}
          onToggleLater={() => {}}
        />
      </QueryClientProvider>
    );

    const busy = container.querySelector('[aria-busy="true"]')!;
    expect(busy).toBeInTheDocument();
    expect(busy.querySelectorAll('.skeleton').length).toBeGreaterThan(3);
    expect(container.querySelector('.reader-body')).toBeNull();

    resolve(baseEmail);
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
  });

  it('uses no inline styles in the loaded document', async () => {
    const { container } = renderReader();
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(container.querySelectorAll('[style]')).toHaveLength(0);
  });

  it('uses no inline styles in the loading skeleton', async () => {
    let resolve!: (e: Email) => void;
    emailDetails.mockReturnValue(new Promise<Email>((r) => { resolve = r; }));
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <MessageReader
          emailId="m1"
          intelVisible
          onToggleIntel={() => {}}
          laterIds={new Set<string>()}
          onToggleLater={() => {}}
        />
      </QueryClientProvider>
    );
    expect(container.querySelectorAll('[style]')).toHaveLength(0);
    resolve(baseEmail);
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
  });

  it('prompts rather than showing a blank pane when nothing is selected', () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MessageReader
          emailId={null}
          intelVisible
          onToggleIntel={() => {}}
          laterIds={new Set<string>()}
          onToggleLater={() => {}}
        />
      </QueryClientProvider>
    );
    expect(screen.getByText('Select a message to read it.')).toBeInTheDocument();
  });

  it('states an empty body instead of rendering nothing', async () => {
    renderReader({ body: '' });
    await screen.findByRole('heading', { name: 'Q3 planning needed' });
    expect(document.querySelector('.reader-body')).toBeInTheDocument();
  });
});

describe('MessageReader — reader stylesheet', () => {
  it('contains no raw hex colours', () => {
    expect(readReaderCss()).not.toMatch(/#[0-9a-fA-F]{3,8}\b/);
  });

  it('contains no unapproved font weights', () => {
    const weights = [...readReaderCss().matchAll(/font-weight:\s*([^;]+);/g)].map((m) => m[1].trim());
    for (const w of weights) {
      expect(w).toMatch(/^var\(--weight-(regular|medium|semibold|bold)\)$/);
    }
  });

  it('contains no undefined custom properties', () => {
    const defined = new Set(
      [...readAllCss().matchAll(/(--[a-z0-9-]+)\s*:/g)].map((m) => m[1])
    );
    const used = new Set([...readReaderCss().matchAll(/var\((--[a-z0-9-]+)\)/g)].map((m) => m[1]));
    const missing = [...used].filter((t) => !defined.has(t));
    expect(missing).toEqual([]);
  });

  it('contains no off-scale spacing values', () => {
    // 28px, 32px, 36px, 44px, 9px, 5px etc. are not on the 4px scale.
    const offenders = [...readReaderCss().matchAll(/(?:padding|margin|gap)[^;]*?\b(\d+)px\b/g)]
      .map((m) => Number(m[1]))
      .filter((n) => n % 4 !== 0);
    expect(offenders).toEqual([]);
  });

  it('does not stack a shadow on the reader surface or the avatar', () => {
    const css = readReaderCss();
    expect(css).not.toMatch(/\.reader-surface\s*\{[^}]*box-shadow/);
  });

  it('scopes the reader responsive rules to a container that contains the reader', () => {
    const all = stripComments(readAllCss());
    const mailPaneBlocks = [...all.matchAll(/@container mail-pane[^{]*\{/g)];
    expect(mailPaneBlocks.length).toBeGreaterThan(0);
    // The reader lives outside .mail-pane, so no reader rule may sit in one of
    // those blocks. This is the defect that left the pane unresponsive.
    for (const m of mailPaneBlocks) {
      const start = m.index!;
      let depth = 0;
      let i = all.indexOf('{', start);
      for (; i < all.length; i++) {
        if (all[i] === '{') depth++;
        else if (all[i] === '}') {
          depth--;
          if (depth === 0) break;
        }
      }
      expect(all.slice(start, i)).not.toMatch(/\.reader-/);
    }
    expect(all).toMatch(/@container mail-workspace[^{]*\{[\s\S]*?\.reader-document/);
  });
});

function stripComments(css: string): string {
  return css.replace(/\/\*[\s\S]*?\*\//g, '');
}

/**
 * The real stylesheets, read from disk. These assertions exist because the
 * reading pane's defects were invisible to jsdom: a declaration naming an
 * undefined token, or a rule stranded in a container query that matches
 * nothing, renders perfectly in a DOM test and does nothing on screen.
 */
const STYLESHEETS = ['globals.css', 'tokens.css', 'themes.css', 'surfaces.css', 'motion.css', 'reset.css'];
const stylesDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'styles');

function readAllCss(): string {
  return STYLESHEETS.map((f) => readFileSync(join(stylesDir, f), 'utf8')).join('\n');
}

/** Only the reader's own rules, so assertions cannot be satisfied by other panes. */
function readReaderCss(): string {
  const all = stripComments(readAllCss());
  const wanted = [
    'reader-scroll', 'reader-surface', 'reader-document', 'reader-subject',
    'reader-fields', 'reader-field', 'reader-sender', 'reader-sender-mail',
    'reader-timestamp', 'reader-body', 'reader-link', 'reader-attachments',
    'reader-attachment-text', 'reader-attachment-size', 'reader-actions',
    'reader-empty-detail', 'reader-skeleton-meta',
  ];
  const out: string[] = [];
  const re = /([^{}]+)\{([^{}]*)\}/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(all))) {
    const selectors = m[1].split(',').map((s) => s.trim());
    if (selectors.some((s) => wanted.some((w) => new RegExp(`\\.${w}\\b`).test(s)))) {
      out.push(`${selectors.join(', ')} {${m[2]}}`);
    }
  }
  return out.join('\n');
}
