import { Button } from '@heroui/react';
import { createFileRoute } from '@tanstack/react-router';

import { Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { getCurrencyQuery, useSuspenseGetCurrency } from '@/queries/integrations/v1/integrationsV1Components';
import { getCurrencyPermissionsQuery, useSuspenseGetCurrencyPermissions } from '@/queries/internal/internalComponents';

export const Route = createFileRoute('/currencies/$shortcode/')({
  component: RouteComponent,
  // TODO: Error boundaries on 404s. Should raise notFound instead
  loader: ({ params: { shortcode } }) =>
    Promise.all([
      queryClient.ensureQueryData(getCurrencyQuery({ pathParams: { shortcode } })),
      queryClient.ensureQueryData(getCurrencyPermissionsQuery({ pathParams: { shortcode } })),
    ]),
});

function RouteComponent() {
  const { shortcode } = Route.useParams();
  const { data: currency } = useSuspenseGetCurrency({ pathParams: { shortcode } });
  const { data: permissions } = useSuspenseGetCurrencyPermissions({ pathParams: { shortcode } });

  return (
    <>
      <div>{JSON.stringify(currency)}</div>
      <div>{JSON.stringify(permissions)}</div>
      {permissions.edit && (
        <Button
          as={Link}
          to={'/currencies/$shortcode/manage'}
          //@ts-ignore - I can't figure out how to get a `Button` with an `as` of a `Link` to work properly
          params={{ shortcode }}
        >
          Manage
        </Button>
      )}
    </>
  );
}
