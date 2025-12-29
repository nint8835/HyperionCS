import { HeroUIProvider, Navbar, NavbarBrand, NavbarContent, NavbarItem } from '@heroui/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { type NavigateOptions, Outlet, type ToOptions, createRootRoute, useRouter } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

import { Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import { fetchGetCurrentUser } from '@/queries/internal/internalComponents';

export const Route = createRootRoute({
  component: RootComponent,
  beforeLoad: async () => {
    if (useStore.getState().user !== undefined) {
      return;
    }

    const currentUser = await fetchGetCurrentUser({});
    useStore.getState().setUser(currentUser);
  },
});

declare module '@react-types/shared' {
  interface RouterConfig {
    href: ToOptions['to'];
    routerOptions: Omit<NavigateOptions, keyof ToOptions>;
  }
}

function RootComponent() {
  const router = useRouter();
  const user = useStore((state) => state.user);

  return (
    <HeroUIProvider
      navigate={(to, options) => router.navigate({ to, ...options })}
      useHref={(to) => router.buildLocation({ to }).href}
    >
      <QueryClientProvider client={queryClient}>
        <div className="relative flex h-screen flex-col overflow-auto">
          <Navbar>
            <NavbarBrand>
              <Link to="/" color="foreground">
                <h1 className="text-2xl font-bold">Hyperion</h1>
              </Link>
            </NavbarBrand>
            <NavbarContent justify="end">
              <NavbarItem>
                <Link to="/currencies" color="foreground">
                  Currencies
                </Link>
              </NavbarItem>
              <NavbarItem>
                {user ? (
                  <Link to="/auth/logout" search={{ next: window.location.href }} color="foreground">
                    Logout
                  </Link>
                ) : (
                  <Link to="/auth/login" search={{ next: window.location.href }} color="foreground">
                    Login
                  </Link>
                )}
              </NavbarItem>
            </NavbarContent>
          </Navbar>
          <main className="container mx-auto max-w-7xl grow px-6">
            <Outlet />
          </main>
        </div>

        <ReactQueryDevtools initialIsOpen={false} />
        <TanStackRouterDevtools />
      </QueryClientProvider>
    </HeroUIProvider>
  );
}
