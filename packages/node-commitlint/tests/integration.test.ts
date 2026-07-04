import lint from '@commitlint/lint';
import { RuleConfigSeverity } from '@commitlint/types';
import { describe, it, expect } from 'vitest';
import plugin from '../src/index';

// Runs the rule through the real commitlint pipeline so a broken export
// shape or rule-name mismatch fails here, not on every user's machine.
const lintMessage = (message: string) =>
  lint(
    message,
    { 'rai-footer-exists': [RuleConfigSeverity.Error, 'always'] },
    { plugins: { 'commitlint-plugin-rai': plugin } },
  );

describe('commitlint integration', () => {
  it('passes a message with a valid attribution footer', async () => {
    const result = await lintMessage(
      'feat: add a thing\n\nGenerated-by: GitHub Copilot <copilot@github.com>',
    );
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('fails a message without an attribution footer', async () => {
    const result = await lintMessage('feat: add a thing\n\nNo attribution here.');
    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0].name).toBe('rai-footer-exists');
    expect(result.errors[0].message).toContain('AI attribution footer');
  });
});
