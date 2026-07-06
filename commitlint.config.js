export default {
  extends: ['@commitlint/config-conventional'],
  // Dependabot titles regularly exceed header-max-length and carry no
  // RAI footer; its commits are machine-generated and not lintable.
  // Both conditions are required so a human can't skip linting by
  // pasting the trailer into an unrelated commit message.
  ignores: [
    (message) =>
      /^build\(deps(-dev)?\): bump /.test(message) &&
      message.includes('Signed-off-by: dependabot[bot] <support@github.com>'),
  ],
  rules: {
    'header-max-length': [2, 'always', 72],
    'footer-max-line-length': [2, 'always', 100],
    'rai-footer-exists': [2, 'always'],
    'rai-signed-off-by': [2, 'always'],
    'subject-case': [0],
  },
  plugins: ['commitlint-plugin-rai'],
};
