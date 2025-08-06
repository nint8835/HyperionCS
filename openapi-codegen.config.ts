import { defineConfig } from '@openapi-codegen/cli';
import { generateReactQueryComponents, generateSchemaTypes } from '@openapi-codegen/typescript';

export default defineConfig({
  internal: {
    from: {
      source: 'url',
      url: 'http://localhost:8000/openapi.json',
    },
    outputDir: 'frontend/src/queries/internal',
    to: async (context) => {
      const filenamePrefix = 'internal';
      const { schemasFiles } = await generateSchemaTypes(context, {
        filenamePrefix,
      });
      await generateReactQueryComponents(context, {
        filenamePrefix,
        schemasFiles,
      });
    },
  },
});
