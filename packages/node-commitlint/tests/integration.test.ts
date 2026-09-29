import lint from '@commitlint/lint';
import { RuleConfigSeverity } from '@commitlint/types';
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

  it('fails a message without an attribution footer', async () => {
    const result = await lintMessage(
      'feat: add a thing\n\nSigned-off-by: Jane Doe <jane@example.com>',
    );
    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0].name).toBe('rai-footer-exists');
    expect(result.errors[0].message).toContain('AI attribution footer');
  });

  it('fails a message without a sign-off footer', async () => {
    const result = await lintMessage(
      'feat: add a thing\n\nGenerated-by: GitHub Copilot <copilot@github.com>',
    );
    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0].name).toBe('rai-signed-off-by');
    expect(result.errors[0].message).toContain('Signed-off-by');
  });

  it('rejects both footers when they appear only after Git scissors', async () => {
    const result = await lintMessage(
      'feat: add a thing\n\n# ------------------------ >8 ------------------------\nGenerated-by: AI <ai@example.com>\nSigned-off-by: Jane Doe <jane@example.com>',
    );
    expect(result.valid).toBe(false);
    expect(result.errors.map((error) => error.name)).toEqual([
      'rai-footer-exists',
      'rai-signed-off-by',
    ]);
  });

  it('rejects a forged Dependabot message under the repository policy', async () => {
    const result = await lint(
      'build(deps): bump example\n\nSigned-off-by: dependabot[bot] <support@github.com>',
      repositoryConfig.rules,
      {
        ignores: repositoryConfig.ignores,
        plugins: { 'commitlint-plugin-rai': plugin },
      },
    );
    expect(result.valid).toBe(false);
    expect(result.errors.some((error) => error.name === 'rai-footer-exists')).toBe(true);
  });

});
