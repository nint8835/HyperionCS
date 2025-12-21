import { Spinner } from '@heroui/react';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';

import { routeTree } from './routeTree.gen';

function LoadingSpinner() {
  return (
    <div className="flex h-full grow items-center justify-center">
      <Spinner size="lg" />
    </div>
  );
}

const router = createRouter({
  routeTree,
  defaultPendingComponent: LoadingSpinner,
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

const rootElement = document.getElementById('root')!;
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  );
}
