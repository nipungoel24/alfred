import { Monitor, Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import type { ThemePreference } from './themeStore';

const OPTIONS: { value: ThemePreference; label: string; icon: typeof Sun }[] = [
  { value: 'system', label: 'System', icon: Monitor },
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
];

export function ThemeToggle() {
  const { preference, setPreference } = useTheme();

  return (
    <div className="theme-toggle" role="radiogroup" aria-label="Theme">
      {OPTIONS.map(({ value, label, icon: Icon }) => (
        <button
          key={value}
          type="button"
          role="radio"
          aria-checked={preference === value}
          className={`theme-toggle-option ${preference === value ? 'active' : ''}`}
          onClick={() => setPreference(value)}
          title={`${label} theme`}
        >
          <Icon size={14} strokeWidth={2} aria-hidden="true" />
          <span>{label}</span>
        </button>
      ))}
    </div>
  );
}
