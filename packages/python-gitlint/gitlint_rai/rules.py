import re

from gitlint.rules import CommitRule, RuleViolation

# Keys must stay plain `[A-Za-z-]` literals — they are interpolated into the
# regex unescaped. Must stay identical to the Node plugin's list.
AI_ATTRIBUTION_KEYS = [
    "Authored-by",
    "Commit-generated-by",
    "Assisted-by",
    "Co-authored-by",
    "Generated-by",
]

# The pattern requires `Key: Value` spacing (whitespace after the colon),
# a non-empty attribution name, and a whitespace separator before `<email>`,
# matching the documented footer format. `\r\n` are excluded from the
# name/email runs so a footer cannot match across lines (`\r?$` only tolerates
# a CRLF line ending), and each quantified run is disjoint from the token
# that follows it, keeping evaluation linear (no catastrophic backtracking).
# Must stay identical to the Node plugin's pattern — enforced by
# test_pattern_parity_with_node_plugin.
AI_ATTRIBUTION_PATTERN = re.compile(
    rf"^(?:{'|'.join(AI_ATTRIBUTION_KEYS)}):[^\S\r\n]+[^\s<][^<\r\n]*(?<=\s)<[^>\r\n]+>\r?$",
    re.IGNORECASE | re.MULTILINE,
)

VIOLATION_MESSAGE = (
    "Commit message must include AI attribution footer:\n"
    '  1. "Authored-by: [Human] <contact>" - Human only, no AI\n'
    '  2. "Commit-generated-by: [AI Tool] <contact>" - Trivial AI (docs, commit msg, advice)\n'
    '  3. "Assisted-by: [AI Tool] <contact>" - AI helped, but primarily human code\n'
    '  4. "Co-authored-by: [AI Tool] <contact>" - Roughly 50/50 AI and human (40-60 leeway)\n'
    '  5. "Generated-by: [AI Tool] <contact>" - Majority of code was AI generated\n'
    "\n"
    "Examples:\n"
    '  - "Authored-by: Jane Doe <jane@example.com>"\n'
    '  - "Commit-generated-by: ChatGPT <chatgpt@openai.com>"\n'
    '  - "Assisted-by: GitHub Copilot <copilot@github.com>"\n'
    '  - "Co-authored-by: Verdent AI <verdent@verdent.ai>"\n'
    '  - "Generated-by: GitHub Copilot <copilot@github.com>"'
)


class RaiFooterExists(CommitRule):
    name = "rai-footer-exists"
    id = "UC1"
    target = "commit"

    def validate(self, commit):
        if AI_ATTRIBUTION_PATTERN.search(commit.message.full or ""):
            return []
        return [RuleViolation(self.id, VIOLATION_MESSAGE)]


# Same single-line `Key: Name <email>` shape as AI_ATTRIBUTION_PATTERN, with
# the same linear-time guarantees. Must stay identical to the Node plugin's
# pattern — enforced by test_signoff_pattern_parity_with_node_plugin.
SIGNED_OFF_BY_PATTERN = re.compile(
    r"^Signed-off-by:[^\S\r\n]+[^\s<][^<\r\n]*(?<=\s)<[^>\r\n]+>\r?$",
    re.IGNORECASE | re.MULTILINE,
)

SIGNED_OFF_BY_VIOLATION_MESSAGE = (
    "Commit message must include a Signed-off-by footer:\n"
    '  "Signed-off-by: Your Name <your.email@example.com>"\n'
    "\n"
    "Sign-off is your human stamp confirming you reviewed and take\n"
    "responsibility for the AI attribution. Git adds it for you with\n"
    "`git commit -s` (or `--signoff`)."
)


class RaiSignedOffBy(CommitRule):
    name = "rai-signed-off-by"
    id = "UC2"
    target = "commit"

    def validate(self, commit):
        if SIGNED_OFF_BY_PATTERN.search(commit.message.full or ""):
            return []
        return [RuleViolation(self.id, SIGNED_OFF_BY_VIOLATION_MESSAGE)]
