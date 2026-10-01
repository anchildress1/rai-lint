import { describe, it, expect } from 'vitest';
import raiSignedOffBy from '../src/rules/rai-signed-off-by.js';

const validate = (raw?: string) => raiSignedOffBy({ raw } as any) as [boolean, string];

describe('rai-signed-off-by', () => {
  it.each([
    'Signed-off-by: Jane Doe <jane@example.com>',
    'signed-off-by: Jane Doe <jane@example.com>', // case insensitive
  ])('should pass with footer: %s', (footer) => {
    const [isValid] = validate(`feat: add feature\n\n${footer}`);
    expect(isValid).toBe(true);
  });

  it('should pass with CRLF line endings', () => {
    const [isValid] = validate('feat: add feature\r\n\r\nSigned-off-by: Jane Doe <jane@example.com>\r\n');
    expect(isValid).toBe(true);
  });

  it('should pass with sign-off among other footers', () => {
    const [isValid] = validate(
      'feat: add feature\n\nGenerated-by: GitHub Copilot <copilot@github.com>\nSigned-off-by: Jane Doe <jane@example.com>',
    );
    expect(isValid).toBe(true);
  });

  it('should fail without a Signed-off-by footer', () => {
    const [isValid, message] = validate('feat: add feature\n\nSome other footer');
    expect(isValid).toBe(false);
    expect(message).toContain('Signed-off-by');
  });

  it.each([
    ['no email', 'feat: add feature\n\nSigned-off-by: Jane Doe'],
    ['an empty value', 'feat: add feature\n\nSigned-off-by: '],
    ['a missing name', 'feat: add feature\n\nSigned-off-by: <jane@example.com>'],
    ['no whitespace after the colon', 'feat: add feature\n\nSigned-off-by:Jane Doe <jane@example.com>'],
    ['no whitespace before the email', 'feat: add feature\n\nSigned-off-by: Jane Doe<jane@example.com>'],
    ['trailing whitespace after the email', 'feat: add feature\n\nSigned-off-by: Jane Doe <jane@example.com> '],
    ['a sign-off spanning multiple lines', 'feat: add feature\n\nSigned-off-by: Jane Doe\n<jane@example.com>'],
    ['no body', 'feat: add feature'],
  ])('should reject %s', (_label, message) => {
    const [isValid] = validate(message);
    expect(isValid).toBe(false);
  });

  // line breaks JS multiline ^$ accepts but Python rejects — both must reject
  it.each([
    ['a lone carriage-return line break', 'feat: add feature\rSigned-off-by: Jane Doe <jane@example.com>'],
    ['a lone carriage-return line ending', 'feat: add feature\n\nSigned-off-by: Jane Doe <jane@example.com>\rjunk'],
    ['a U+2028 line separator', 'feat: add feature\u2028Signed-off-by: Jane Doe <jane@example.com>'],
  ])('should not match across %s', (_label, message) => {
    const [isValid] = validate(message);
    expect(isValid).toBe(false);
  });

  it('should stay linear on a long name', () => {
    const [isValid] = validate(`feat: add feature\n\nSigned-off-by: ${'A'.repeat(10000)} <jane@example.com>`);
    expect(isValid).toBe(true);
  });

  it('should stay linear on pathological input', () => {
    const [isValid] = validate(`feat: add feature\n\nSigned-off-by:${'A'.repeat(5000)}:${'B'.repeat(5000)}`);
    expect(isValid).toBe(false);
  });

  it('should fail when commit message is empty or missing', () => {
    const [isValidEmpty, messageEmpty] = validate('');
    expect(isValidEmpty).toBe(false);
    expect(messageEmpty).toContain('Signed-off-by');

    const [isValidMissing, messageMissing] = validate(undefined);
    expect(isValidMissing).toBe(false);
    expect(messageMissing).toContain('Signed-off-by');
  });
});
