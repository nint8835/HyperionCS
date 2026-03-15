import { Button } from '@heroui/react';
import { createFileRoute } from '@tanstack/react-router';

import { Link } from '@/components/link';
import { queryClient } from '@/lib/query';
import { useStore } from '@/lib/state';
import {
  listIntegrationsQuery,
  useSuspenseListIntegrations,
} from '@/queries/internal/internalComponents';

export const Route = createFileRoute('/integrations/')({
  component: RouteComponent,
  loader: () =>
    queryClient.ensureQueryData(
      listIntegrationsQuery({ queryParams: { manageable: true } }),
    ),
});

function RouteComponent() {
  const { data: integrations } = useSuspenseListIntegrations({
    queryParams: { manageable: true },
  });
  const user = useStore((state) => state.user);

  return (
    <div>
      <div className="flex flex-row justify-between">
        <h1 className="text-xl font-bold">Integrations</h1>
        {user && (
          <Button as={Link} to="/integrations/create">
            Create Integration
          </Button>
        )}
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
                <span className="text-default-500 ml-2 text-sm">
                  {integration.description}
                </span>
              )}
            </Link>
          </div>
        ))}
        {integrations.length === 0 && (
          <p className="text-default-400 w-full text-center italic">
            No integrations yet.
          </p>
        )}
      </div>
    </div>
  );
}
