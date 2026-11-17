import { Alert } from '@heroui/react';
import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';

import { ButtonLink, Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import { listIntegrationsOptions } from '@/queries/internal';

export const Route = createFileRoute('/integrations/')({
  component: RouteComponent,
  loader: () => {
    if (!useStore.getState().user) {
      return;
    }
    return queryClient.ensureQueryData(listIntegrationsOptions({ query: { manageable: true } }));
  },
  errorComponent: ({ error }) => (
    <Alert status="danger">
      <Alert.Indicator />
      <Alert.Content>
        <Alert.Description>
          {typeof error === 'object' && error !== null && 'detail' in error && typeof error.detail === 'string'
            ? error.detail
            : error instanceof Error
              ? error.message
              : 'Unable to load integrations. Please try again.'}
        </Alert.Description>
      </Alert.Content>
    </Alert>
  ),
});

function RouteComponent() {
  const user = useStore((state) => state.user);

  if (!user) {
    return (
      <div>
        Please{' '}
        <Link to="/auth/login" search={{ next: '/integrations' }}>
          log in
        </Link>{' '}
        to view your integrations.
      </div>
    );
  }

  return <IntegrationsList />;
}

function IntegrationsList() {
  const { data: integrations } = useSuspenseQuery(listIntegrationsOptions({ query: { manageable: true } }));

  return (
    <div>
      <div className="flex flex-row justify-between">
        <h1 className="text-xl font-bold">Integrations</h1>
        <ButtonLink to="/integrations/create">Create Integration</ButtonLink>
      </div>
      <div>
        {integrations.map((integration) => (
          <div key={integration.id}>
            <Link
              to="/integrations/$integrationId/manage"
              params={{ integrationId: integration.id }}
              className="text-foreground"
            >
              <span className="font-semibold">{integration.name}</span>
              {integration.description && <span className="text-muted ml-2 text-sm">{integration.description}</span>}
            </Link>
          </div>
        ))}
        {integrations.length === 0 && <p className="text-muted w-full text-center italic">No integrations yet.</p>}
      </div>
    </div>
  );
}
