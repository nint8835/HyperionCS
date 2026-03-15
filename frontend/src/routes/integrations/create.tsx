import { Alert, Button, Form, Input } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { Link, createFileRoute, useNavigate } from '@tanstack/react-router';
import z from 'zod';

import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import {
  listIntegrationsQuery,
  useCreateIntegration,
} from '@/queries/internal/internalComponents';
import { ErrorResponseSchema } from '@/queries/internal/internalSchemas';
import { CreateIntegrationSchemaZod } from '@/queries/internal/internalSchemas.zod';

export const Route = createFileRoute('/integrations/create')({
  component: RouteComponent,
});

function CreateIntegrationForm() {
  const { mutateAsync: createIntegration, isPending } = useCreateIntegration();
  const navigate = useNavigate();

  async function handleSubmit(value: z.infer<typeof CreateIntegrationSchemaZod>) {
    try {
      await createIntegration({ body: value });
      await queryClient.invalidateQueries(
        listIntegrationsQuery({ queryParams: { manageable: true } }),
      );
      navigate({ to: '/integrations' });
    } catch (error) {
      form.setErrorMap({ onSubmit: { fields: {}, form: (error as ErrorResponseSchema).detail } });
    }
  }

  const form = useForm({
    defaultValues: {
      name: '',
      description: '',
    } as z.infer<typeof CreateIntegrationSchemaZod>,
    onSubmit: ({ value }) => handleSubmit(value),
    validators: { onSubmit: CreateIntegrationSchemaZod },
  });

  return (
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
        name="description"
        children={(field) => (
          <Input
            name={field.name}
            isRequired
            label="Description"
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
        name="url"
        children={(field) => (
          <Input
            name={field.name}
            label="URL"
            value={field.state.value || ''}
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
        Create Integration
      </Button>

      <form.Subscribe
        selector={(state) => state.errors.filter((e) => typeof e === 'string')}
        children={(errors) => errors.length > 0 && <Alert color="danger">{errors}</Alert>}
      />
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
          search={{ next: '/integrations/create' }}
        >
          log in
        </Link>{' '}
        to create an integration.
      </div>
    );
  }

  return <CreateIntegrationForm />;
}
