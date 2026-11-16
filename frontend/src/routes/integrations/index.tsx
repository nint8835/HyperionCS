import { Alert, Button } from '@heroui/react';
import { useSuspenseQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';

import { Link } from '@/components/link';
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
    <Alert color="danger">
      {'detail' in error && typeof error.detail === 'string'
        ? error.detail
        : error.message || 'Unable to load integrations. Please try again.'}
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
        <Button as={Link} to="/integrations/create">
          Create Integration
        </Button>
      </div>
      <div>
        {integrations.map((integration) => (
          <div key={integration.id}>
            <Link
              to="/integrations/$integrationId/manage"
              params={{ integrationId: integration.id }}
              color="foreground"
            >
              <span className="font-semibold">{integration.name}</span>
              {integration.description && (
                <span className="text-default-500 ml-2 text-sm">{integration.description}</span>
              )}
            </Link>
          </div>
        ))}
        {integrations.length === 0 && (
          <p className="text-default-400 w-full text-center italic">No integrations yet.</p>
        )}
      </div>
    </div>
  );
}
