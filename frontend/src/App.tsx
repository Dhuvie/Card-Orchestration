import React from 'react';
import ChatContainer from './components/ChatContainer';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import ErrorBoundary from './components/ErrorBoundary';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background text-textMain font-sans flex items-center justify-center p-4">
        <ErrorBoundary>
          <ChatContainer />
        </ErrorBoundary>
      </div>
    </QueryClientProvider>
  );
}

export default App;
