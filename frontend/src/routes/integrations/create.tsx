import { Alert, Button, FieldError, Form, Input, Label, Spinner, TextField } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { Link, createFileRoute, useNavigate } from '@tanstack/react-router';
import z from 'zod';

import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import { type ErrorResponseSchema, listIntegrationsOptions, useCreateIntegrationMutation } from '@/queries/internal';
import { zCreateIntegrationSchema } from '@/queries/internal/zod.gen';

export const Route = createFileRoute('/integrations/create')({
  component: RouteComponent,
});

function CreateIntegrationForm() {
  const { mutateAsync: createIntegration, isPending } = useCreateIntegrationMutation();
  const navigate = useNavigate();

  async function handleSubmit(value: z.infer<typeof zCreateIntegrationSchema>) {
    try {
      await createIntegration({ body: value });
      await queryClient.invalidateQueries(listIntegrationsOptions({ query: { manageable: true } }));
      navigate({ to: '/integrations' });
    } catch (error) {
      // TODO: Better, re-usable error handling
      form.setErrorMap({ onSubmit: { fields: {}, form: (error as ErrorResponseSchema).detail } });
    }
  }

  const form = useForm({
    defaultValues: {
      name: '',
      description: '',
    } as z.infer<typeof zCreateIntegrationSchema>,
    onSubmit: ({ value }) => handleSubmit(value),
    validators: { onSubmit: zCreateIntegrationSchema },
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
        name="description"
        children={(field) => (
          <TextField
            className="w-full"
            isRequired
            isInvalid={!field.state.meta.isValid}
            validationBehavior="aria"
            name={field.name}
          >
            <Label>Description</Label>
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
        name="url"
        children={(field) => (
          <TextField
            className="w-full"
            isInvalid={!field.state.meta.isValid}
            validationBehavior="aria"
            name={field.name}
          >
            <Label>URL</Label>
            <Input
              value={field.state.value || ''}
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

      <Button type="submit" isPending={isPending}>
        {isPending && <Spinner size="sm" />}
        Create Integration
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
