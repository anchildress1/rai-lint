import re
from pathlib import Path
from unittest.mock import Mock

import pytest

from gitlint_rai.rules import (
    AI_ATTRIBUTION_KEYS,
    AI_ATTRIBUTION_PATTERN,
    SIGNED_OFF_BY_PATTERN,
    SIGNED_OFF_BY_VIOLATION_MESSAGE,
    VIOLATION_MESSAGE,
    RaiFooterExists,
    RaiSignedOffBy,
)

NODE_RULES_DIR = Path(__file__).resolve().parents[2] / "node-commitlint" / "src" / "rules"
NODE_RULE_SOURCE = NODE_RULES_DIR / "rai-footer-exists.ts"
NODE_SIGNOFF_RULE_SOURCE = NODE_RULES_DIR / "rai-signed-off-by.ts"


@pytest.fixture
def rule():
    return RaiFooterExists()


@pytest.fixture
def signoff_rule():
    return RaiSignedOffBy()


def create_commit(message: str):
    commit = Mock()
    commit.message.full = message
    return commit


class TestRaiFooterExists:
    @pytest.mark.parametrize(
        "footer",
        [
            "Generated-by: GitHub Copilot <copilot@github.com>",
            "Assisted-by: Verdent AI <verdent@verdent.ai>",
            "Co-authored-by: GitHub Copilot <copilot@github.com>",
            "Commit-generated-by: Claude AI <claude@anthropic.com>",
            "Authored-by: Jane Doe <jane@example.com>",
            "generated-by: GitHub Copilot <copilot@github.com>",  # case insensitive
        ],
    )
    def test_valid_footers(self, rule, footer):
        commit = create_commit(f"feat: add feature\n\n{footer}")
        violations = rule.validate(commit)
        assert len(violations) == 0, f"Expected no violations for {footer}"

    def test_crlf_line_endings(self, rule):
        commit = create_commit("feat: add feature\r\n\r\nGenerated-by: AI <ai@example.com>\r\n")
        violations = rule.validate(commit)
        assert len(violations) == 0

    def test_attribution_anywhere_in_message(self, rule):
        commit = create_commit(
            "feat: add feature\n\nGenerated-by: AI <ai@example.com>\n\nMore detail after."
        )
        violations = rule.validate(commit)
        assert len(violations) == 0

    def test_attribution_with_other_footers(self, rule):
        commit = create_commit(
            "feat: add feature\n\nDescription\n\nCloses #123\n\n"
            "Assisted-by: GitHub Copilot <copilot@github.com>"
        )
        violations = rule.validate(commit)
        assert len(violations) == 0

    def test_generated_by_footer_no_email(self, rule):
        commit = create_commit("feat: add new feature\n\nGenerated-by: GitHub Copilot")
        violations = rule.validate(commit)
        assert len(violations) == 1
        assert "AI attribution" in violations[0].message

    def test_missing_ai_attribution(self, rule):
        commit = create_commit("feat: add new feature\n\nSome other footer")
        violations = rule.validate(commit)
        assert len(violations) == 1
        assert "AI attribution" in violations[0].message

    def test_malformed_footer_empty_value(self, rule):
        commit = create_commit("feat: add feature\n\nGenerated-by: ")
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_missing_attribution_name(self, rule):
        commit = create_commit("feat: add feature\n\nGenerated-by: <ai@example.com>")
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_no_whitespace_after_colon(self, rule):
        commit = create_commit("feat: add feature\n\nGenerated-by:AI <ai@example.com>")
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_no_whitespace_before_email(self, rule):
        commit = create_commit("feat: add feature\n\nGenerated-by: AI<ai@example.com>")
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_attribution_spanning_multiple_lines(self, rule):
        commit = create_commit(
            "feat: add feature\n\nGenerated-by: GitHub Copilot\n<copilot@github.com>"
        )
        violations = rule.validate(commit)
        assert len(violations) == 1

    # line breaks JS multiline ^$ accepts but Python rejects — both must reject
    @pytest.mark.parametrize(
        "message",
        [
            "feat: add feature\rGenerated-by: AI <ai@example.com>",
            "feat: add feature\n\nGenerated-by: AI <ai@example.com>\rjunk",
            "feat: add feature\u2028Generated-by: AI <ai@example.com>",
        ],
    )
    def test_engine_divergent_line_breaks(self, rule, message):
        violations = rule.validate(create_commit(message))
        assert len(violations) == 1

    def test_redos_resistance_long_trailer_value(self, rule):
        long_value = "A" * 10000
        commit = create_commit(
            f"feat: add feature\n\nGenerated-by: {long_value} <test@example.com>"
        )
        violations = rule.validate(commit)
        assert len(violations) == 0

    def test_redos_resistance_pathological_input(self, rule):
        pathological = "A" * 5000 + ":" + "B" * 5000
        commit = create_commit(f"feat: add feature\n\n{pathological}")
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_empty_message(self, rule):
        commit = create_commit("")
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_none_message(self, rule):
        commit = create_commit("")
        commit.message.full = None
        violations = rule.validate(commit)
        assert len(violations) == 1

    def test_no_body(self, rule):
        commit = create_commit("feat: add feature")
        violations = rule.validate(commit)
        assert len(violations) == 1


class TestRaiSignedOffBy:
    @pytest.mark.parametrize(
        "footer",
        [
            "Signed-off-by: Jane Doe <jane@example.com>",
            "signed-off-by: Jane Doe <jane@example.com>",  # case insensitive
        ],
    )
    def test_valid_footers(self, signoff_rule, footer):
        commit = create_commit(f"feat: add feature\n\n{footer}")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 0, f"Expected no violations for {footer}"

    def test_crlf_line_endings(self, signoff_rule):
        commit = create_commit(
            "feat: add feature\r\n\r\nSigned-off-by: Jane Doe <jane@example.com>\r\n"
        )
        violations = signoff_rule.validate(commit)
        assert len(violations) == 0

    def test_signoff_among_other_footers(self, signoff_rule):
        commit = create_commit(
            "feat: add feature\n\nGenerated-by: GitHub Copilot <copilot@github.com>\n"
            "Signed-off-by: Jane Doe <jane@example.com>"
        )
        violations = signoff_rule.validate(commit)
        assert len(violations) == 0

    def test_missing_signoff(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSome other footer")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1
        assert "Signed-off-by" in violations[0].message

    def test_signoff_no_email(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by: Jane Doe")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_malformed_footer_empty_value(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by: ")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_missing_name(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by: <jane@example.com>")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_no_whitespace_after_colon(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by:Jane Doe <jane@example.com>")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_no_whitespace_before_email(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by: Jane Doe<jane@example.com>")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_trailing_whitespace_after_email(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by: Jane Doe <jane@example.com> ")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_signoff_spanning_multiple_lines(self, signoff_rule):
        commit = create_commit("feat: add feature\n\nSigned-off-by: Jane Doe\n<jane@example.com>")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    # line breaks JS multiline ^$ accepts but Python rejects — both must reject
    @pytest.mark.parametrize(
        "message",
        [
            "feat: add feature\rSigned-off-by: Jane Doe <jane@example.com>",
            "feat: add feature\n\nSigned-off-by: Jane Doe <jane@example.com>\rjunk",
            "feat: add feature\u2028Signed-off-by: Jane Doe <jane@example.com>",
        ],
    )
    def test_engine_divergent_line_breaks(self, signoff_rule, message):
        violations = signoff_rule.validate(create_commit(message))
        assert len(violations) == 1

    def test_redos_resistance_long_name(self, signoff_rule):
        long_value = "A" * 10000
        commit = create_commit(
            f"feat: add feature\n\nSigned-off-by: {long_value} <jane@example.com>"
        )
        violations = signoff_rule.validate(commit)
        assert len(violations) == 0

    def test_redos_resistance_pathological_input(self, signoff_rule):
        pathological = "Signed-off-by:" + "A" * 5000 + ":" + "B" * 5000
        commit = create_commit(f"feat: add feature\n\n{pathological}")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_empty_message(self, signoff_rule):
        commit = create_commit("")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_none_message(self, signoff_rule):
        commit = create_commit("")
        commit.message.full = None
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1

    def test_no_body(self, signoff_rule):
        commit = create_commit("feat: add feature")
        violations = signoff_rule.validate(commit)
        assert len(violations) == 1


def test_pattern_parity_with_node_plugin():
    """Both plugins promise identical validation; fail loudly if the sources drift."""
    source = NODE_RULE_SOURCE.read_text()

    keys_block = re.search(r"const AI_ATTRIBUTION_KEYS = \[(.*?)\]", source, re.DOTALL)
    assert keys_block, "key list not found in Node plugin source"
    node_keys = re.findall(r"'([^']+)'", keys_block.group(1))
    assert node_keys == AI_ATTRIBUTION_KEYS

    # The 'i' flag (and the absence of 'm') is part of the match so flag
    # changes in the Node source fail this test, not just pattern-text edits.
    # String.raw means the template text is the literal pattern — no unescaping.
    template = re.search(
        r"new RegExp\(\s*String\.raw`\(\?:\^\|\\n\)\(\?:\$\{AI_ATTRIBUTION_KEYS\.join\('\|'\)\}\)(.*?)`,\s*'i',?\s*\)",
        source,
    )
    assert template, "pattern template with 'i' flag not found in Node plugin source"
    node_suffix = template.group(1)
    python_suffix = AI_ATTRIBUTION_PATTERN.pattern.split(")", 2)[2]
    assert node_suffix == python_suffix
    assert AI_ATTRIBUTION_PATTERN.flags & re.IGNORECASE
    assert not AI_ATTRIBUTION_PATTERN.flags & re.MULTILINE


def test_message_parity_with_node_plugin():
    """The violation text is duplicated across plugins; fail loudly if it drifts."""
    source = NODE_RULE_SOURCE.read_text()

    block = re.search(r"const VIOLATION_MESSAGE =\n(.*?);", source, re.DOTALL)
    assert block, "violation message not found in Node plugin source"
    node_message = "".join(re.findall(r"'([^']*)'", block.group(1))).replace("\\n", "\n")
    assert node_message == VIOLATION_MESSAGE


def test_signoff_pattern_parity_with_node_plugin():
    """Both plugins promise identical sign-off validation; fail loudly on drift."""
    source = NODE_SIGNOFF_RULE_SOURCE.read_text()

    # The 'i' flag (and the absence of 'm') is part of the match so flag
    # changes in the Node source fail this test, not just pattern-text edits.
    # String.raw means the template text is the literal pattern — no unescaping.
    template = re.search(
        r"new RegExp\(\s*String\.raw`(.*?)`,\s*'i',?\s*\)",
        source,
        re.DOTALL,
    )
    assert template, "pattern template with 'i' flag not found in Node plugin source"
    assert template.group(1) == SIGNED_OFF_BY_PATTERN.pattern
    assert SIGNED_OFF_BY_PATTERN.flags & re.IGNORECASE
    assert not SIGNED_OFF_BY_PATTERN.flags & re.MULTILINE


def test_signoff_message_parity_with_node_plugin():
    """The violation text is duplicated across plugins; fail loudly if it drifts."""
    source = NODE_SIGNOFF_RULE_SOURCE.read_text()

    block = re.search(r"const VIOLATION_MESSAGE =\n(.*?);", source, re.DOTALL)
    assert block, "violation message not found in Node plugin source"
    node_message = "".join(re.findall(r"'([^']*)'", block.group(1))).replace("\\n", "\n")
    assert node_message == SIGNED_OFF_BY_VIOLATION_MESSAGE
