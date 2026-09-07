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

// Start backend resolution immediately (before React renders).
// Under Tauri this calls the durable `await_backend_ready` command.
const initPromise = initApi();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <StartupGate initPromise={initPromise}>
          <App />
        </StartupGate>
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>
);
