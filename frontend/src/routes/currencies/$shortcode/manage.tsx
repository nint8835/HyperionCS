import { Alert, Button, Description, FieldError, Form, Input, Label, Spinner, TextField } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import z from 'zod';

import { queryClient } from '@/lib/query';
import { getCurrencyOptions } from '@/queries/integrations/v1';
import {
  type ErrorResponseSchema,
  type IntegrationSchema,
  getCurrencyIntegrationsOptions,
  listIntegrationsOptions,
  useConnectIntegrationMutation,
  useDisconnectIntegrationMutation,
  useEditCurrencyMutation,
} from '@/queries/internal';
import { zEditCurrencySchema } from '@/queries/internal/zod.gen';

export const Route = createFileRoute('/currencies/$shortcode/manage')({
  component: RouteComponent,
  loader: ({ params: { shortcode } }) =>
    Promise.all([
      queryClient.ensureQueryData(getCurrencyIntegrationsOptions({ path: { shortcode } })),
      queryClient.ensureQueryData(getCurrencyOptions({ path: { shortcode } })),
      queryClient.ensureQueryData(listIntegrationsOptions()),
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
  const { mutateAsync: connectIntegration } = useConnectIntegrationMutation();
  const { mutateAsync: disconnectIntegration } = useDisconnectIntegrationMutation();

  const stateToggler = isConnected ? disconnectIntegration : connectIntegration;

  async function toggleState(integrationId: string) {
    await stateToggler({ path: { integration_id: integrationId }, body: { currency_shortcode: currencyShortcode } });
    await queryClient.invalidateQueries(getCurrencyIntegrationsOptions({ path: { shortcode: currencyShortcode } }));
  }

  return (
    <div className="flex w-full items-center justify-between">
      <div>
        <h4 className="font-semibold">{integration.name}</h4>
        <p className="text-muted text-sm">{integration.description}</p>
      </div>
      <Button onPress={() => toggleState(integration.id)} variant={isConnected ? 'danger' : 'primary'}>
        {isConnected ? 'Disconnect' : 'Connect'}
      </Button>
    </div>
  );
}

function ManageIntegrations({ shortcode }: { shortcode: string }) {
  const { data: integrations } = useSuspenseQuery(listIntegrationsOptions());
  const { data: currencyIntegrations } = useSuspenseQuery(getCurrencyIntegrationsOptions({ path: { shortcode } }));

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
          <p className="text-muted w-full text-center italic">No integrations connected.</p>
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
            <p className="text-muted w-full text-center italic">No private integrations available.</p>
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
            <p className="text-muted w-full text-center italic">No public integrations available.</p>
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
  const { data: currency } = useSuspenseQuery(getCurrencyOptions({ path: { shortcode } }));
  const { mutateAsync: editCurrency, isPending, data } = useEditCurrencyMutation();

  async function handleSubmit(value: z.infer<typeof zEditCurrencySchema>) {
    try {
      await editCurrency({ path: { shortcode }, body: value });
      await queryClient.invalidateQueries(getCurrencyOptions({ path: { shortcode } }));
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
    validators: { onSubmit: zEditCurrencySchema },
  });

  return (
    <div>
      <h2 className="text-2xl font-semibold">Manage Currency Details</h2>
      <Form
        className="flex flex-col gap-4"
        onSubmit={(e) => {
          e.preventDefault();
          form.handleSubmit();
        }}
      >
        <form.Field
          name="name"
          children={(field) => (
            <TextField
              className="w-full"
              isRequired
              isInvalid={!field.state.meta.isValid}
              validationBehavior="aria"
              name={field.name}
            >
              <Label>Name</Label>
              <Input
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
              />
              <FieldError>
                {field.state.meta.errors
                  .filter((e) => e !== undefined)
                  .map((e) => e.message)
                  .join(', ')}
              </FieldError>
            </TextField>
          )}
        />

        <form.Field
          name="singular_form"
          children={(field) => (
            <TextField
              className="w-full"
              isRequired
              isInvalid={!field.state.meta.isValid}
              validationBehavior="aria"
              name={field.name}
            >
              <Label>Singular Form</Label>
              <Input
                placeholder="Coin"
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
              />
              <Description>{`The singular form of the currency to use in user-facing messages. Example: "They received 1 ${field.state.value || 'Coin'}."`}</Description>
              <FieldError>
                {field.state.meta.errors
                  .filter((e) => e !== undefined)
                  .map((e) => e.message)
                  .join(', ')}
              </FieldError>
            </TextField>
          )}
        />

        <form.Field
          name="plural_form"
          children={(field) => (
            <TextField
              className="w-full"
              isRequired
              isInvalid={!field.state.meta.isValid}
              validationBehavior="aria"
              name={field.name}
            >
              <Label>Plural Form</Label>
              <Input
                placeholder="Coins"
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
              />
              <Description>{`The plural form of the currency to use in user-facing messages. Example: "They received 2 ${field.state.value || 'Coins'}."`}</Description>
              <FieldError>
                {field.state.meta.errors
                  .filter((e) => e !== undefined)
                  .map((e) => e.message)
                  .join(', ')}
              </FieldError>
            </TextField>
          )}
        />

        <Button type="submit" isPending={isPending}>
          {isPending && <Spinner size="sm" />}
          Save
        </Button>

        <form.Subscribe
          selector={(state) => state.errors.filter((e) => typeof e === 'string')}
          children={(errors) =>
            errors.length > 0 && (
              <Alert status="danger">
                <Alert.Indicator />
                <Alert.Content>
                  <Alert.Description>{errors}</Alert.Description>
                </Alert.Content>
              </Alert>
            )
          }
        />

        {data && (
          <Alert status="success">
            <Alert.Indicator />
            <Alert.Content>
              <Alert.Description>Currency updated!</Alert.Description>
            </Alert.Content>
          </Alert>
        )}
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
