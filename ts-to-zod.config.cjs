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
];
