# Troubleshooting Guide

> [!TIP]
> If you're wondering why this matters, read the full story: [Did AI Erase Attribution? Your Git History Is Missing a Co-Author](https://dev.to/anchildress1/did-ai-erase-attribution-your-git-history-is-missing-a-co-author-1m2l).

---

## Node.js / Commitlint Issues

### "Cannot find module 'commitlint-plugin-rai'"

**What happened**: The package isn't installed or node_modules is broken.

**Fix it**:

```bash
npm install --save-dev commitlint-plugin-rai
rm -rf node_modules package-lock.json
npm install
```

---

### "Plugin not found: commitlint-plugin-rai"

**What happened**: You didn't add it to your `commitlint.config.js`.

**Fix it**: Add this to your config:

```javascript
export default {
  plugins: ['commitlint-plugin-rai'],
  rules: {
    'rai-footer-exists': [2, 'always'],
    'rai-signed-off-by': [2, 'always'],
  },
};
```

---

### Hook not running on commit

**What happened**: Git hooks aren't installed.

**Fix it (Lefthook)**:

```bash
npx lefthook install
```

**Fix it (Husky)**:

```bash
npx husky install
npx husky add .husky/commit-msg 'npx --no-install commitlint --edit $1'
```

**Verify**:

```bash
ls -la .git/hooks/commit-msg
cat .git/hooks/commit-msg
```

---

### "ReferenceError: require is not defined"

**What happened**: You're using CommonJS syntax in an ESM module.

**Fix it**: Either convert to ESM or use `.cjs` extension:

```javascript
// ❌ Wrong (CommonJS in .js file with "type": "module")
module.exports = { ... }

// ✅ Option 1: ESM syntax
export default { ... }

// ✅ Option 2: Rename to commitlint.config.cjs
// commitlint.config.cjs
module.exports = { ... }
```

---

## Python / Gitlint Issues

### "ModuleNotFoundError: No module named 'gitlint_rai'"

**What happened**: Package isn't installed.

**Fix it**:

```bash
uv add gitlint-rai
uv run python -c "import gitlint_rai; print('Installed')"
```

---

### Gitlint can't find the RAI rules

**What happened**: Your `.gitlint` config uses `contrib=` — that only loads gitlint's own bundled contrib rules, never this package's. External rules load via `extra-path` (a filesystem path) or the `gitlint-rai` CLI.

**Fix it**: Use `gitlint-rai` instead of `gitlint` (it loads the rules automatically), or point `extra-path` at the installed package:

```ini
[general]
extra-path=/path/to/site-packages/gitlint_rai
```

Get that path with:

```bash
python -c "import gitlint_rai, pathlib; print(pathlib.Path(gitlint_rai.__file__).parent)"
```

**Debug it** (`--debug` lists the loaded rules):

```bash
gitlint-rai --debug
python -c "from gitlint_rai.rules import RaiFooterExists; print(RaiFooterExists)"
```

---

### pre-commit hook not running

**What happened**: Hooks aren't installed.

**Fix it**:

```bash
pre-commit install --hook-type commit-msg
pre-commit run --hook-stage commit-msg --commit-msg-filename .git/COMMIT_EDITMSG
```

**Verify**:

```bash
ls -la .git/hooks/commit-msg
```

---

## Footer Validation Issues

### Valid footer rejected

**Symptoms**: You added a footer but the commit still fails.

**Common mistakes**:

1. **Extra whitespace**

   ```bash
   # ❌ Wrong (leading space)
   " Generated-by: GitHub Copilot <copilot@github.com>"

   # ✅ Right
   "Generated-by: GitHub Copilot <copilot@github.com>"
   ```

2. **Wrong keyword**

   ```bash
   # ❌ Wrong (not a valid keyword)
   "Created-by: GitHub Copilot <copilot@github.com>"

   # ✅ Right
   "Generated-by: GitHub Copilot <copilot@github.com>"
   ```

3. **Typo**

   ```bash
   # ❌ Wrong (missing hyphen)
   "Generatedby: GitHub Copilot <copilot@github.com>"

   # ✅ Right
   "Generated-by: GitHub Copilot <copilot@github.com>"
   ```

4. **Missing angle brackets**

   ```bash
   # ❌ Wrong (no brackets)
   "Generated-by: GitHub Copilot copilot@github.com"

   # ✅ Right
   "Generated-by: GitHub Copilot <copilot@github.com>"
   ```

**Debug it**:

```bash
# Check exact bytes
echo "Generated-by: GitHub Copilot <copilot@github.com>" | xxd

# Test the pattern
printf 'feat: test\n\nGenerated-by: GitHub Copilot <copilot@github.com>\n' | npx --no-install commitlint
```

---

### "Commit message must include a Signed-off-by footer"

**What happened**: The `rai-signed-off-by` rule is on and your commit has no sign-off.

**Fix it**: Let Git add it:

```bash
git commit -s -m "..."          # new commit
git commit --amend -s --no-edit # fix the last one
```

**Opt out**: drop `'rai-signed-off-by'` from your commitlint rules, or set
`ignore=rai-signed-off-by` in `.gitlint` for the Python side.

---

### Footer appears but still fails

**What happened**: Footer isn't on its own line.

**Fix it**: Add a blank line before the footer:

```bash
# ❌ Wrong (no blank line)
feat: add feature
Generated-by: GitHub Copilot <copilot@github.com>

# ✅ Right (blank line before footer)
feat: add feature

Generated-by: GitHub Copilot <copilot@github.com>
```

---

## CI/CD Issues

### GitHub Actions failing on commitlint

**What happened**: Shallow clone doesn't have commit history.

**Fix it**: Use `fetch-depth: 0`:

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

---

### Python tests failing in CI

**What happened**: gitlint isn't installed in the CI environment.

**Fix it**: Install with test dependencies:

```yaml
- name: Install dependencies
  run: |
    uv sync --locked --group dev
```

---

## IDE Integration Issues

### VS Code not showing commit errors

**What happened**: Extension isn't configured.

**Fix it**: Install the Conventional Commits extension and add to settings:

```json
{
  "conventionalCommits.autoCommit": false,
  "conventionalCommits.promptFooter": true
}
```

---

### JetBrains IDE not running hook

**What happened**: Git hooks aren't enabled in the IDE.

**Fix it**:

1. Go to Settings → Version Control → Git
2. Enable "Run Git hooks"
3. Restart IDE

---

## Debugging Commands

### Node.js

```bash
# Test a commit message
printf 'feat: test\n\nGenerated-by: GitHub Copilot <copilot@github.com>\n' | npx --no-install commitlint

# Verbose output
npx --no-install commitlint --verbose --edit .git/COMMIT_EDITMSG

# Debug mode
DEBUG=* npx --no-install commitlint --edit .git/COMMIT_EDITMSG

# Check config
npx --no-install commitlint --print-config
```

### Python

```bash
# Test a commit message
printf 'feat: test\n\nGenerated-by: GitHub Copilot <copilot@github.com>\n' | gitlint-rai

# Verbose output
gitlint-rai --verbose

# Debug mode (also prints the active config and loaded rules)
gitlint-rai --debug
```

---

## Getting Help

If none of this worked:

1. Check [GitHub Issues](https://github.com/anchildress1/rai-lint/issues)
2. Run with `--debug` or `--verbose` flags
3. Verify your versions:

   ```bash
   # Node
   node --version
   npm list commitlint-plugin-rai

   # Python
   python --version
   uv pip show gitlint-rai
   ```

4. Create a minimal reproduction case
5. Open a new issue with debug output
