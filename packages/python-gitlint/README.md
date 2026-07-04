# gitlint-rai

<p align="center">
  <img
    src="https://raw.githubusercontent.com/anchildress1/admin-things/main/assets/logos/checkmark-rai-lint-logo.png"
    alt="RAI Lint"
    width="160"
  />
</p>

<p align="center">
  A gitlint plugin that enforces exactly one thing:<br />
  if AI touched the code, say so in the commit. ⚖️
</p>

<p align="center">
  That’s it. No philosophy, no negotiations. Pick a trailer and move on.
</p>

## Installation 🔧

```bash
pip install gitlint-rai
```

Or with `uv`, which is objectively the better choice:

```bash
uv add gitlint-rai
```

## Usage 🚦

Run the bundled wrapper — it loads the RAI rules automatically and accepts all gitlint arguments:

```bash
gitlint-rai
gitlint-rai --msg-filename .git/COMMIT_EDITMSG
```

Prefer plain `gitlint`? Point your `.gitlint` config at the installed package:

```ini
[general]
extra-path=/path/to/site-packages/gitlint_rai
```

Get that path with:

```bash
python -c "import gitlint_rai, pathlib; print(pathlib.Path(gitlint_rai.__file__).parent)"
```

To verify the rule loaded:

```bash
gitlint-rai --debug
```

Look for `rai-footer-exists` in the loaded-rules output. If you see it, the plugin is active and doing its job.

## Valid Trailers 📌

Pick the one that matches the **majority AI contribution**.
Skip it entirely and the commit fails.
Extra footers are fine — the rule only checks that at least one valid footer exists.

This is not a debate.

1. `Authored-by: [Human] <email>` — all you, no AI involved
2. `Commit-generated-by: [AI Tool] <email>` — AI wrote the commit message, you wrote the code
3. `Assisted-by: [AI Tool] <email>` — AI helped some, you were driving
4. `Co-authored-by: [AI Tool] <email>` — roughly 50/50, like actual pair programming
5. `Generated-by: [AI Tool] <email>` — AI did most of it, you supervised

All patterns are case-insensitive, because life is too short for that kind of pedantry.

## Why This Exists ⚖️

Git already supports trailers. Commits already support attribution.
What they don’t do is _require_ you to be honest when AI is involved.

This plugin exists to make that honesty boring, consistent, and automatic, so nobody has to reconstruct intent later by reading commit history like tea leaves.

If you want the longer reasoning behind this, it lives at [Did AI Erase Attribution?](https://dev.to/anchildress1/did-ai-erase-attribution-your-git-history-is-missing-a-co-author-1m2l).

This plugin is the practical follow-through.

## Requirements ⚙️

- Python >= 3.11, < 3.15
- gitlint >= 0.19.1

## License 📄

PolyForm Shield License 1.0.0
