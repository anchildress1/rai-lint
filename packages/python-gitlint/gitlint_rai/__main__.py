import sys
from pathlib import Path

from gitlint.cli import cli

RULES_PATH = str(Path(__file__).resolve().parent)


def main():
    args = sys.argv[1:]
    # gitlint is a click group: group-level options must precede any
    # subcommand, so the injected path goes first. A user-supplied
    # -e/--extra-path wins because click keeps the last occurrence.
    sys.argv = [sys.argv[0], "--extra-path", RULES_PATH, *args]
    sys.exit(cli())


if __name__ == "__main__":
    main()
