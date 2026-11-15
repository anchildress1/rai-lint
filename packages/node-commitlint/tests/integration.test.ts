import lint from '@commitlint/lint';
import { RuleConfigSeverity, type UserConfig } from '@commitlint/types';
import { describe, it, expect } from 'vitest';
import repositoryConfig from '../../../commitlint.config.js';
import plugin from '../src/index';

// Runs the rules through the real commitlint pipeline so a broken export
// shape or rule-name mismatch fails here, not on every user's machine.
const lintMessage = (message: string) =>
  lint(
    message,
    {
      'rai-footer-exists': [RuleConfigSeverity.Error, 'always'],
      'rai-signed-off-by': [RuleConfigSeverity.Error, 'always'],
    },
    { plugins: { 'commitlint-plugin-rai': plugin } },
  );

describe('commitlint integration', () => {
  it('passes a message with attribution and sign-off footers', async () => {
    const result = await lintMessage(
      'feat: add a thing\n\nGenerated-by: GitHub Copilot <copilot@github.com>\nSigned-off-by: Jane Doe <jane@example.com>',
    );
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it.each([
    [
      'without an attribution footer',
      'feat: add a thing\n\nSigned-off-by: Jane Doe <jane@example.com>',
      'rai-footer-exists',
      'AI attribution footer',
    ],
    [
      'with several attribution footers',
      'feat: add a thing\n\nGenerated-by: GitHub Copilot <copilot@github.com>\nAssisted-by: Claude <noreply@anthropic.com>\nSigned-off-by: Jane Doe <jane@example.com>',
      'rai-footer-exists',
      'found several',
    ],
    [
      'without a sign-off footer',
      'feat: add a thing\n\nGenerated-by: GitHub Copilot <copilot@github.com>',
      'rai-signed-off-by',
      'Signed-off-by',
    ],
  ])('fails a message %s with exactly one error', async (_label, message, rule, text) => {
    const result = await lintMessage(message);
    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0].name).toBe(rule);
    expect(result.errors[0].message).toContain(text);
  });

  it('passes one attribution footer alongside unrelated trailers', async () => {
    const result = await lintMessage(
      'feat: add a thing\n\nReviewed-by: Bob <bob@example.com>\nGenerated-by: GitHub Copilot <copilot@github.com>\nSigned-off-by: Jane Doe <jane@example.com>',
    );
    expect(result.valid).toBe(true);
  });

  it('rejects a forged Dependabot message under the repository policy', async () => {
    const result = await lint(
      'build(deps): bump example\n\nSigned-off-by: dependabot[bot] <support@github.com>',
      repositoryConfig.rules,
      {
        ignores: (repositoryConfig as UserConfig).ignores,
        plugins: { 'commitlint-plugin-rai': plugin },
      },
    );
    expect(result.valid).toBe(false);
    expect(result.errors.some((error) => error.name === 'rai-footer-exists')).toBe(true);
  });
});
