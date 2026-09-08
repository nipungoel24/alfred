import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CategoryTabs } from './CategoryTabs';
import { CATEGORY_ORDER } from '../api/emails';

const counts = {
  active_inbox: 7,
  all_mail: 9,
  excluded: 2,
  categories: { primary: 3, promotions: 2, social: 0, updates: 1, forums: 1 },
};

describe('CategoryTabs', () => {
  it('renders all five Gmail categories with live counts', () => {
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="primary" counts={counts} onChange={() => {}} />
    );
    for (const label of ['Primary', 'Promotions', 'Social', 'Updates', 'Forums']) {
      expect(screen.getByRole('tab', { name: new RegExp(label) })).toBeInTheDocument();
    }
    expect(screen.getByRole('tab', { name: /Promotions mail, 2 messages/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Social mail/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Social mail/ }).textContent).toContain('0');
  });

  it('marks the active tab and switches on click', () => {
    const onChange = vi.fn();
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="primary" counts={counts} onChange={onChange} />
    );
    const promo = screen.getByRole('tab', { name: /Promotions/ });
    expect(screen.getByRole('tab', { name: /Primary/ })).toHaveAttribute('aria-selected', 'true');
    expect(promo).toHaveAttribute('aria-selected', 'false');

    fireEvent.click(promo);
    expect(onChange).toHaveBeenCalledWith('promotions');
  });

  it('navigates with ArrowRight from first to last tab wrapping', () => {
    const onChange = vi.fn();
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="primary" counts={counts} onChange={onChange} />
    );
    const tablist = screen.getByRole('tablist');
    fireEvent.keyDown(tablist, { key: 'ArrowRight' });
    expect(onChange).toHaveBeenCalledWith('promotions');
  });

  it('navigates with ArrowLeft from first tab wrapping to last', () => {
    const onChange = vi.fn();
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="primary" counts={counts} onChange={onChange} />
    );
    const tablist = screen.getByRole('tablist');
    fireEvent.keyDown(tablist, { key: 'ArrowLeft' });
    expect(onChange).toHaveBeenCalledWith('forums');
  });

  it('navigates to first tab with Home key', () => {
    const onChange = vi.fn();
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="social" counts={counts} onChange={onChange} />
    );
    const tablist = screen.getByRole('tablist');
    fireEvent.keyDown(tablist, { key: 'Home' });
    expect(onChange).toHaveBeenCalledWith('primary');
  });

  it('navigates to last tab with End key', () => {
    const onChange = vi.fn();
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="primary" counts={counts} onChange={onChange} />
    );
    const tablist = screen.getByRole('tablist');
    fireEvent.keyDown(tablist, { key: 'End' });
    expect(onChange).toHaveBeenCalledWith('forums');
  });

  it('does not call onChange for unsupported keys', () => {
    const onChange = vi.fn();
    render(
      <CategoryTabs categories={CATEGORY_ORDER} active="primary" counts={counts} onChange={onChange} />
    );
    const tablist = screen.getByRole('tablist');
    fireEvent.keyDown(tablist, { key: 'Enter' });
    expect(onChange).not.toHaveBeenCalled();
  });
});
