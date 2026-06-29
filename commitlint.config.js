export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 72],
    'footer-max-line-length': [2, 'always', 100],
    'rai-footer-exists': [2, 'always'],
    'subject-case': [0],
  },
  plugins: ['commitlint-plugin-rai'],
};
