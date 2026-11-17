import { Alert, Button, Description, FieldError, Form, Input, Label, Spinner, TextField } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { Link, createFileRoute } from '@tanstack/react-router';
import z from 'zod';

import { useStore } from '@/lib/state';
import { type ErrorResponseSchema, useCreateCurrencyMutation } from '@/queries/internal';
import { zCreateCurrencySchema } from '@/queries/internal/zod.gen';

export const Route = createFileRoute('/currencies/create')({
  component: RouteComponent,
});

function CreateCurrencyForm() {
  const { mutateAsync: createCurrency, isPending, data } = useCreateCurrencyMutation();

  async function handleSubmit(value: z.infer<typeof zCreateCurrencySchema>) {
    try {
      await createCurrency({ body: value });
    } catch (error) {
      // TODO: Better, re-usable error handling
      form.setErrorMap({ onSubmit: { fields: {}, form: (error as ErrorResponseSchema).detail } });
    }
  }

  const form = useForm({
    defaultValues: {
      shortcode: '',
      name: '',
      singular_form: '',
      plural_form: '',
    },
    onSubmit: ({ value }) => handleSubmit(value),
    validators: { onSubmit: zCreateCurrencySchema },
  });

  return (
    <Form
      className="flex flex-col gap-4"
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field
        name="shortcode"
        children={(field) => (
          <TextField
            className="w-full"
            isRequired
            isInvalid={!field.state.meta.isValid}
            validationBehavior="aria"
            name={field.name}
          >
            <Label>Shortcode</Label>
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
        Create Currency
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
            <Alert.Description>Currency created!</Alert.Description>
          </Alert.Content>
        </Alert>
      )}
    </Form>
  );
}

function RouteComponent() {
  const user = useStore((store) => store.user);

  if (!user) {
    return (
      <div>
        Please{' '}
        <Link
          className="hover:text-accent underline transition-colors"
          to="/auth/login"
          search={{ next: '/currencies/create' }}
        >
          log in
        </Link>{' '}
        to create a currency.
      </div>
    );
  }

  return <CreateCurrencyForm />;
}
