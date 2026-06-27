# Installation Guide

> [!TIP]
> New to this whole RAI attribution thing? Start here: [Did AI Erase Attribution? Your Git History Is Missing a Co-Author](https://dev.to/anchildress1/did-ai-erase-attribution-your-git-history-is-missing-a-co-author-1m2l).

---

## Prerequisites

### Node.js Projects

- Node.js >= 20.0.0, < 27.0.0
- npm or yarn
- A Git repository (obviously)

### Python Projects

- Python >= 3.11, < 3.13
- uv (not pip—use uv)
- A Git repository

---

## Node.js Installation

### 1. Install the Plugin

```bash
npm install --save-dev @checkmarkdevtools/commitlint-plugin-rai @commitlint/cli @commitlint/config-conventional
```

### 2. Configure Commitlint

Create or update `commitlint.config.js`:

```javascript
export default {
  extends: ['@commitlint/config-conventional'],
  plugins: ['@checkmarkdevtools/commitlint-plugin-rai'],
  rules: {
    'rai-footer-exists': [2, 'always'],
    // Optional but recommended for complete accountability:
    // 'signed-off-by-exists': [2, 'always'],
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

Create or update `.gitlint`:

```ini
[general]
contrib = gitlint_rai.rules.RaiFooterExists

# Optional but recommended for complete accountability:
# contrib = gitlint_rai.rules.RaiFooterExists,gitlint_rai.rules.SignedOffByExists
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
        entry: gitlint
        args: [--msg-filename]
        language: python
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
gitlint --msg-filename="$1"
```

Make it executable:

```bash
chmod +x .git/hooks/commit-msg
```

---

## Verification

Test everything with a valid commit:

```bash
git commit -m "test: verify RAI lint setup

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

**Problem**: `Module not found: @checkmarkdevtools/commitlint-plugin-rai`

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
      run: gitlint --msg-filename {1}
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
        entry: gitlint
        args: [--msg-filename]
        language: python
        stages: [commit-msg]
```
