/**
 * Mail workspace pane-layout persistence with strict validation.
 *
 * react-resizable-panels v4 interprets NUMERIC Panel sizes as PIXELS and
 * STRING sizes as percentages. Alfred's panels therefore use explicit
 * percentage strings (PANEL_CONSTRAINTS); Group layouts remain percentage
 * numbers (Layout = { [id]: number }). Never pass numeric Panel sizes.
 *
 * Storage key is versioned (v2): layouts persisted by the old numeric
 * implementation are ignored so a stale value can never trap a panel.
 */

export interface PaneLayout {
  mail: number;
  reader: number;
  intel: number;
  // Index signature so the layout is assignable to
  // react-resizable-panels' `{ [panelId: string]: number }` slots.
  [panelId: string]: number;
}

export const LAYOUT_KEY = 'alfred-pane-layout-v2';

/** Panel constraints as percentage STRINGS (v4: numbers would be pixels). */
export const PANEL_CONSTRAINTS = {
  mail: { minSize: '20%', maxSize: '45%' },
  reader: { minSize: '30%' },
  intel: { minSize: '0%', maxSize: '40%', collapsedSize: '0%' },
} as const;

export const DEFAULT_LAYOUT: PaneLayout = {
  mail: 30,
  reader: 45,
  intel: 25,
};

// Validation ranges mirror the constraints above with small float
// tolerance (the library may report 29.97 for a 30% panel). Reader has no
// upper constraint in the UI, so only the total bounds it from above.
const RANGES: Record<'mail' | 'reader' | 'intel', [number, number]> = {
  mail: [18, 47],
  reader: [28, 100],
  intel: [0, 42],
};

function isValidPane(value: unknown, [lo, hi]: [number, number]): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value >= lo && value <= hi;
}

/**
 * Validate an unknown parsed value as a PaneLayout.
 * Returns the layout when every pane is numeric, finite, in range, and
 * the total is sane for react-resizable-panels (~100); otherwise null.
 * Stale v1 values (stored under a different key) are never read at all —
 * see LAYOUT_KEY.
 */
export function validateLayout(value: unknown): PaneLayout | null {
  if (typeof value !== 'object' || value === null) return null;
  const record = value as Record<string, unknown>;
  if (!isValidPane(record.mail, RANGES.mail)) return null;
  if (!isValidPane(record.reader, RANGES.reader)) return null;
  if (!isValidPane(record.intel, RANGES.intel)) return null;
  const total = (record.mail as number) + (record.reader as number) + (record.intel as number);
  if (!Number.isFinite(total) || total < 98 || total > 102) return null;
  return { mail: record.mail as number, reader: record.reader as number, intel: record.intel as number };
}

export function readSavedLayout(): PaneLayout | null {
  try {
    const raw = localStorage.getItem(LAYOUT_KEY);
    if (!raw) return null;
    return validateLayout(JSON.parse(raw));
  } catch {
    return null;
  }
}

export function persistLayout(layout: PaneLayout): void {
  try {
    if (!validateLayout(layout)) return; // never persist a broken layout
    localStorage.setItem(LAYOUT_KEY, JSON.stringify(layout));
  } catch {
    /* storage unavailable */
  }
}
