import { Alert, Button, Form, Input, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader } from '@heroui/react';
import { useForm } from '@tanstack/react-form';
import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import z from 'zod';

import { queryClient } from '@/lib/query';
import {
  type ErrorResponseSchema,
  type IntegrationTokenSchema,
  getIntegrationOptions,
  listIntegrationTokensOptions,
  useCreateIntegrationTokenMutation,
  useDeleteIntegrationTokenMutation,
  useEditIntegrationMutation,
} from '@/queries/internal';
import { zCreateIntegrationTokenSchema, zEditIntegrationSchema } from '@/queries/internal/zod.gen';

export const Route = createFileRoute('/integrations/$integrationId/manage')({
  component: RouteComponent,
  loader: ({ params: { integrationId } }) =>
    Promise.all([
      queryClient.ensureQueryData(getIntegrationOptions({ path: { integration_id: integrationId } })),
      queryClient.ensureQueryData(listIntegrationTokensOptions({ path: { integration_id: integrationId } })),
    ]),
});

function EditIntegrationDetails({ integrationId }: { integrationId: string }) {
  const { data: integration } = useSuspenseQuery(getIntegrationOptions({ path: { integration_id: integrationId } }));
  const { mutateAsync: editIntegration, isPending, data } = useEditIntegrationMutation();

  async function handleSubmit(value: z.infer<typeof zEditIntegrationSchema>) {
    try {
      await editIntegration({ path: { integration_id: integrationId }, body: value });
      await queryClient.invalidateQueries(getIntegrationOptions({ path: { integration_id: integrationId } }));
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
    } as z.infer<typeof zEditIntegrationSchema>,
    onSubmit: ({ value }) => handleSubmit(value),
    validators: { onSubmit: zEditIntegrationSchema },
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
          children={(errors) => errors.length > 0 && <Alert color="danger">{errors}</Alert>}
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
  const { mutateAsync: deleteToken } = useDeleteIntegrationTokenMutation();

  async function handleDelete() {
    try {
      await deleteToken({
        path: { integration_id: integrationId, token_id: token.id },
      });
      await queryClient.invalidateQueries(listIntegrationTokensOptions({ path: { integration_id: integrationId } }));
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
  const { data: tokens } = useSuspenseQuery(listIntegrationTokensOptions({ path: { integration_id: integrationId } }));
  const { mutateAsync: createToken, isPending } = useCreateIntegrationTokenMutation();

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newTokenValue, setNewTokenValue] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleCreateSubmit(value: z.infer<typeof zCreateIntegrationTokenSchema>) {
    try {
      const result = await createToken({
        path: { integration_id: integrationId },
        body: value,
      });
      setCreateModalOpen(false);
      form.reset();
      setNewTokenValue(result.token);
      await queryClient.invalidateQueries(listIntegrationTokensOptions({ path: { integration_id: integrationId } }));
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
    defaultValues: { name: '' } as z.infer<typeof zCreateIntegrationTokenSchema>,
    onSubmit: ({ value }) => handleCreateSubmit(value),
    validators: { onSubmit: zCreateIntegrationTokenSchema },
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
          <p className="text-default-400 w-full text-center italic">No tokens yet.</p>
        ) : (
          tokens.map((token) => (
            <TokenRow key={token.id} token={token} integrationId={integrationId} onDeleteError={setDeleteError} />
          ))
        )}
      </div>

      <Button
        onPress={() => {
          setCreateModalOpen(true);
          form.reset();
        }}
      >
        Create Token
      </Button>

      <Modal
        isOpen={createModalOpen}
        onClose={() => {
          setCreateModalOpen(false);
          form.reset();
        }}
      >
        <ModalContent>
          <ModalHeader>Create Token</ModalHeader>
          <ModalBody>
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
            <form.Subscribe
              selector={(state) => state.errors.filter((e) => typeof e === 'string')}
              children={(errors) => errors.length > 0 && <Alert color="danger">{errors}</Alert>}
            />
          </ModalBody>
          <ModalFooter>
            <Button
              onPress={() => {
                setCreateModalOpen(false);
                form.reset();
              }}
            >
              Cancel
            </Button>
            <Button isLoading={isPending} onPress={() => form.handleSubmit()}>
              Create
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      <Modal isOpen={newTokenValue !== null} onClose={() => setNewTokenValue(null)}>
        <ModalContent>
          <ModalHeader>Token Created</ModalHeader>
          <ModalBody>
            <Alert color="warning">This token will not be shown again. Copy it now.</Alert>
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
