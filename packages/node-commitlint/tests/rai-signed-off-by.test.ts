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

  it('should fail without email', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by: Jane Doe');
    expect(isValid).toBe(false);
  });

  it('should fail with an empty value', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by: ');
    expect(isValid).toBe(false);
  });

  it('should fail when the name is missing', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by: <jane@example.com>');
    expect(isValid).toBe(false);
  });

  it('should fail without whitespace after the colon', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by:Jane Doe <jane@example.com>');
    expect(isValid).toBe(false);
  });

  it('should fail without whitespace before the email', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by: Jane Doe<jane@example.com>');
    expect(isValid).toBe(false);
  });

  it('should fail with trailing whitespace after the email', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by: Jane Doe <jane@example.com> ');
    expect(isValid).toBe(false);
  });

  it('should not match a sign-off spanning multiple lines', () => {
    const [isValid] = validate('feat: add feature\n\nSigned-off-by: Jane Doe\n<jane@example.com>');
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

  it('should fail without a body', () => {
    const [isValid] = validate('feat: add feature');
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
