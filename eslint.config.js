import globals from 'globals';
// import pluginJs from '@eslint/js';
import tseslint from 'typescript-eslint';

export default [
  { files: ['**/*.{mjs,cjs,ts}'] },
  { ignores: ['.node_modules/*', 'dist'] },
  { languageOptions: { globals: globals.browser } },
  {
    rules: {
      quotes: [2, 'single', { avoidEscape: true }],
    },
  },
  // pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
];
