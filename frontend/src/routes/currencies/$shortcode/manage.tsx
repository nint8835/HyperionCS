import { createFileRoute } from '@tanstack/react-router';

import { queryClient } from '@/lib/query';
import { getCurrencyQuery, useSuspenseGetCurrency } from '@/queries/integrations/v1/integrationsV1Components';
import { listIntegrationsQuery, useSuspenseListIntegrations } from '@/queries/internal/internalComponents';

export const Route = createFileRoute('/currencies/$shortcode/manage')({
  component: RouteComponent,
  loader: ({ params: { shortcode } }) =>
    Promise.all([
      queryClient.ensureQueryData(getCurrencyQuery({ pathParams: { shortcode } })),
      queryClient.ensureQueryData(listIntegrationsQuery({})),
    ]),
});

function RouteComponent() {
  const { shortcode } = Route.useParams();
  const { data: currency } = useSuspenseGetCurrency({ pathParams: { shortcode } });
  const { data: integrations } = useSuspenseListIntegrations({});

  return <div>{JSON.stringify(integrations)}</div>;
}
