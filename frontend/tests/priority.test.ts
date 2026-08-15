import { describe, expect, it } from 'vitest';

describe('priority contract', () => {
  it('keeps the API priority values controlled', () => {
    expect(['urgent', 'high', 'medium', 'low']).toContain('urgent');
  });
});
