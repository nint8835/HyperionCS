import { Alert, Button, Form, Input } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { Link, createFileRoute } from '@tanstack/react-router';
import z from 'zod';

import { useStore } from '@/lib/state';
import { useCreateCurrency } from '@/queries/internal/internalComponents';
import { ErrorResponseSchema } from '@/queries/internal/internalSchemas';
import { CreateCurrencySchemaZod } from '@/queries/internal/internalSchemas.zod';

export const Route = createFileRoute('/currencies/create')({
  component: RouteComponent,
});

function CreateCurrencyForm() {
  const { mutateAsync: createCurrency, isPending, data } = useCreateCurrency();

  async function handleSubmit(value: z.infer<typeof CreateCurrencySchemaZod>) {
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
    validators: { onSubmit: CreateCurrencySchemaZod },
  });

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field
        name="shortcode"
        children={(field) => (
          <Input
            name={field.name}
            isRequired
            label="Shortcode"
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
            isRequired
            label="Singular Form"
            description={`The singular form of the currency to use in user-facing messages. Example: "They received 1 ${field.state.value}."`}
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
            isRequired
            label="Plural Form"
            description={`The plural form of the currency to use in user-facing messages. Example: "They received 2 ${field.state.value}."`}
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
        Create Currency
      </Button>

      {/* TODO: Validation errors cause error boundary */}
      <form.Subscribe
        selector={(state) => state.errors}
        children={(errors) => errors.length > 0 && <Alert color="danger">{errors as unknown as string}</Alert>}
      />

      {data && <Alert color="success">Currency created!</Alert>}
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
          className="hover:text-primary underline transition-colors"
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
