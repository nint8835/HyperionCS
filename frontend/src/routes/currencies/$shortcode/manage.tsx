import { Button, Divider } from '@heroui/react';
import { createFileRoute } from '@tanstack/react-router';

import { queryClient } from '@/lib/query';
import { getCurrencyQuery, useSuspenseGetCurrency } from '@/queries/integrations/v1/integrationsV1Components';
import {
  getCurrencyIntegrationsQuery,
  listIntegrationsQuery,
  useConnectIntegration,
  useDisconnectIntegration,
  useSuspenseGetCurrencyIntegrations,
  useSuspenseListIntegrations,
} from '@/queries/internal/internalComponents';

export const Route = createFileRoute('/currencies/$shortcode/manage')({
  component: RouteComponent,
  loader: ({ params: { shortcode } }) =>
    Promise.all([
      queryClient.ensureQueryData(getCurrencyIntegrationsQuery({ pathParams: { shortcode } })),
      queryClient.ensureQueryData(getCurrencyQuery({ pathParams: { shortcode } })),
      queryClient.ensureQueryData(listIntegrationsQuery({})),
    ]),
});

function ManageIntegrations({ shortcode }: { shortcode: string }) {
  const { data: integrations } = useSuspenseListIntegrations({});
  const { data: currencyIntegrations } = useSuspenseGetCurrencyIntegrations({ pathParams: { shortcode } });

  const { mutateAsync: connectIntegration } = useConnectIntegration();
  const { mutateAsync: disconnectIntegration } = useDisconnectIntegration();

  async function doConnect(integrationId: string) {
    await connectIntegration({ pathParams: { integrationId }, body: { currency_shortcode: shortcode } });
    queryClient.invalidateQueries(getCurrencyIntegrationsQuery({ pathParams: { shortcode } }));
  }

  async function doDisconnect(integrationId: string) {
    await disconnectIntegration({ pathParams: { integrationId }, body: { currency_shortcode: shortcode } });
    queryClient.invalidateQueries(getCurrencyIntegrationsQuery({ pathParams: { shortcode } }));
  }

  const availablePrivateIntegrations = integrations.filter(
    (integration) => integration.private && !currencyIntegrations.some((ci) => ci.id === integration.id),
  );
  const availablePublicIntegrations = integrations.filter(
    (integration) => !integration.private && !currencyIntegrations.some((ci) => ci.id === integration.id),
  );

  return (
    <div className="space-y-2">
      <h2 className="text-2xl font-semibold">Manage Integrations</h2>

      <div>
        <h3 className="text-xl font-semibold">Connected Integrations</h3>
        {currencyIntegrations.length === 0 ? (
          <p>No integrations connected.</p>
        ) : (
          <ul>
            {currencyIntegrations.map((integration) => (
              <div key={integration.id}>
                {integration.name}{' '}
                <Button color="danger" onPress={() => doDisconnect(integration.id)}>
                  Disconnect
                </Button>
              </div>
            ))}
          </ul>
        )}
      </div>

      <Divider />

      <div>
        <h3 className="text-xl font-semibold">Available Integrations</h3>

        <div>
          <h4 className="text-lg font-semibold">Private Integrations</h4>
          {availablePrivateIntegrations.length === 0 ? (
            <p>No private integrations available.</p>
          ) : (
            <ul>
              {availablePrivateIntegrations.map((integration) => (
                <div key={integration.id}>
                  {integration.name} <Button onPress={() => doConnect(integration.id)}>Connect</Button>
                </div>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h4 className="text-lg font-semibold">Public Integrations</h4>
          {availablePublicIntegrations.length === 0 ? (
            <p>No public integrations available.</p>
          ) : (
            <ul>
              {availablePublicIntegrations.map((integration) => (
                <div key={integration.id}>
                  {integration.name} <Button onPress={() => doConnect(integration.id)}>Connect</Button>
                </div>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function RouteComponent() {
  const { shortcode } = Route.useParams();
  const { data: currency } = useSuspenseGetCurrency({ pathParams: { shortcode } });

  return (
    <div>
      <ManageIntegrations shortcode={shortcode} />
    </div>
  );
}
