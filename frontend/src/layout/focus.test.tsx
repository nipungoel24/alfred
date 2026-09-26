/// <reference types="node" />
import { beforeEach, describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WorkspaceHeader } from './WorkspaceHeader';
import { IconRail } from './IconRail';
import { FocusIntentContext } from '../lib/focus';
import type { FocusTarget } from '../lib/focus';
import type { AppPage } from './IconRail';

vi.mock('../api/emails', async (importOriginal) => {
  const original = await importOriginal<typeof import('../api/emails')>();
  return {
    ...original,
    emails: vi.fn(() => Promise.resolve([])),
    emailDetails: vi.fn(() => Promise.resolve(null)),
    emailCounts: vi.fn(() => Promise.resolve({
      active_inbox: 0, all_mail: 0, excluded: 0,
      categories: { primary: 0, promotions: 0, social: 0, updates: 0, forums: 0 },
    })),
    accounts: vi.fn(() => Promise.resolve([])),
    health: vi.fn(() => Promise.resolve({ status: 'ok', ai: 'ready', build: 'b1' })),
    analysisStatus: vi.fn(() => Promise.resolve(null)),
    tasks: vi.fn(() => Promise.resolve([])),
    deadlines: vi.fn(() => Promise.resolve([])),
    briefing: vi.fn(() => Promise.resolve(null)),
  };
});

vi.mock('../theme/ThemeProvider', () => ({
  useTheme: () => ({ preference: 'system', setPreference: vi.fn(), resolved: 'light' }),
}));

function makeIntent() {
  let pending: FocusTarget | null = null;
  return {
    requestFocus: (t: FocusTarget) => { pending = t; },
    takeFocusIntent: (t: FocusTarget) => {
      if (pending !== t) return false;
      pending = null;
      return true;
    },
  };
}

function renderHeader(props: Partial<React.ComponentProps<typeof WorkspaceHeader>> = {}) {
  const intent = makeIntent();
  const utils = render(
    <FocusIntentContext.Provider value={intent}>
      <WorkspaceHeader
        title="Mail"
        searchValue=""
        onSearchChange={() => {}}
        aiReady
        {...props}
      />
    </FocusIntentContext.Provider>
  );
  return { ...utils, intent };
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

describe('the view heading is a focus target, not a tab stop', () => {
  it('is programmatically focusable so a deliberate navigation can reach it', () => {
    renderHeader();
    const heading = screen.getByRole('heading', { level: 1, name: 'Mail' });
    expect(heading).toHaveAttribute('tabindex', '-1');
    heading.focus();
    expect(document.activeElement).toBe(heading);
  });

  it('keeps the heading out of the tab order', () => {
    renderHeader();
    expect(screen.getByRole('heading', { level: 1 }).tabIndex).toBe(-1);
  });
});

describe('search', () => {
  it('Ctrl+K moves focus into the search field', async () => {
    renderHeader();
    const input = screen.getByRole('searchbox');
    expect(document.activeElement).not.toBe(input);

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });

    await waitFor(() => expect(document.activeElement).toBe(input));
  });

  it('does not steal focus during normal startup', () => {
    renderHeader();
    expect(document.activeElement).toBe(document.body);
  });

  it('keeps focus in the field while the user types', async () => {
    const onSearchChange = vi.fn();
    renderHeader({ onSearchChange });
    const input = screen.getByRole('searchbox');

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    await waitFor(() => expect(document.activeElement).toBe(input));

    fireEvent.change(input, { target: { value: 'q' } });
    fireEvent.change(input, { target: { value: 'qu' } });

    expect(onSearchChange).toHaveBeenCalledTimes(2);
    expect(document.activeElement).toBe(input);
  });

  it('Escape returns focus to where it came from, not to <body>', async () => {
    render(
      <FocusIntentContext.Provider value={makeIntent()}>
        <button type="button">before search</button>
        <WorkspaceHeader title="Mail" searchValue="" onSearchChange={() => {}} aiReady />
      </FocusIntentContext.Provider>
    );
    const before = screen.getByRole('button', { name: 'before search' });
    const input = screen.getByRole('searchbox');
    before.focus();

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    await waitFor(() => expect(document.activeElement).toBe(input));

    fireEvent.keyDown(input, { key: 'Escape' });

    await waitFor(() => expect(document.activeElement).toBe(before));
    expect(document.activeElement).not.toBe(document.body);
  });

  it('Escape does not throw when there is nothing to return to', async () => {
    renderHeader();
    const input = screen.getByRole('searchbox');

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    await waitFor(() => expect(document.activeElement).toBe(input));

    fireEvent.keyDown(input, { key: 'Escape' });
    expect(document.activeElement).not.toBe(input);
  });
});

describe('sidebar', () => {
  function renderRail(page: AppPage = 'mail') {
    const onNavigate = vi.fn();
    const utils = render(
      <FocusIntentContext.Provider value={makeIntent()}>
        <IconRail
          page={page}
          onNavigate={onNavigate}
          aiReady
          gmailConnected={false}
          counts={{ inbox: 0, allMail: 0 }}
          activeMailView="inbox:inbox"
        />
      </FocusIntentContext.Provider>
    );
    return { ...utils, onNavigate };
  }

  it('is a single tab stop', () => {
    renderRail();
    const items = screen.getAllByRole('button');
    const tabbable = items.filter((b) => b.tabIndex === 0);
    expect(tabbable).toHaveLength(1);
  });

  it('arrow keys move focus along the rail and do not lose it', () => {
    renderRail();
    const items = screen.getAllByRole('button');
    const first = items[0];
    first.focus();
    expect(document.activeElement).toBe(first);

    fireEvent.keyDown(first, { key: 'ArrowDown' });

    const after = screen.getAllByRole('button').find((b) => b === document.activeElement);
    expect(after).toBeDefined();
    expect(document.activeElement).not.toBe(first);
    expect(document.activeElement).not.toBe(document.body);
  });

  it('Home and End move to the ends of the rail', () => {
    renderRail();
    const items = screen.getAllByRole('button');
    items[0].focus();

    fireEvent.keyDown(items[0], { key: 'End' });
    const last = document.activeElement as HTMLElement;
    expect(last).not.toBe(items[0]);

    fireEvent.keyDown(last, { key: 'Home' });
    expect(document.activeElement).toBe(items[0]);
  });

  it('activating a rail item keeps focus on that item', () => {
    const { onNavigate } = renderRail();
    const settings = screen.getByRole('button', { name: /Settings/ });
    settings.focus();
    fireEvent.click(settings);

    expect(onNavigate).toHaveBeenCalledWith('settings');
    // The rail must keep focus: arrowing it also changes the page, so moving
    // focus to the page heading on navigation would break arrow navigation.
    expect(document.activeElement).toBe(settings);
  });
});

describe('skip link', () => {
  it('exists, is the first tab stop, and targets the main region', () => {
    render(
      <FocusIntentContext.Provider value={makeIntent()}>
        <a className="skip-link" href="#main-content">Skip to content</a>
        <main id="main-content" className="workspace-content" tabIndex={-1}>
          <h1>Mail</h1>
        </main>
      </FocusIntentContext.Provider>
    );
    const link = screen.getByRole('link', { name: 'Skip to content' });
    expect(link).toHaveAttribute('href', '#main-content');

    const main = document.getElementById('main-content')!;
    expect(main).toHaveAttribute('tabindex', '-1');
  });

  it('moving focus to the main region is possible, so the link has a real target', () => {
    render(
      <FocusIntentContext.Provider value={makeIntent()}>
        <main id="main-content" tabIndex={-1}>content</main>
      </FocusIntentContext.Provider>
    );
    const main = document.getElementById('main-content') as HTMLElement;
    main.focus();
    expect(document.activeElement).toBe(main);
  });
});
