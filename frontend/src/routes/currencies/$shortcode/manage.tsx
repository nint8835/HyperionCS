import { Alert, Button, Form, Input } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { createFileRoute } from '@tanstack/react-router';
import z from 'zod';

import { queryClient } from '@/lib/query';
import { getCurrencyQuery, useSuspenseGetCurrency } from '@/queries/integrations/v1/integrationsV1Components';
import {
  getCurrencyIntegrationsQuery,
  listIntegrationsQuery,
  useConnectIntegration,
  useDisconnectIntegration,
  useEditCurrency,
  useSuspenseGetCurrencyIntegrations,
  useSuspenseListIntegrations,
} from '@/queries/internal/internalComponents';
import type { ErrorResponseSchema, IntegrationSchema } from '@/queries/internal/internalSchemas';
import { EditCurrencySchemaZod } from '@/queries/internal/internalSchemas.zod';

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

function ManageCurrencyDetails({ shortcode }: { shortcode: string }) {
  const { data: currency } = useSuspenseGetCurrency({ pathParams: { shortcode } });
  const { mutateAsync: editCurrency, isPending, data } = useEditCurrency();

  async function handleSubmit(value: z.infer<typeof EditCurrencySchemaZod>) {
    try {
      await editCurrency({ pathParams: { shortcode }, body: value });
      await queryClient.invalidateQueries(getCurrencyQuery({ pathParams: { shortcode } }));
    } catch (error) {
      // TODO: Better, re-usable error handling
      form.setErrorMap({ onSubmit: { fields: {}, form: (error as ErrorResponseSchema).detail } });
    }
  }

  const form = useForm({
    defaultValues: {
      name: currency.name,
      singular_form: currency.singular_form,
      plural_form: currency.plural_form,
    },
    onSubmit: ({ value }) => handleSubmit(value),
    validators: { onSubmit: EditCurrencySchemaZod },
  });

  return (
    <div>
      <h2 className="text-2xl font-semibold">Manage Currency Details</h2>
      <Form
        onSubmit={(e) => {
          e.preventDefault();
          form.handleSubmit();
        }}
      >
        <form.Field
          name="name"
          children={(field) => (
            <Input
              name={field.name}
              isRequired
              label="Name"
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              validationBehavior="aria"
              errorMessage={field.state.meta.errors
                .filter((e) => e !== undefined)
                .map((e) => e.message)
                .join(', ')}
              isInvalid={!field.state.meta.isValid}
            />
          )}
        />

        <form.Field
          name="singular_form"
          children={(field) => (
            <Input
              name={field.name}
              placeholder="Coin"
              isRequired
              label="Singular Form"
              description={`The singular form of the currency to use in user-facing messages. Example: "They received 1 ${field.state.value || 'Coin'}."`}
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              validationBehavior="aria"
              errorMessage={field.state.meta.errors
                .filter((e) => e !== undefined)
                .map((e) => e.message)
                .join(', ')}
              isInvalid={!field.state.meta.isValid}
            />
          )}
        />

        <form.Field
          name="plural_form"
          children={(field) => (
            <Input
              name={field.name}
              placeholder="Coins"
              isRequired
              label="Plural Form"
              description={`The plural form of the currency to use in user-facing messages. Example: "They received 2 ${field.state.value || 'Coins'}."`}
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              validationBehavior="aria"
              errorMessage={field.state.meta.errors
                .filter((e) => e !== undefined)
                .map((e) => e.message)
                .join(', ')}
              isInvalid={!field.state.meta.isValid}
            />
          )}
        />

        <Button type="submit" isLoading={isPending}>
          Save
        </Button>

        <form.Subscribe
          selector={(state) => state.errors.filter((e) => typeof e === 'string')}
          children={(errors) => errors.length > 0 && <Alert color="danger">{errors}</Alert>}
        />

        {data && <Alert color="success">Currency updated!</Alert>}
      </Form>
    </div>
  );
}

function RouteComponent() {
  const { shortcode } = Route.useParams();

  return (
    <div className="space-y-8">
      <ManageCurrencyDetails shortcode={shortcode} />
      <ManageIntegrations shortcode={shortcode} />
    </div>
  );
}
