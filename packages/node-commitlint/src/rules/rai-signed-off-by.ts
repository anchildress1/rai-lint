import type { Rule } from '@commitlint/types';

// Same single-line `Key: Name <email>` shape as the attribution pattern in
// rai-footer-exists.ts, with the same linear-time and engine-parity
// guarantees (see the comment there for why the anchors and whitespace
// classes are explicit). Must stay identical to the Python plugin's pattern —
// enforced by test_signoff_pattern_parity_with_node_plugin in the Python
// suite.
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
