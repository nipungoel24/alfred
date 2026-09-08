/**
 * Mail workspace pane-layout persistence with strict validation.
 *
 * react-resizable-panels reports sizes as percentages that must sum to
 * ~100. A corrupted localStorage value must never produce an unusable
 * workspace — invalid layouts are ignored and defaults are used.
 */

export interface PaneLayout {
  mail: number;
  reader: number;
  intel: number;
  // Index signature so the layout is assignable to
  // react-resizable-panels' `{ [panelId: string]: number }` slots.
  [panelId: string]: number;
}

export const LAYOUT_KEY = 'alfred-pane-layout';

export const DEFAULT_LAYOUT: PaneLayout = {
  mail: 30,
  reader: 45,
  intel: 25,
};

// Sensible bounds per pane (percent). Intel may collapse to 0.
const RANGES: Record<keyof PaneLayout, [number, number]> = {
  mail: [15, 60],
  reader: [20, 70],
  intel: [0, 50],
};

function isValidPane(value: unknown, [lo, hi]: [number, number]): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value >= lo && value <= hi;
}

/**
 * Validate an unknown parsed value as a PaneLayout.
 * Returns the layout when every pane is numeric, finite, in range, and
 * the total is sane for react-resizable-panels (~100); otherwise null.
 */
export function validateLayout(value: unknown): PaneLayout | null {
  if (typeof value !== 'object' || value === null) return null;
  const record = value as Record<string, unknown>;
  if (!isValidPane(record.mail, RANGES.mail)) return null;
  if (!isValidPane(record.reader, RANGES.reader)) return null;
  if (!isValidPane(record.intel, RANGES.intel)) return null;
  const total = (record.mail as number) + (record.reader as number) + (record.intel as number);
  if (!Number.isFinite(total) || total < 99 || total > 101) return null;
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
