import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/integrations/$integrationId/manage')({
  component: RouteComponent,
});

function RouteComponent() {
  const { integrationId } = Route.useParams();

  return (
    <div>
      <h1 className="text-xl font-bold">Integration Management</h1>
      <p>Integration ID: {integrationId}</p>
    </div>
  );
}
