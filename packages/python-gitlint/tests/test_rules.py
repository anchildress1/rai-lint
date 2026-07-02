import re
from pathlib import Path
from unittest.mock import Mock

import pytest

from gitlint_rai.rules import AI_ATTRIBUTION_KEYS, AI_ATTRIBUTION_PATTERN, RaiFooterExists

NODE_RULE_SOURCE = (
    Path(__file__).resolve().parents[2]
    / "node-commitlint"
    / "src"
    / "rules"
    / "rai-footer-exists.ts"
)


@pytest.fixture
def rule():
    return RaiFooterExists()


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


def test_pattern_parity_with_node_plugin():
    """Both plugins promise identical validation; fail loudly if the sources drift."""
    source = NODE_RULE_SOURCE.read_text()

    node_keys = re.findall(r"'([A-Za-z-]+-by)'", source)
    assert node_keys == AI_ATTRIBUTION_KEYS

    template = re.search(
        r"new RegExp\(\s*`\^\(\?:\$\{AI_ATTRIBUTION_KEYS\.join\('\|'\)\}\)(.*?)`", source
    )
    assert template, "pattern template not found in Node plugin source"
    node_suffix = template.group(1).replace("\\\\", "\\")
    python_suffix = AI_ATTRIBUTION_PATTERN.pattern.split(")", 1)[1]
    assert node_suffix == python_suffix
