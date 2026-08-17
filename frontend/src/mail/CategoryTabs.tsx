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
  return (
    <div className="category-tabs" role="tablist" aria-label="Mail categories">
      {categories.map(category => {
        const count = counts?.categories[category] ?? 0;
        const meta = CATEGORY_META[category];
        return (
          <button
            key={category}
            type="button"
            role="tab"
            aria-selected={active === category}
            aria-label={`${meta.aria}${count > 0 ? `, ${count} messages` : ''}`}
            className={`category-tab ${active === category ? 'active' : ''}`}
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
