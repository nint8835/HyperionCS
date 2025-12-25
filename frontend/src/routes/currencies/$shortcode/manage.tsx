import { Button } from '@heroui/react';
import { createFileRoute } from '@tanstack/react-router';

import { queryClient } from '@/lib/query';
import { getCurrencyQuery } from '@/queries/integrations/v1/integrationsV1Components';
import {
  getCurrencyIntegrationsQuery,
  listIntegrationsQuery,
  useConnectIntegration,
  useDisconnectIntegration,
  useSuspenseGetCurrencyIntegrations,
  useSuspenseListIntegrations,
} from '@/queries/internal/internalComponents';
import type { IntegrationSchema } from '@/queries/internal/internalSchemas';

export const Route = createFileRoute('/currencies/$shortcode/manage')({
  component: RouteComponent,
  loader: ({ params: { shortcode } }) =>
    Promise.all([
      queryClient.ensureQueryData(getCurrencyIntegrationsQuery({ pathParams: { shortcode } })),
      queryClient.ensureQueryData(getCurrencyQuery({ pathParams: { shortcode } })),
      queryClient.ensureQueryData(listIntegrationsQuery({})),
    ]),
});

function IntegrationDisplay({
  integration,
  isConnected = false,
  currencyShortcode,
}: {
  integration: IntegrationSchema;
  isConnected?: boolean;
  currencyShortcode: string;
}) {
  const { mutateAsync: connectIntegration } = useConnectIntegration();
  const { mutateAsync: disconnectIntegration } = useDisconnectIntegration();

  const stateToggler = isConnected ? disconnectIntegration : connectIntegration;

  async function toggleState(integrationId: string) {
    await stateToggler({ pathParams: { integrationId }, body: { currency_shortcode: currencyShortcode } });
    await queryClient.invalidateQueries(getCurrencyIntegrationsQuery({ pathParams: { shortcode: currencyShortcode } }));
  }

  return (
    <div className="flex w-full items-center justify-between">
      <div>
        <h4 className="font-semibold">{integration.name}</h4>
        <p className="text-default-500 text-sm">{integration.description}</p>
      </div>
      <Button onPress={() => toggleState(integration.id)} color={isConnected ? 'danger' : 'primary'}>
        {isConnected ? 'Disconnect' : 'Connect'}
      </Button>
    </div>
  );
}

function ManageIntegrations({ shortcode }: { shortcode: string }) {
  const { data: integrations } = useSuspenseListIntegrations({});
  const { data: currencyIntegrations } = useSuspenseGetCurrencyIntegrations({ pathParams: { shortcode } });

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
          <p className="text-default-400 w-full text-center italic">No integrations connected.</p>
        ) : (
          <div className="space-y-1">
            {currencyIntegrations.map((integration) => (
              <IntegrationDisplay
                key={integration.id}
                integration={integration}
                isConnected
                currencyShortcode={shortcode}
              />
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 className="text-xl font-semibold">Available Integrations</h3>

        <div>
          <h4 className="text-lg font-semibold">Private Integrations</h4>
          {availablePrivateIntegrations.length === 0 ? (
            <p className="text-default-400 w-full text-center italic">No private integrations available.</p>
          ) : (
            <div className="space-y-1">
              {availablePrivateIntegrations.map((integration) => (
                <IntegrationDisplay key={integration.id} integration={integration} currencyShortcode={shortcode} />
              ))}
            </div>
          )}
        </div>

        <div>
          <h4 className="text-lg font-semibold">Public Integrations</h4>
          {availablePublicIntegrations.length === 0 ? (
            <p className="text-default-400 w-full text-center italic">No public integrations available.</p>
          ) : (
            <div className="space-y-1">
              {availablePublicIntegrations.map((integration) => (
                <IntegrationDisplay key={integration.id} integration={integration} currencyShortcode={shortcode} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function RouteComponent() {
  const { shortcode } = Route.useParams();

  return (
    <div>
      <ManageIntegrations shortcode={shortcode} />
    </div>
  );
}
