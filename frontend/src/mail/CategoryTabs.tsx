import { useCallback, useRef } from 'react';
import type { KeyboardEvent } from 'react';
import type { MailCategory, EmailCounts } from '../api/emails';

export const CATEGORY_META: Record<MailCategory, { label: string; aria: string }> = {
  primary: { label: 'Primary', aria: 'Primary mail' },
  promotions: { label: 'Promotions', aria: 'Promotions mail' },
  social: { label: 'Social', aria: 'Social mail' },
  updates: { label: 'Updates', aria: 'Updates mail' },
  forums: { label: 'Forums', aria: 'Forums mail' },
};

interface CategoryTabsProps {
  categories: MailCategory[];
  active: MailCategory;
  counts?: EmailCounts;
  onChange: (category: MailCategory) => void;
}

export function CategoryTabs({ categories, active, counts, onChange }: CategoryTabsProps) {
  const tabRefs = useRef<Map<MailCategory, HTMLButtonElement>>(new Map());

  const setTabRef = useCallback((category: MailCategory, el: HTMLButtonElement | null) => {
    if (el) {
      tabRefs.current.set(category, el);
    } else {
      tabRefs.current.delete(category);
    }
  }, []);

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLDivElement>) => {
    const currentIndex = categories.indexOf(active);
    if (currentIndex === -1) return;

    let nextIndex: number;

    switch (e.key) {
      case 'ArrowRight':
        nextIndex = (currentIndex + 1) % categories.length;
        break;
      case 'ArrowLeft':
        nextIndex = (currentIndex - 1 + categories.length) % categories.length;
        break;
      case 'Home':
        nextIndex = 0;
        break;
      case 'End':
        nextIndex = categories.length - 1;
        break;
      default:
        return;
    }

    e.preventDefault();
    const nextCategory = categories[nextIndex];
    onChange(nextCategory);
    tabRefs.current.get(nextCategory)?.focus();
  }, [categories, active, onChange]);

  return (
    <div
      className="category-tabs"
      role="tablist"
      aria-label="Mail categories"
      onKeyDown={handleKeyDown}
    >
      {categories.map(category => {
        const count = counts?.categories[category] ?? 0;
        const meta = CATEGORY_META[category];
        const isActive = active === category;
        return (
          <button
            key={category}
            ref={el => setTabRef(category, el)}
            type="button"
            role="tab"
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            aria-label={`${meta.aria}${count > 0 ? `, ${count} messages` : ''}`}
            className={`category-tab ${isActive ? 'active' : ''}`}
            onClick={() => onChange(category)}
          >
            <span>{meta.label}</span>
            <span className="tab-count">{count}</span>
          </button>
        );
      })}
    </div>
  );
}
