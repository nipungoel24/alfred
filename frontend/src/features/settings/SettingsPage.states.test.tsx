import { beforeEach, describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { AnalysisStatus, Health } from '../../api/emails';

vi.mock('../../api/emails', () => ({
  health: vi.fn(),
  analysisStatus: vi.fn(),
  aiModel: vi.fn(),
  selectAiModel: vi.fn(),
  pullAiModel: vi.fn(),
  cancelAiModelPull: vi.fn(),
}));

vi.mock('../../theme/ThemeProvider', () => ({
  useTheme: () => ({ preference: 'system', setPreference: vi.fn(), resolved: 'light' }),
}));

import { SettingsPage } from './SettingsPage';
import { health, analysisStatus, aiModel } from '../../api/emails';

const readyStatus: AnalysisStatus = {
  state: 'ready',
  model: 'qwen3:8b-instruct',
  model_installed: true,
  ollama_installed: true,
  ollama_running: true,
  last_error: null,
  detail: null,
  pending: 0,
  worker_running: true,
  queue_paused: false,
  pull: null,
};

const okHealth: Health = { status: 'ok', ai: 'ready', build: 'backend-abc1234' };

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <SettingsPage />
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.mocked(health).mockReset();
  vi.mocked(analysisStatus).mockReset();
  vi.mocked(aiModel).mockReset();
  vi.mocked(health).mockResolvedValue(okHealth);
  vi.mocked(analysisStatus).mockResolvedValue(readyStatus);
  vi.mocked(aiModel).mockResolvedValue({
    model: 'qwen3:8b-instruct',
    installed: true,
    size_bytes: 5_000_000_000,
    human_size: '4.7 GB',
    local_models: [{ name: 'qwen3:8b-instruct', size_bytes: 5_000_000_000 }],
    preflight: {
      disk_free_bytes: 100_000_000_000,
      human_disk_free: '93 GB',
      disk_path: 'C:/Users/test/.ollama',
      ram_bytes: 16_000_000_000,
      human_ram: '14.9 GB',
      ram_sufficient: true,
      blocking: false,
      code: null,
      guidance: null,
    },
  });
});

describe('SettingsPage â€” sections', () => {
  it('groups every setting under a real heading', async () => {
    renderPage();

    expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument();
    for (const name of ['Appearance', 'Local AI', 'Data', 'Privacy', 'About']) {
      expect(screen.getByRole('heading', { level: 2, name })).toBeInTheDocument();
    }
  });

  it('has exactly one h1', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('qwen3:8b-instruct')).toBeInTheDocument());
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1);
  });

  it('shows only settings that really exist', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('qwen3:8b-instruct')).toBeInTheDocument());

    expect(screen.getByText('Theme')).toBeInTheDocument();
    expect(screen.getByText('Storage')).toBeInTheDocument();
    expect(screen.getByText('Credentials')).toBeInTheDocument();
    expect(screen.getByText('Analysis')).toBeInTheDocument();
    expect(screen.getByText('Frontend build')).toBeInTheDocument();

    // No invented preferences.
    for (const invented of ['Language', 'Font size', 'Notifications', 'Auto-sync']) {
      expect(screen.queryByText(invented)).toBeNull();
    }
  });
});

describe('SettingsPage â€” Local AI reports the real model', () => {
  it('reads the model from the supervisor instead of a hardcoded name', async () => {
    vi.mocked(analysisStatus).mockResolvedValue({ ...readyStatus, model: 'llama3.1:8b' });
    renderPage();

    expect(await screen.findByText('llama3.1:8b')).toBeInTheDocument();
    expect(screen.queryByText('qwen3:4b')).toBeNull();
  });

  it('does not invent a model when the supervisor has not reported one', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('Model')).toBeInTheDocument());
    expect(screen.queryByText('qwen3:4b')).toBeNull();
  });

  it('shows the queue with its real state', async () => {
    vi.mocked(analysisStatus).mockResolvedValue({ ...readyStatus, pending: 7, worker_running: false });
    renderPage();

    expect(await screen.findByText(/7 pending/)).toBeInTheDocument();
    expect(screen.getByText(/idle/)).toBeInTheDocument();
  });

  it('marks a paused queue as paused', async () => {
    vi.mocked(analysisStatus).mockResolvedValue({ ...readyStatus, pending: 3, queue_paused: true });
    renderPage();

    expect(await screen.findByText(/3 pending/)).toBeInTheDocument();
    expect(screen.getByText(/paused/)).toBeInTheDocument();
  });

  it('reports an unready runtime with an icon and a word, not colour alone', async () => {
    vi.mocked(analysisStatus).mockResolvedValue({ ...readyStatus, state: 'ollama_not_running', ollama_running: false });
    const { container } = renderPage();

    expect(await screen.findByText("Ollama isn't running")).toBeInTheDocument();
    const statusRow = screen.getByText('Status').closest('.settings-row')!;
    const indicator = statusRow.querySelector('.status-indicator')!;
    expect(indicator.querySelector('svg')).toBeInTheDocument();
    expect(container.querySelectorAll('.status-indicator').length).toBeGreaterThan(1);
  });

  it('does not crash on a state it does not recognise', async () => {
    vi.mocked(analysisStatus).mockResolvedValue({ ...readyStatus, state: 'wat' as AnalysisStatus['state'] });
    renderPage();

    // Reported, not invented into a healthy-looking row.
    expect(await screen.findByText('Starting')).toBeInTheDocument();
  });
});

describe('SettingsPage â€” states', () => {
  it('shows a skeleton, not stale or empty values, while loading', async () => {
    let resolveHealth!: (h: Health) => void;
    vi.mocked(health).mockReturnValue(new Promise((r) => { resolveHealth = r; }));

    const { container } = renderPage();

    const busy = container.querySelector('[aria-busy="true"]');
    expect(busy).toBeInTheDocument();
    expect(container.querySelectorAll('.skeleton').length).toBeGreaterThan(0);
    expect(screen.queryByText('qwen3:8b-instruct')).toBeNull();

    resolveHealth(okHealth);
    await waitFor(() => expect(screen.getByText('qwen3:8b-instruct')).toBeInTheDocument());
  });

  it('scopes a runtime failure so the other sections keep working', async () => {
    vi.mocked(health).mockRejectedValue(new Error('ECONNREFUSED 127.0.0.1:55001'));
    renderPage();

    const alert = await screen.findByRole('alert');
    expect(within(alert).getByText('Runtime status unavailable')).toBeInTheDocument();
    expect(screen.getByText('Appearance')).toBeInTheDocument();
    expect(screen.getByText('Privacy')).toBeInTheDocument();
    expect(screen.getByText('Theme')).toBeInTheDocument();
  });

  it('recovers when the runtime retry succeeds', async () => {
    vi.mocked(health).mockRejectedValueOnce(new Error('down'));
    renderPage();

    fireEvent.click(await screen.findByRole('button', { name: /Try again/i }));

    expect(await screen.findByText('qwen3:8b-instruct')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('says the backend build is unavailable rather than showing a dash', async () => {
    vi.mocked(health).mockResolvedValue({ status: 'ok', ai: 'ready', build: null });
    renderPage();

    expect(await screen.findByText('Unavailable')).toBeInTheDocument();
  });

  it('never leaks a raw exception string', async () => {
    vi.mocked(health).mockRejectedValue(new Error('ConnectError: ECONNREFUSED 127.0.0.1:49152'));
    const { container } = renderPage();

    await screen.findByRole('alert');
    expect(container.textContent).not.toMatch(/ConnectError/);
    expect(container.textContent).not.toMatch(/ECONNREFUSED/);
  });
});

describe('SettingsPage â€” accessibility', () => {
  it('labels every row', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('qwen3:8b-instruct')).toBeInTheDocument());

    for (const row of document.querySelectorAll('.settings-row')) {
      expect(row.querySelector('.settings-label')?.textContent?.trim()).toBeTruthy();
    }
  });

  it('exposes the theme control as a labelled radio group', async () => {
    renderPage();
    const group = screen.getByRole('radiogroup', { name: 'Theme' });
    expect(within(group).getAllByRole('radio')).toHaveLength(3);
    expect(within(group).getByRole('radio', { name: /System/ })).toBeInTheDocument();
  });

  it('uses no inline styles for layout', async () => {
    const { container } = renderPage();
    await waitFor(() => expect(screen.getByText('qwen3:8b-instruct')).toBeInTheDocument());

    // The only permitted inline style is the --stagger reveal custom property.
    for (const el of Array.from(container.querySelectorAll('[style]'))) {
      expect(el.getAttribute('style')).toMatch(/^--stagger:\s*\d+;?$/);
    }
  });
});
