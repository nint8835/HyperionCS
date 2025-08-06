import { createFileRoute } from '@tanstack/react-router';

import { queryClient } from '@/lib/query';
import { placeholderEndpointQuery, useSuspensePlaceholderEndpoint } from '@/queries/internal/internalComponents';

export const Route = createFileRoute('/')({
  component: RouteComponent,
  loader: () => queryClient.ensureQueryData(placeholderEndpointQuery({})),
});

function RouteComponent() {
  const { data: placeholderData } = useSuspensePlaceholderEndpoint({});

  console.log('Placeholder data:', placeholderData);

  return <div>Hello "/"!</div>;
}
