import type { Rule } from '@commitlint/types';

// Keys must stay plain `[A-Za-z-]` literals — they are interpolated into the
// regex unescaped. Must stay identical to the Python plugin's list.
const AI_ATTRIBUTION_KEYS = [
  'Authored-by',
  'Commit-generated-by',
  'Assisted-by',
  'Co-authored-by',
  'Generated-by',
];

// The pattern requires `Key: Value` spacing (whitespace after the colon),
// a non-empty attribution name, and a whitespace separator before `<email>`,
// matching the documented footer format. `\r\n` are excluded from the
// name/email runs so a footer cannot match across lines (`\r?$` only tolerates
// a CRLF line ending), and each quantified run is disjoint from the token
// that follows it, keeping evaluation linear (no catastrophic backtracking).
// Must stay identical to the Python plugin's pattern — enforced by
// test_pattern_parity_with_node_plugin in the Python suite.
const AI_ATTRIBUTION_PATTERN = new RegExp(
  String.raw`^(?:${AI_ATTRIBUTION_KEYS.join('|')}):[^\S\r\n]+[^\s<][^<\r\n]*(?<=\s)<[^>\r\n]+>\r?$`,
  'im',
);

const VIOLATION_MESSAGE =
  'Commit message must include AI attribution footer:\n' +
  '  1. "Authored-by: [Human] <contact>" - Human only, no AI\n' +
  '  2. "Commit-generated-by: [AI Tool] <contact>" - Trivial AI (docs, commit msg, advice)\n' +
  '  3. "Assisted-by: [AI Tool] <contact>" - AI helped, but primarily human code\n' +
  '  4. "Co-authored-by: [AI Tool] <contact>" - Roughly 50/50 AI and human (40-60 leeway)\n' +
  '  5. "Generated-by: [AI Tool] <contact>" - Majority of code was AI generated\n' +
  '\n' +
  'Examples:\n' +
  '  - "Authored-by: Jane Doe <jane@example.com>"\n' +
  '  - "Commit-generated-by: ChatGPT <chatgpt@openai.com>"\n' +
  '  - "Assisted-by: GitHub Copilot <copilot@github.com>"\n' +
  '  - "Co-authored-by: Verdent AI <verdent@verdent.ai>"\n' +
  '  - "Generated-by: GitHub Copilot <copilot@github.com>"';

const raiFooterExists: Rule = (parsed) => {
  const hasValidFooter = AI_ATTRIBUTION_PATTERN.test(parsed.raw ?? '');
  return hasValidFooter ? [true, ''] : [false, VIOLATION_MESSAGE];
};

export default raiFooterExists;
