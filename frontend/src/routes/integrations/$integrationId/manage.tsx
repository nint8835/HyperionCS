import { Alert, Button, Form, Input, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import z from 'zod';

import { queryClient } from '@/lib/query';
import {
  getIntegrationQuery,
  listIntegrationTokensQuery,
  useCreateIntegrationToken,
  useDeleteIntegrationToken,
  useEditIntegration,
  useSuspenseGetIntegration,
  useSuspenseListIntegrationTokens,
} from '@/queries/internal/internalComponents';
import type {
  ErrorResponseSchema,
  IntegrationTokenSchema,
} from '@/queries/internal/internalSchemas';
import {
  CreateIntegrationTokenSchemaZod,
  EditIntegrationSchemaZod,
} from '@/queries/internal/internalSchemas.zod';

export const Route = createFileRoute('/integrations/$integrationId/manage')({
  component: RouteComponent,
  loader: ({ params: { integrationId } }) =>
    Promise.all([
      queryClient.ensureQueryData(
        getIntegrationQuery({ pathParams: { integrationId } }),
      ),
      queryClient.ensureQueryData(
        listIntegrationTokensQuery({ pathParams: { integrationId } }),
      ),
    ]),
});

function EditIntegrationDetails({ integrationId }: { integrationId: string }) {
  const { data: integration } = useSuspenseGetIntegration({
    pathParams: { integrationId },
  });
  const { mutateAsync: editIntegration, isPending, data } = useEditIntegration();

  async function handleSubmit(
    value: z.infer<typeof EditIntegrationSchemaZod>,
  ) {
    try {
      await editIntegration({ pathParams: { integrationId }, body: value });
      await queryClient.invalidateQueries(
        getIntegrationQuery({ pathParams: { integrationId } }),
      );
    } catch (error) {
      form.setErrorMap({
        onSubmit: {
          fields: {},
          form: (error as ErrorResponseSchema).detail,
        },
      });
    }
  }

  const form = useForm({
    defaultValues: {
      name: integration.name,
      description: integration.description,
      url: integration.url ?? '',
    } as z.infer<typeof EditIntegrationSchemaZod>,
    onSubmit: ({ value }) => handleSubmit(value),
    validators: { onSubmit: EditIntegrationSchemaZod },
  });

  return (
    <div>
      <h2 className="text-2xl font-semibold">Edit Integration Details</h2>
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
          Save
        </Button>
        <form.Subscribe
          selector={(state) => state.errors.filter((e) => typeof e === 'string')}
          children={(errors) =>
            errors.length > 0 && <Alert color="danger">{errors}</Alert>
          }
        />
        {data && <Alert color="success">Integration updated!</Alert>}
      </Form>
    </div>
  );
}

function TokenRow({
  token,
  integrationId,
  onDeleteError,
}: {
  token: IntegrationTokenSchema;
  integrationId: string;
  onDeleteError: (message: string) => void;
}) {
  const { mutateAsync: deleteToken } = useDeleteIntegrationToken();

  async function handleDelete() {
    try {
      await deleteToken({
        pathParams: { integrationId, tokenId: token.id },
      });
      await queryClient.invalidateQueries(
        listIntegrationTokensQuery({ pathParams: { integrationId } }),
      );
    } catch (error) {
      onDeleteError((error as ErrorResponseSchema).detail);
    }
  }

  return (
    <div className="flex w-full items-center justify-between">
      <span>{token.name}</span>
      <Button color="danger" onPress={handleDelete}>
        Delete
      </Button>
    </div>
  );
}

function ManageTokens({ integrationId }: { integrationId: string }) {
  const { data: tokens } = useSuspenseListIntegrationTokens({
    pathParams: { integrationId },
  });
  const { mutateAsync: createToken, isPending } = useCreateIntegrationToken();

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTokenValue, setNewTokenValue] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleCreateSubmit(
    value: z.infer<typeof CreateIntegrationTokenSchemaZod>,
  ) {
    try {
      const result = await createToken({
        pathParams: { integrationId },
        body: value,
      });
      setNewTokenValue(result.token);
      setShowCreateForm(false);
      form.reset();
      await queryClient.invalidateQueries(
        listIntegrationTokensQuery({ pathParams: { integrationId } }),
      );
    } catch (error) {
      form.setErrorMap({
        onSubmit: {
          fields: {},
          form: (error as ErrorResponseSchema).detail,
        },
      });
    }
  }

  const form = useForm({
    defaultValues: { name: '' } as z.infer<
      typeof CreateIntegrationTokenSchemaZod
    >,
    onSubmit: ({ value }) => handleCreateSubmit(value),
    validators: { onSubmit: CreateIntegrationTokenSchemaZod },
  });

  return (
    <div className="space-y-2">
      <h2 className="text-2xl font-semibold">Manage Tokens</h2>

      {deleteError && (
        <Alert color="danger" onClose={() => setDeleteError(null)}>
          {deleteError}
        </Alert>
      )}

      <div className="space-y-1">
        {tokens.length === 0 ? (
          <p className="text-default-400 w-full text-center italic">
            No tokens yet.
          </p>
        ) : (
          tokens.map((token) => (
            <TokenRow
              key={token.id}
              token={token}
              integrationId={integrationId}
              onDeleteError={setDeleteError}
            />
          ))
        )}
      </div>

      <Button
        onPress={() => {
          setShowCreateForm((v) => !v);
          form.reset();
        }}
      >
        Create Token
      </Button>

      {showCreateForm && (
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
                label="Token Name"
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
            Create
          </Button>
          <form.Subscribe
            selector={(state) =>
              state.errors.filter((e) => typeof e === 'string')
            }
            children={(errors) =>
              errors.length > 0 && <Alert color="danger">{errors}</Alert>
            }
          />
        </Form>
      )}

      <Modal
        isOpen={newTokenValue !== null}
        onClose={() => setNewTokenValue(null)}
      >
        <ModalContent>
          <ModalHeader>Token Created</ModalHeader>
          <ModalBody>
            <Alert color="warning">
              This token will not be shown again. Copy it now.
            </Alert>
            <Input
              isReadOnly
              label="Token"
              value={newTokenValue ?? ''}
              onClick={(e) => (e.target as HTMLInputElement).select()}
            />
          </ModalBody>
          <ModalFooter>
            <Button onPress={() => setNewTokenValue(null)}>Done</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
}

function RouteComponent() {
  const { integrationId } = Route.useParams();

  return (
    <div className="space-y-8">
      <EditIntegrationDetails integrationId={integrationId} />
      <ManageTokens integrationId={integrationId} />
    </div>
  );
}
