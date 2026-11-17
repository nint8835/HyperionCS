import { Alert, Button, CloseButton, FieldError, Form, Input, Label, Modal, Spinner, TextField } from '@heroui/react';
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
              <Alert.Description>Integration updated!</Alert.Description>
            </Alert.Content>
          </Alert>
        )}
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
      <Button variant="danger" onPress={handleDelete}>
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
        <Alert status="danger">
          <Alert.Indicator />
          <Alert.Content>
            <Alert.Description>{deleteError}</Alert.Description>
          </Alert.Content>
          <CloseButton onPress={() => setDeleteError(null)} />
        </Alert>
      )}

      <div className="space-y-1">
        {tokens.length === 0 ? (
          <p className="text-muted w-full text-center italic">No tokens yet.</p>
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
        onOpenChange={(open) => {
          setCreateModalOpen(open);
          form.reset();
        }}
      >
        <Modal.Backdrop>
          <Modal.Container>
            <Modal.Dialog>
              <Modal.CloseTrigger />
              <Modal.Header>
                <Modal.Heading>Create Token</Modal.Heading>
              </Modal.Header>
              <Modal.Body>
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
                      <Label>Token Name</Label>
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
              </Modal.Body>
              <Modal.Footer>
                <Button
                  onPress={() => {
                    setCreateModalOpen(false);
                    form.reset();
                  }}
                >
                  Cancel
                </Button>
                <Button isPending={isPending} onPress={() => form.handleSubmit()}>
                  {isPending && <Spinner size="sm" />}
                  Create
                </Button>
              </Modal.Footer>
            </Modal.Dialog>
          </Modal.Container>
        </Modal.Backdrop>
      </Modal>

      <Modal
        isOpen={newTokenValue !== null}
        onOpenChange={(open) => {
          if (!open) setNewTokenValue(null);
        }}
      >
        <Modal.Backdrop>
          <Modal.Container>
            <Modal.Dialog>
              <Modal.CloseTrigger />
              <Modal.Header>
                <Modal.Heading>Token Created</Modal.Heading>
              </Modal.Header>
              <Modal.Body>
                <Alert status="warning">
                  <Alert.Indicator />
                  <Alert.Content>
                    <Alert.Description>This token will not be shown again. Copy it now.</Alert.Description>
                  </Alert.Content>
                </Alert>
                <TextField className="w-full" isReadOnly>
                  <Label>Token</Label>
                  <Input value={newTokenValue ?? ''} onClick={(e) => (e.target as HTMLInputElement).select()} />
                </TextField>
              </Modal.Body>
              <Modal.Footer>
                <Button onPress={() => setNewTokenValue(null)}>Done</Button>
              </Modal.Footer>
            </Modal.Dialog>
          </Modal.Container>
        </Modal.Backdrop>
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
