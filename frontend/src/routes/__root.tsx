import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Outlet, createRootRoute } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

import { Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import { getCurrentUser } from '@/queries/internal';

export const Route = createRootRoute({
  component: RootComponent,
  beforeLoad: async () => {
    if (useStore.getState().user !== undefined) {
      return;
    }

    const { data: currentUser } = await getCurrentUser({ throwOnError: true });
    useStore.getState().setUser(currentUser);
  },
});

function RootComponent() {
  const user = useStore((state) => state.user);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="relative flex h-screen flex-col overflow-auto">
        <nav
          aria-label="Main navigation"
          className="border-border bg-background/70 sticky top-0 z-40 border-b backdrop-blur-lg"
        >
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-6">
            <div>
              <Link to="/" className="text-foreground">
                <h1 className="text-2xl font-bold">Hyperion</h1>
              </Link>
            </div>
            <ul className="flex items-center gap-6">
              {user && (
                <li>
                  <Link to="/integrations" className="text-foreground">
                    Integrations
                  </Link>
                </li>
              )}
              <li>
                <Link to="/currencies" className="text-foreground">
                  Currencies
                </Link>
              </li>
              <li>
                {user ? (
                  <Link to="/auth/logout" search={{ next: window.location.href }} className="text-foreground">
                    Logout
                  </Link>
                ) : (
                  <Link to="/auth/login" search={{ next: window.location.href }} className="text-foreground">
                    Login
                  </Link>
                )}
              </li>
            </ul>
          </div>
        </nav>
        <main className="container mx-auto max-w-7xl grow px-6">
          <Outlet />
        </main>
      </div>

      <ReactQueryDevtools initialIsOpen={false} />
      <TanStackRouterDevtools />
    </QueryClientProvider>
  );
}
