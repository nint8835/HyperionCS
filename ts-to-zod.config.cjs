/**
 * ts-to-zod configuration.
 *
 * @type {import("ts-to-zod").TsToZodConfig}
 */
module.exports = [
  {
    name: 'internal',
    input: 'frontend/src/queries/internal/internalSchemas.ts',
    output: 'frontend/src/queries/internal/internalSchemas.zod.ts',
    getSchemaName: (name) => `${name}Zod`,
  },
  {
    name: 'integrationsV1',
    input: 'frontend/src/queries/integrations/v1/integrationsV1Schemas.ts',
    output: 'frontend/src/queries/integrations/v1/integrationsV1Schemas.zod.ts',
    getSchemaName: (name) => `${name}Zod`,
  },
];
