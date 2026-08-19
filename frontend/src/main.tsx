import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './theme/ThemeProvider';
import { StartupGate } from './layout/StartupGate';
import { initApi } from './api/client';
import App from './App';
import './styles.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10_000,
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

// Resolve backend port/token BEFORE first paint (Tauri bootstrap).
await initApi();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <StartupGate>
          <App />
        </StartupGate>
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>
);
