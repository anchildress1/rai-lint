import type { Rule } from '@commitlint/types';

const AI_ATTRIBUTION_PATTERNS = [
  /^Authored-by:[^<]+<[^>]+>$/im,
  /^Commit-generated-by:[^<]+<[^>]+>$/im,
  /^Assisted-by:[^<]+<[^>]+>$/im,
  /^Co-authored-by:[^<]+<[^>]+>$/im,
  /^Generated-by:[^<]+<[^>]+>$/im,
];

const raiFooterExists: Rule = (parsed) => {
  const { raw } = parsed;

  if (!raw) {
    return [false, 'Commit message is empty'];
  }

  const hasValidFooter = AI_ATTRIBUTION_PATTERNS.some((pattern) => pattern.test(raw));

  if (!hasValidFooter) {
    return [
      false,
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
        '  - "Generated-by: GitHub Copilot <copilot@github.com>"',
    ];
  }

  return [true, ''];
};

export default raiFooterExists;
