import os
import subprocess
import sys
from pathlib import Path

import pytest

from gitlint_rai.__main__ import RULES_PATH, main

# lets `-m gitlint_rai` resolve in subprocesses when the project runs from
# source (CI installs with --no-install-project)
SUBPROCESS_ENV = {
    **os.environ,
    "PYTHONPATH": os.pathsep.join(
        p for p in [str(Path(RULES_PATH).parent), os.environ.get("PYTHONPATH")] if p
    ),
}

VALID_MESSAGE = (
    "feat: add a thing\n"
    "\n"
    "A body line that satisfies the default length rules.\n"
    "\n"
    "Generated-by: GitHub Copilot <copilot@github.com>\n"
)

INVALID_MESSAGE = "feat: add a thing\n\nA body line without any attribution footer.\n"


def run_main(monkeypatch, argv):
    captured = {}

    def fake_cli():
        captured["argv"] = sys.argv[:]
        raise SystemExit(0)

    monkeypatch.setattr("gitlint_rai.__main__.cli", fake_cli)
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        main()
    return captured["argv"]


class TestArgvInjection:
    def test_injects_absolute_rules_path(self, monkeypatch):
        argv = run_main(monkeypatch, ["gitlint-rai"])
        assert argv[1:] == ["--extra-path", RULES_PATH]
        assert Path(RULES_PATH).is_absolute()
        assert (Path(RULES_PATH) / "rules.py").is_file()

    def test_injection_precedes_user_args(self, monkeypatch):
        argv = run_main(monkeypatch, ["gitlint-rai", "--msg-filename", "msg.txt"])
        assert argv[1:] == ["--extra-path", RULES_PATH, "--msg-filename", "msg.txt"]

    def test_injection_precedes_subcommand(self, monkeypatch):
        # click group options are rejected after a subcommand, so the
        # injected pair must come first for `gitlint-rai install-hook`.
        argv = run_main(monkeypatch, ["gitlint-rai", "install-hook"])
        assert argv[1:] == ["--extra-path", RULES_PATH, "install-hook"]

    def test_user_extra_path_wins(self, monkeypatch):
        argv = run_main(monkeypatch, ["gitlint-rai", "--extra-path", "/custom"])
        injected = argv.index(RULES_PATH)
        custom = argv.index("/custom")
        assert injected < custom


def run_cli(tmp_path, message):
    msg_file = tmp_path / "msg.txt"
    msg_file.write_text(message)
    # cwd is a directory with no gitlint_rai/ in it: the exact setup the
    # relative --extra-path bug failed under.
    return subprocess.run(
        [sys.executable, "-m", "gitlint_rai", "--msg-filename", str(msg_file)],
        cwd=tmp_path,
        env=SUBPROCESS_ENV,
        capture_output=True,
        text=True,
    )


class TestCliFromForeignCwd:
    def test_missing_footer_reports_uc1(self, tmp_path):
        result = run_cli(tmp_path, INVALID_MESSAGE)
        assert result.returncode != 0
        assert "UC1" in result.stderr

    def test_valid_footer_passes(self, tmp_path):
        result = run_cli(tmp_path, VALID_MESSAGE)
        assert result.returncode == 0, result.stderr

    def test_plain_gitlint_loads_rule_via_absolute_extra_path(self, tmp_path):
        msg_file = tmp_path / "msg.txt"
        msg_file.write_text(INVALID_MESSAGE)
        result = subprocess.run(
            [
                str(Path(sys.executable).parent / "gitlint"),
                "--extra-path",
                RULES_PATH,
                "--msg-filename",
                str(msg_file),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "UC1" in result.stderr
