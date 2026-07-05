import { describe, it, expect } from 'vitest';
import plugin from '../src/index';

describe('plugin export', () => {
  it('should export a valid commitlint plugin', () => {
    expect(plugin).toBeDefined();
    expect(plugin.rules).toBeDefined();
  });

  it.each(['rai-footer-exists', 'rai-signed-off-by'])('should have %s rule', (name) => {
    const rule = plugin.rules[name];
    expect(typeof rule).toBe('function');
  });
});
