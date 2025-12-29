import { Button } from '@heroui/react';
import { createFileRoute } from '@tanstack/react-router';

import { Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import { listCurrenciesQuery, useSuspenseListCurrencies } from '@/queries/integrations/v1/integrationsV1Components';

export const Route = createFileRoute('/currencies/')({
  component: RouteComponent,
  loader: () => queryClient.ensureQueryData(listCurrenciesQuery({})),
});

function RouteComponent() {
  const { data: currencies } = useSuspenseListCurrencies({});
  const user = useStore((state) => state.user);

  return (
    <div>
      <div className="flex flex-row justify-between">
        <h1 className="text-xl font-bold">Currencies</h1>
        {user && (
          <Button as={Link} to="/currencies/create">
            Create Currency
          </Button>
        )}
      </div>
      <div>
        {currencies.map((currency) => (
          <div key={currency.shortcode}>
            <Link to="/currencies/$shortcode" params={{ shortcode: currency.shortcode }} color="foreground">
              {currency.shortcode}: {currency.name}
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
