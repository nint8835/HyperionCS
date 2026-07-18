import { heyApiPlugin } from '@hey-api/vite-plugin';
import tailwindcss from '@tailwindcss/vite';
import { tanstackRouter } from '@tanstack/router-plugin/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  root: 'frontend',
  plugins: [
    heyApiPlugin({
      vite: {
        apply: 'serve',
      },
      config: [
        {
          input: 'http://localhost:8000/openapi.json',
          output: {
            path: 'frontend/src/queries/internal',
            postProcess: ['prettier'],
          },
          plugins: [
            {
              name: '@hey-api/client-fetch',
              baseUrl: false,
            },
            '@hey-api/typescript',
            'zod',
            {
              name: '@hey-api/sdk',
              validator: true,
            },
            {
              name: '@tanstack/react-query',
              includeInEntry: true,
              useQuery: true,
              useMutation: true,
              mutationKeys: true,
            },
          ],
        },
        {
          input: 'http://localhost:8000/api/v1/openapi.json',
          output: {
            path: 'frontend/src/queries/integrations/v1',
            postProcess: ['prettier'],
          },
          plugins: [
            {
              name: '@hey-api/client-fetch',
              baseUrl: false,
            },
            '@hey-api/typescript',
            'zod',
            {
              name: '@hey-api/sdk',
              validator: true,
            },
            {
              name: '@tanstack/react-query',
              includeInEntry: true,
              useQuery: true,
              useMutation: true,
              mutationKeys: true,
            },
          ],
        },
      ],
    }),
    tanstackRouter({
      target: 'react',
      autoCodeSplitting: true,
      routesDirectory: './src/routes',
      generatedRouteTree: './src/routeTree.gen.ts',
    }),
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/auth': {
        target: 'http://127.0.0.1:8000',
      },
      '/docs': {
        target: 'http://127.0.0.1:8000',
      },
      '/openapi.json': {
        target: 'http://127.0.0.1:8000',
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
});
