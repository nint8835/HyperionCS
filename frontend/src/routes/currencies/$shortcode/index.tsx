import { Button } from '@heroui/react';
import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';

import { Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { getCurrencyOptions } from '@/queries/integrations/v1';
import { getCurrencyPermissionsOptions } from '@/queries/internal';

export const Route = createFileRoute('/currencies/$shortcode/')({
  component: RouteComponent,
  // TODO: Error boundaries on 404s. Should raise notFound instead
  loader: ({ params: { shortcode } }) =>
    Promise.all([
      queryClient.ensureQueryData(getCurrencyOptions({ path: { shortcode } })),
      queryClient.ensureQueryData(getCurrencyPermissionsOptions({ path: { shortcode } })),
    ]),
});

function RouteComponent() {
  const { shortcode } = Route.useParams();
  const { data: currency } = useSuspenseQuery(getCurrencyOptions({ path: { shortcode } }));
  const { data: permissions } = useSuspenseQuery(getCurrencyPermissionsOptions({ path: { shortcode } }));

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
