export default {
  extends: ['@commitlint/config-conventional'],
  // Dependabot titles regularly exceed header-max-length and carry no
  // RAI footer; its commits are machine-generated and not lintable.
  ignores: [(message) => message.includes('Signed-off-by: dependabot[bot]')],
  rules: {
    'header-max-length': [2, 'always', 72],
    'footer-max-line-length': [2, 'always', 100],
    'rai-footer-exists': [2, 'always'],
    'subject-case': [0],
  },
  plugins: ['commitlint-plugin-rai'],
};
