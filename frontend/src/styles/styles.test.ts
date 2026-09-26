/// <reference types="node" />
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

/**
 * Stylesheet correctness gate.
 *
 * Every defect this file guards against was invisible to a DOM test. A custom
 * property that is referenced but never defined makes its whole declaration
 * invalid at computed-value time, so the element renders with *no* style rather
 * than a wrong one. A rule parked in a container query that names an ancestor the
 * element is not inside never matches at all. Both look perfect from jsdom.
 */

const STYLES_DIR = join(dirname(fileURLToPath(import.meta.url)));
const SHEETS = ['reset.css', 'tokens.css', 'themes.css', 'surfaces.css', 'motion.css', 'globals.css'];

const raw = SHEETS.map((f) => readFileSync(join(STYLES_DIR, f), 'utf8'));
const sheets = new Map(SHEETS.map((f, i) => [f, raw[i]]));
/** All CSS with comments removed, so prose in a comment is never read as code. */
const all = stripComments(raw.join('\n'));

function stripComments(css: string): string {
  return css.replace(/\/\*[\s\S]*?\*\//g, '');
}

/** Custom properties that CSS resolves without a stylesheet definition. */
const NATIVE_PROPERTIES = new Set([
  'currentcolor', 'inherit', 'initial', 'unset', 'revert', 'revert-layer',
]);

/** Every `var()` reference, with whether it supplies a fallback. */
function varReferences(css: string): { token: string; fallback: boolean }[] {
  const out: { token: string; fallback: boolean }[] = [];
  for (const m of css.matchAll(/var\(\s*(--[a-z0-9-]+)\s*([,)])/g)) {
    out.push({ token: m[1], fallback: m[2] === ',' });
  }
  return out;
}

/** Every custom property that some stylesheet actually assigns. */
function definedTokens(css: string): Set<string> {
  return new Set([...css.matchAll(/(--[a-z0-9-]+)\s*:/g)].map((m) => m[1]));
}

const defined = definedTokens(all);

describe('stylesheets: custom properties', () => {
  it('references no custom property that is neither defined nor given a fallback', () => {
    const dangling = varReferences(all)
      .filter((r) => !defined.has(r.token) && !r.fallback && !NATIVE_PROPERTIES.has(r.token))
      .map((r) => r.token);

    expect([...new Set(dangling)]).toEqual([]);
  });

  it.each(SHEETS)('%s defines or falls back on every property it uses', (sheet) => {
    const dangling = varReferences(stripComments(sheets.get(sheet)!))
      .filter((r) => !defined.has(r.token) && !r.fallback)
      .map((r) => r.token);
    expect([...new Set(dangling)]).toEqual([]);
  });

  it('keeps the four retired tokens out of the codebase entirely', () => {
    // Removed deliberately; see UI-DESIGN-SPEC section 15. If one reappears it
    // has been reintroduced without a decision.
    for (const token of [
      '--highlight-top', '--reader-border', '--radius-xl',
      '--shadow-accent', '--bg-panel-solid', '--danger-border',
    ]) {
      expect(all, `${token} must not be referenced or defined`).not.toContain(token);
    }
  });

  it('permits a locally-set property that carries a fallback', () => {
    // --stagger is set inline per element and falls back to 0. That is a
    // deliberate pattern, not a dangling reference.
    expect(all).toMatch(/var\(\s*--stagger\s*,/);
  });
});

describe('stylesheets: design tokens', () => {
  it('uses no raw hex colour outside the canonical token layer', () => {
    // tokens.css and themes.css are where colour values are *supposed* to live.
    // A hex inside a var() fallback is not a raw reference: it is a guarded
    // default for a token that does resolve, and it never paints.
    const offenders: string[] = [];
    for (const [name, css] of sheets) {
      if (name === 'tokens.css' || name === 'themes.css') continue;
      const body = stripComments(css).replace(/var\([^)]*\)/g, '');
      for (const m of body.matchAll(/#[0-9a-fA-F]{3,8}\b/g)) {
        offenders.push(`${name}: ${m[0]}`);
      }
    }
    expect(offenders).toEqual([]);
  });

  it('expresses every font weight as one of the four scale tokens', () => {
    const weights = [...all.matchAll(/font-weight:\s*([^;}]+)[;}]/g)]
      .map((m) => m[1].trim())
      .filter((w) => !w.startsWith('var(') && !['normal', 'bold', 'bolder', 'lighter', 'inherit'].includes(w));
    expect(weights).toEqual([]);
  });

  it('defines exactly the four weight steps and no others', () => {
    const values = new Set([...all.matchAll(/--weight-[\w-]+\s*:\s*(\d+)/g)].map((m) => m[1]));
    expect([...values].sort()).toEqual(['400', '500', '600', '700']);
  });

  it('keeps literal radii to the cases the spec allows', () => {
    // 50% is a circle (status dot, spinner — spec 4). A `::after` tab indicator
    // is indicator geometry, not a surface corner. Everything else must come
    // from the radius scale.
    const offenders: string[] = [];
    for (const [name, css] of sheets) {
      if (name === 'reset.css') continue; // browser chrome only
      for (const m of stripComments(css).matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
        const v = /border-radius:\s*([^;}]+)/.exec(m[2]);
        if (!v) continue;
        const value = v[1].trim();
        const isIndicator = m[1].split(',').some((s) => s.trim().endsWith('::after'));
        if (value.startsWith('var(') || value === '50%' || isIndicator) continue;
        offenders.push(`${name}: ${m[1].split(/\s+/).join(' ').slice(0, 32)} -> ${value}`);
      }
    }
    expect(offenders).toEqual([]);
  });

  it('defines every radius in the approved scale', () => {
    for (const t of ['--radius-xs', '--radius-sm', '--radius-md', '--radius-lg', '--radius-full']) {
      expect(defined, `${t} must be defined`).toContain(t);
    }
  });

  it('uses no tinted glow: a blurred shadow must not carry a semantic colour', () => {
    // Spec 6: shadow is elevation, never decoration, and "no coloured shadow".
    // A zero-blur spread ring is a focus indicator, which spec 5 and 11 require,
    // so only shadows carrying a real blur are in scope.
    const glows: string[] = [];
    for (const m of all.matchAll(/box-shadow:\s*([^;}]+)/g)) {
      for (const layer of m[1].split(',')) {
        if (!/--(accent|success|danger|warning|info)/.test(layer)) continue;
        const parts = layer.trim().replace(/^inset\s+/, '').split(/\s+/);
        const blur = parts.length >= 3 ? Number(parts[2].replace('px', '')) : 0;
        if (blur > 0) glows.push(m[0].split(/\s+/).join(' '));
      }
    }
    expect(glows).toEqual([]);
  });

  it('keeps a focus ring on focusable controls', () => {
    // The counterpart to the rule above: dropping glow must not drop the focus
    // indicator itself.
    expect(all).toMatch(/box-shadow:\s*0 0 0 3px var\(--accent-soft\)/);
    const focusRules = [...all.matchAll(/([^{}]*focus[^{}]*)\{([^{}]*)\}/g)]
      .filter(([, , body]) => /box-shadow|outline/.test(body));
    expect(focusRules.length).toBeGreaterThan(3);
  });

  it('uses no shadow on the tokens the spec reserves for overlays only', () => {
    // --shadow-3 is the modal token, for SourceEmailPreview alone.
    const users = sheets.get('globals.css')!;
    const blocks = [...stripComments(users).matchAll(/([^{}]+)\{([^{}]*)\}/g)];
    const shadow3 = blocks
      .filter(([, body]) => /box-shadow:[^;}]*--shadow-3/.test(body))
      .map(([sel]) => sel.split(/\s+/).join(' ').split(',')[0].trim());
    for (const sel of shadow3) {
      expect(
        ['.source-preview', '.analysis-progress-bar'],
        `${sel} uses --shadow-3`
      ).toContain(sel);
    }
  });
});

describe('stylesheets: container queries are reachable', () => {
  /**
   * The DOM relationship, asserted rather than assumed. `.mail-pane` is the only
   * element that establishes `container-name: mail-pane`, and the reader and the
   * intelligence pane are siblings of it — not descendants. A rule for either
   * written inside `@container mail-pane` therefore matches nothing at all.
   */
  const CONTAINERS: Record<string, { selector: string; contains: string[] }> = {
    'mail-pane': {
      selector: '.mail-pane',
      // Classes that live inside the list pane.
      contains: ['mail-pane-head', 'mail-pane-toolbar', 'mail-view-switch', 'pane-filter', 'category-tab'],
    },
    'mail-workspace': {
      selector: '.mail-workspace',
      // Siblings of the list pane: the reader and the intelligence pane.
      contains: ['reader-', 'intel-'],
    },
  };

  function containerQueryBlocks(css: string) {
    const out: { name: string; condition: string; selectors: string[] }[] = [];
    for (const m of css.matchAll(/@container\s+([a-z-]+)\s*(\([^)]*\))?\s*\{/g)) {
      const name = m[1];
      const start = m.index;
      let depth = 0;
      let i = css.indexOf('{', start);
      for (; i < css.length; i++) {
        if (css[i] === '{') depth++;
        else if (css[i] === '}') {
          depth--;
          if (depth === 0) break;
        }
      }
      out.push({ name, condition: (m[2] ?? '').trim(), selectors: selectorsIn(css.slice(start, i + 1)) });
    }
    return out;
  }

  function selectorsIn(block: string): string[] {
    const out: string[] = [];
    let depth = 0;
    let buf = '';
    for (const ch of block) {
      if (ch === '{') {
        if (depth >= 1) out.push(buf.trim());
        depth++;
        buf = '';
      } else if (ch === '}') {
        depth--;
        buf = '';
      } else if (depth >= 1) {
        buf += ch;
      }
    }
    return out.flatMap((s) => s.split(',').map((x) => x.trim())).filter(Boolean);
  }

  it('declares every container name that a query relies on', () => {
    const names = new Set([...all.matchAll(/container-name:\s*([a-z-]+)/g)].map((m) => m[1]));
    const used = new Set(containerQueryBlocks(all).map((b) => b.name));
    expect([...used].filter((n) => !names.has(n))).toEqual([]);
  });

  it('parks no reader or intelligence rule inside a container that cannot reach it', () => {
    const wrong: string[] = [];
    for (const block of containerQueryBlocks(all)) {
      const spec = CONTAINERS[block.name];
      if (!spec) continue;
      for (const sel of block.selectors) {
        const isReaderOrIntel = /(^|[\s,>])\.(reader|intel)-/.test(sel);
        const belongsToMailPane = spec.contains.some(
          (c) => sel.includes(`.${c}`) && !c.endsWith('-')
        );
        if (isReaderOrIntel && belongsToMailPane) {
          wrong.push(`@container ${block.name} ${block.condition} -> ${sel}`);
        }
      }
    }
    expect(wrong).toEqual([]);
  });

  it('keeps the intelligence responsive rules in a container that contains them', () => {
    const blocks = containerQueryBlocks(all);
    const intelRules = blocks.flatMap((b) =>
      b.selectors.filter((s) => /(^|[\s,>])\.intel-/.test(s)).map((s) => ({ container: b.name, sel: s }))
    );
    // The 900px intelligence compression must exist, and must be reachable.
    expect(intelRules.map((r) => r.sel).sort()).toEqual(['.intel-head', '.intel-scroll']);
    for (const r of intelRules) {
      expect(r.container, `${r.sel} must live in a container that contains it`).toBe('mail-workspace');
    }
  });

  it('keeps the reading pane responsive rules in a container that contains it', () => {
    const blocks = containerQueryBlocks(all);
    const readerRules = blocks.flatMap((b) =>
      b.selectors.filter((s) => /(^|[\s,>])\.reader-/.test(s)).map((s) => ({ container: b.name, sel: s }))
    );
    expect(readerRules.length).toBeGreaterThan(0);
    for (const r of readerRules) {
      expect(r.container, `${r.sel} must live in a container that contains it`).toBe('mail-workspace');
    }
  });

  it('does not let a container query touch the 1100px rail collapse', () => {
    // The rail collapse is chrome: window media query only, per spec section 13.
    for (const block of containerQueryBlocks(all)) {
      for (const sel of block.selectors) {
        expect(sel, `${sel} must not be pane-internal chrome`).not.toMatch(/\.(app-shell|rail-|header-search)\b/);
      }
    }
    expect(all).toMatch(/@media\s*\(max-width:\s*1100px\)/);
  });
});

describe('stylesheets: no duplicated or conflicting declarations', () => {
  it('declares each real property at most once per rule', () => {
    // Custom properties are excluded: their names contain digits and would be
    // mis-parsed as bare property names.
    const offenders: string[] = [];
    for (const [, sel, body] of all.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
      const seen = new Map<string, number>();
      for (const m of body.matchAll(/(^|[;{\s])([a-z][a-z-]*)\s*:/g)) {
        if (m[2].startsWith('-')) continue;
        seen.set(m[2], (seen.get(m[2]) ?? 0) + 1);
      }
      for (const [prop, n] of seen) {
        if (n > 1) offenders.push(`${sel.split(/\s+/).join(' ').slice(0, 40)}: ${prop} x${n}`);
      }
    }
    expect(offenders).toEqual([]);
  });

  it('never defines the identical selector twice in flat scope', () => {
    // This is the `.skeleton` bug: two identical rule blocks, the second
    // silently winning. `:hover` / `::before` variants are *different*
    // selectors and are not flagged — only exact repeats are.
    const ranges: [number, number][] = [];
    for (const m of all.matchAll(/@(container|media)[^{]*\{/g)) {
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
      ranges.push([start, i + 1]);
    }
    const flat = [...ranges]
      .sort((a, b) => b[0] - a[0])
      .reduce((acc, [from, to]) => acc.slice(0, from) + ' '.repeat(to - from) + acc.slice(to), all);

    const seen = new Map<string, number>();
    for (const m of flat.matchAll(/([^{}]+)\{[^{}]*\}/g)) {
      for (const sel of m[1].split(',')) {
        const key = sel.trim().replace(/\s+/g, ' ');
        if (!key.startsWith('.')) continue;
        seen.set(key, (seen.get(key) ?? 0) + 1);
      }
    }
    expect([...seen].filter(([, n]) => n > 1).map(([c, n]) => `${c} x${n}`)).toEqual([]);
  });
});

describe('stylesheets: no horizontal overflow introduced', () => {
  it('gives every reader and intelligence text container a shrink-and-wrap rule', () => {
    // `.intel-scroll` is the scroll container, not a text container. `.reader-sender`
    // inherits from `.reader-field-value`, which is the rule that matters.
    const mustWrap = [
      '.reader-subject', '.reader-field-value', '.reader-body',
      '.reader-attachment-text', '.intel-summary', '.intel-item',
    ];
    const css = stripComments(sheets.get('globals.css')!);
    for (const sel of mustWrap) {
      const rule = new RegExp(
        `\\${sel}\\s*\\{[^}]*overflow-wrap:\\s*(anywhere|break-word)`,
      );
      expect(css, `${sel} must be able to wrap`).toMatch(rule);
    }
  });

  it('never sets a fixed width on the reader document', () => {
    const css = stripComments(sheets.get('globals.css')!);
    expect(css).not.toMatch(/\.reader-(?:document|surface|scroll)\s*\{[^}]*\bwidth:\s*\d+px/);
  });

  it('caps the reading measure with a ch-based token', () => {
    const css = stripComments(sheets.get('globals.css')!);
    expect(css).toMatch(/\.reader-surface\s*\{[^}]*max-width:\s*68ch/);
  });
});
