import js from '@eslint/js';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import { globalIgnores } from 'eslint/config';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config([
  globalIgnores(['frontend/dist', 'frontend/src/queries', 'frontend/src/routeTree.gen.ts']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      'react-refresh/only-export-components': ['error', { allowConstantExport: true, extraHOCs: ['createLink'] }],
    },
  },
  {
    // TanStack's Vite plugin handles route refresh; main.tsx mounts the React root.
    files: ['frontend/src/routes/**/*.tsx', 'frontend/src/main.tsx'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
]);
