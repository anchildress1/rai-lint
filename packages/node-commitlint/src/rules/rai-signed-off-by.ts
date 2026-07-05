import type { Rule } from '@commitlint/types';

// Same shape and engine-parity constraints as rai-footer-exists.ts. Must match
// the Python pattern exactly (test_signoff_pattern_parity_with_node_plugin).
const SIGNED_OFF_BY_PATTERN = new RegExp(
  String.raw`(?:^|\n)Signed-off-by:[ \t]+[^ \t<\r\n][^<\r\n]*(?<=[ \t])<[^>\r\n]+>\r?(?:\n|$)`,
  'i',
);

const VIOLATION_MESSAGE =
  'Commit message must include a Signed-off-by footer:\n' +
  '  "Signed-off-by: Your Name <your.email@example.com>"\n' +
  '\n' +
  'Sign-off is your human stamp confirming you reviewed and take\n' +
  'responsibility for the AI attribution. Git adds it for you with\n' +
  '`git commit -s` (or `--signoff`).';

const raiSignedOffBy: Rule = (parsed) => {
  const hasSignOff = SIGNED_OFF_BY_PATTERN.test(parsed.raw ?? '');
  return hasSignOff ? [true, ''] : [false, VIOLATION_MESSAGE];
};

export default raiSignedOffBy;
