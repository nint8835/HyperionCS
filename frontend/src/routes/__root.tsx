import { HeroUIProvider, Link, Navbar, NavbarBrand } from '@heroui/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { type NavigateOptions, Outlet, type ToOptions, createRootRoute, useRouter } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

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

  return (
    <HeroUIProvider
      navigate={(to, options) => router.navigate({ to, ...options })}
      useHref={(to) => router.buildLocation({ to }).href}
    >
      <QueryClientProvider client={queryClient}>
        <div className="relative flex h-screen flex-col overflow-auto">
          <Navbar>
            <NavbarBrand>
              <Link href="/" color="foreground">
                <h1 className="text-2xl font-bold">Hyperion</h1>
              </Link>
            </NavbarBrand>
          </Navbar>
          <main className="container mx-auto max-w-7xl flex-grow px-6">
            <Outlet />
          </main>
        </div>

        <ReactQueryDevtools initialIsOpen={false} />
        <TanStackRouterDevtools />
      </QueryClientProvider>
    </HeroUIProvider>
  );
}
