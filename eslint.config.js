import eslint from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import prettierConfig from 'eslint-config-prettier';
import commentsPlugin from '@eslint-community/eslint-plugin-eslint-comments';
import globals from 'globals';

export default [
  eslint.configs.recommended,
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
      },
      globals: {
        ...globals.node,
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
      'eslint-comments': commentsPlugin,
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      'eslint-comments/no-unused-disable': 'error',
      'no-undef': 'off',
    },
  },
  prettierConfig,
];
