import type { Plugin } from '@commitlint/types';
import raiFooterExists from './rules/rai-footer-exists.js';
import raiSignedOffBy from './rules/rai-signed-off-by.js';

const plugin: Plugin = {
  rules: {
    'rai-footer-exists': raiFooterExists,
    'rai-signed-off-by': raiSignedOffBy,
  },
};

export default plugin;
