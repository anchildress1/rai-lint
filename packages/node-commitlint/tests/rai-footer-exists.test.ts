import { describe, it, expect } from 'vitest';
import raiFooterExists from '../src/rules/rai-footer-exists.js';

const validate = (raw?: string) => raiFooterExists({ raw } as any) as [boolean, string];

describe('rai-footer-exists', () => {
  it.each([
    'Generated-by: GitHub Copilot <copilot@github.com>',
    'Assisted-by: Verdent AI <verdent@verdent.ai>',
    'Co-authored-by: GitHub Copilot <copilot@github.com>',
    'Commit-generated-by: Claude AI <claude@anthropic.com>',
    'Authored-by: Jane Doe <jane@example.com>',
    'generated-by: GitHub Copilot <copilot@github.com>', // case insensitive
  ])('should pass with footer: %s', (footer) => {
    const [isValid] = validate(`feat: add feature\n\n${footer}`);
    expect(isValid).toBe(true);
  });

  it('should pass with CRLF line endings', () => {
    const [isValid] = validate('feat: add feature\r\n\r\nGenerated-by: AI <ai@example.com>\r\n');
    expect(isValid).toBe(true);
  });

  it('should pass with attribution anywhere in the message', () => {
    const [isValid] = validate(
      'feat: add feature\n\nGenerated-by: AI <ai@example.com>\n\nMore detail after.',
    );
    expect(isValid).toBe(true);
  });

  it('should pass with attribution among other footers', () => {
    const [isValid] = validate(
      'feat: add feature\n\nDescription\n\nCloses #123\n\nAssisted-by: GitHub Copilot <copilot@github.com>',
    );
    expect(isValid).toBe(true);
  });

  it('should fail without AI attribution footer', () => {
    const [isValid, message] = validate('feat: add new feature\n\nSome other footer');
    expect(isValid).toBe(false);
    expect(message).toContain('AI attribution');
  });

  it('should fail without email', () => {
    const [isValid] = validate('feat: add feature\n\nGenerated-by: GitHub Copilot');
    expect(isValid).toBe(false);
  });

  it('should fail with an empty value', () => {
    const [isValid] = validate('feat: add feature\n\nGenerated-by: ');
    expect(isValid).toBe(false);
  });

  it('should fail when the attribution name is missing', () => {
    const [isValid] = validate('feat: add feature\n\nGenerated-by: <ai@example.com>');
    expect(isValid).toBe(false);
  });

  it('should fail without whitespace after the colon', () => {
    const [isValid] = validate('feat: add feature\n\nGenerated-by:AI <ai@example.com>');
    expect(isValid).toBe(false);
  });

  it('should fail without whitespace before the email', () => {
    const [isValid] = validate('feat: add feature\n\nGenerated-by: AI<ai@example.com>');
    expect(isValid).toBe(false);
  });

  it('should not match an attribution spanning multiple lines', () => {
    const [isValid] = validate('feat: add feature\n\nGenerated-by: GitHub Copilot\n<copilot@github.com>');
    expect(isValid).toBe(false);
  });

  // line breaks JS multiline ^$ accepts but Python rejects — both must reject
  it.each([
    ['a lone carriage-return line break', 'feat: add feature\rGenerated-by: AI <ai@example.com>'],
    ['a lone carriage-return line ending', 'feat: add feature\n\nGenerated-by: AI <ai@example.com>\rjunk'],
    ['a U+2028 line separator', 'feat: add feature\u2028Generated-by: AI <ai@example.com>'],
  ])('should not match across %s', (_label, message) => {
    const [isValid] = validate(message);
    expect(isValid).toBe(false);
  });

  it('should stay linear on a long attribution name', () => {
    const [isValid] = validate(`feat: add feature\n\nGenerated-by: ${'A'.repeat(10000)} <test@example.com>`);
    expect(isValid).toBe(true);
  });

  it('should stay linear on pathological input', () => {
    const [isValid] = validate(`feat: add feature\n\n${'A'.repeat(5000)}:${'B'.repeat(5000)}`);
    expect(isValid).toBe(false);
  });

  it('should fail without a body', () => {
    const [isValid] = validate('feat: add feature');
    expect(isValid).toBe(false);
  });

  it('should fail when commit message is empty or missing', () => {
    const [isValidEmpty, messageEmpty] = validate('');
    expect(isValidEmpty).toBe(false);
    expect(messageEmpty).toContain('AI attribution');

    const [isValidMissing, messageMissing] = validate(undefined);
    expect(isValidMissing).toBe(false);
    expect(messageMissing).toContain('AI attribution');
  });
});
