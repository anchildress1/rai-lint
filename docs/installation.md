# Installation Guide

> [!TIP]
> New to this whole RAI attribution thing? Start here: [Did AI Erase Attribution? Your Git History Is Missing a Co-Author](https://dev.to/anchildress1/did-ai-erase-attribution-your-git-history-is-missing-a-co-author-1m2l).

---

## Prerequisites

### Node.js Projects

- Node.js >= 22.0.0, < 27.0.0
- npm or yarn
- A Git repository (obviously)

### Python Projects

- Python >= 3.11, < 3.15
- uv (not pip—use uv)
- A Git repository

---

## Node.js Installation

### 1. Install the Plugin

```bash
npm install --save-dev commitlint-plugin-rai @commitlint/cli @commitlint/config-conventional
```

### 2. Configure Commitlint

Create or update `commitlint.config.js`:

```javascript
export default {
  extends: ['@commitlint/config-conventional'],
  plugins: ['commitlint-plugin-rai'],
  rules: {
    'rai-footer-exists': [2, 'always'],
    // Requires the Signed-off-by footer from `git commit -s`:
    'rai-signed-off-by': [2, 'always'],
  },
};
```

### 3. Set Up Git Hooks

You need a hook manager. Pick one.

#### Option A: Lefthook (I use this one)

```bash
npm install --save-dev lefthook
```

Create `lefthook.yml`:

```yaml
commit-msg:
  commands:
    commitlint:
      run: npx --no-install commitlint --edit {1}
```

Install hooks:

```bash
npx lefthook install
```

#### Option B: Husky

```bash
npm install --save-dev husky
npx husky install
npx husky add .husky/commit-msg 'npx --no-install commitlint --edit $1'
```

---

## Python Installation

### 1. Install the Plugin

```bash
uv add gitlint-rai
```

For dev dependencies:

```bash
uv add gitlint-rai --dev
```

### 2. Configure Gitlint

Simplest path: run the bundled `gitlint-rai` CLI instead of `gitlint`. It loads the RAI rules automatically and accepts all gitlint arguments — no config needed.

For plain `gitlint`, point `.gitlint` at the installed package:

```ini
[general]
extra-path=/path/to/site-packages/gitlint_rai

# Both RAI rules load automatically: rai-footer-exists (UC1) and
# rai-signed-off-by (UC2). To skip sign-off enforcement:
# ignore=rai-signed-off-by
```

Get that path with:

```bash
python -c "import gitlint_rai, pathlib; print(pathlib.Path(gitlint_rai.__file__).parent)"
```

### 3. Set Up Git Hooks

Again, pick a hook manager.

#### Option A: pre-commit (standard for Python projects)

```bash
uv add pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: gitlint
        name: gitlint
        entry: gitlint-rai
        args: [--msg-filename]
        language: python
        additional_dependencies: ['gitlint-rai']
        stages: [commit-msg]
```

Install hooks:

```bash
pre-commit install --hook-type commit-msg
```

#### Option B: Manual Git Hook

If you don't want a hook manager, do it manually.

Create `.git/hooks/commit-msg`:

```bash
#!/bin/sh
gitlint-rai --msg-filename "$1"
```

Make it executable:

```bash
chmod +x .git/hooks/commit-msg
```

---

## Verification

Test everything with a valid commit:

```bash
git commit -s -m "test: verify RAI lint setup

Assisted-by: GitHub Copilot <copilot@github.com>"
```

This should succeed. Now try an invalid one:

```bash
git commit -m "test: this should fail"
```

This should get rejected with an error message explaining what you need to add.

---

## Troubleshooting

### Node.js Issues

**Problem**: `Module not found: commitlint-plugin-rai`

**Fix**: You didn't install it. Run the install command again and check `package.json`.

**Problem**: Commitlint not running on commit

**Fix**: Your hooks aren't installed. Check:

```bash
ls -la .git/hooks/commit-msg
```

If nothing's there, re-run the hook install step.

### Python Issues

**Problem**: `ImportError: No module named 'gitlint_rai'`

**Fix**: Reinstall:

```bash
uv add --reinstall gitlint-rai
```

**Problem**: Gitlint not finding the rule

**Fix**: Check your `.gitlint` config. Debug with:

```bash
gitlint --debug
```

---

### Lefthook Configuration

```yaml
commit-msg:
  commands:
    commitlint:
      run: npx --no-install commitlint --edit {1}
    gitlint:
      run: gitlint-rai --msg-filename {1}
```

### pre-commit Configuration

```yaml
repos:
  - repo: local
    hooks:
      - id: commitlint
        name: commitlint
        entry: npx --no-install commitlint --edit
        language: system
        stages: [commit-msg]

      - id: gitlint
        name: gitlint
        entry: gitlint-rai
        args: [--msg-filename]
        language: python
        additional_dependencies: ['gitlint-rai']
        stages: [commit-msg]
```
