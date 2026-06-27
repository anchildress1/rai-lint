import { describe, it, expect } from 'vitest';
import raiFooterExists from '../src/rules/rai-footer-exists.js';

describe('rai-footer-exists', () => {
  it('should pass with Generated-by footer', async () => {
    const parsed = {
      raw: 'feat: add new feature\n\nGenerated-by: GitHub Copilot <copilot@github.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should pass with Assisted-by footer', async () => {
    const parsed = {
      raw: 'fix: resolve bug\n\nAssisted-by: Verdent AI <verdent@verdent.ai>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should pass with Co-authored-by footer', async () => {
    const parsed = {
      raw: 'refactor: improve code\n\nCo-authored-by: GitHub Copilot <copilot@github.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should pass with Commit-generated-by footer', async () => {
    const parsed = {
      raw: 'chore: update dependencies\n\nCommit-generated-by: Claude AI <claude@anthropic.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should pass with Authored-by footer', async () => {
    const parsed = {
      raw: 'feat: implement feature\n\nAuthored-by: Jane Doe <jane@example.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should fail without AI attribution footer', async () => {
    const parsed = {
      raw: 'feat: add new feature\n\nSome other footer',
    } as any;

    const [isValid, message] = await raiFooterExists(parsed);
    expect(isValid).toBe(false);
    expect(message).toContain('AI attribution');
  });

  it('should pass with case-insensitive footer', async () => {
    const parsed = {
      raw: 'feat: add feature\n\ngenerated-by: GitHub Copilot <copilot@github.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should fail with malformed footer', async () => {
    const parsed = {
      raw: 'feat: add feature\n\nGenerated-by: Invalid Format',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(false);
  });

  it('should pass with multiple AI tools', async () => {
    const parsed = {
      raw: 'feat: complex feature\n\nGenerated-by: ChatGPT <chatgpt@openai.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should accept guidance percentages', async () => {
    const parsed = {
      raw: 'feat: add feature\n\nAssisted-by: GitHub Copilot <copilot@github.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(true);
  });

  it('should fail when the attribution name is missing', async () => {
    const parsed = {
      raw: 'feat: add feature\n\nGenerated-by: <ai@example.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(false);
  });

  it('should fail without whitespace after the colon', async () => {
    const parsed = {
      raw: 'feat: add feature\n\nGenerated-by:AI <ai@example.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(false);
  });

  it('should fail without whitespace before the email', async () => {
    const parsed = {
      raw: 'feat: add feature\n\nGenerated-by: AI<ai@example.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(false);
  });

  it('should not match an attribution spanning multiple lines', async () => {
    const parsed = {
      raw: 'feat: add feature\n\nGenerated-by: GitHub Copilot\n<copilot@github.com>',
    } as any;

    const [isValid] = await raiFooterExists(parsed);
    expect(isValid).toBe(false);
  });

  it('should fail when commit message is empty', async () => {
    const parsedEmpty = {} as any;
    const [isValidEmpty, messageEmpty] = await raiFooterExists(parsedEmpty);
    expect(isValidEmpty).toBe(false);
    expect(messageEmpty).toContain('Commit message is empty');

    const parsedBlank = { raw: '' } as any;
    const [isValidBlank, messageBlank] = await raiFooterExists(parsedBlank);
    expect(isValidBlank).toBe(false);
    expect(messageBlank).toContain('Commit message is empty');
  });
});
