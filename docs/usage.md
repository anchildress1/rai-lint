# Usage Guide

## What This Actually Does

RAI Lint enforces AI attribution in Git commit trailers. No attribution footer = rejected commit. Simple.

**Read the full context**: [Did AI Erase Attribution? Your Git History Is Missing a Co-Author](https://dev.to/anchildress1/did-ai-erase-attribution-your-git-history-is-missing-a-co-author-1m2l)

---

## Valid RAI Footer Formats

Five footer patterns. All case-insensitive. Pick **one** that represents the **majority AI contribution**.

> [!TIP]
> The `Signed-off-by` footer is YOUR human stamp confirming you reviewed and take responsibility for the AI attribution. Both plugins enforce it with their own `rai-signed-off-by` rule: `gitlint-rai` enables it by default (rule id `UC2`; opt out with `ignore=rai-signed-off-by` in `.gitlint`), and commitlint enables it via `'rai-signed-off-by': [2, 'always']` in your config.

### Signed-off-by

**Complete accountability.** This is YOUR stamp confirming you reviewed and take responsibility for the AI attribution.

**Add it automatically:** `git commit -s` (or `--signoff`)

```bash
# Your AI attribution prompt generates:
git commit -m "feat: implement user authentication

Add JWT-based authentication with refresh tokens and secure session management.

Authored-by: Jane Doe <jane@example.com>"

# Then add Signed-off-by with the -s flag:
git commit --amend -s

# Or combine in one step:
git commit -s -m "feat: implement user authentication

Add JWT-based authentication with refresh tokens and secure session management.

Authored-by: Jane Doe <jane@example.com>"
```

### 1. Authored-by

**When**: Zero AI involvement. You wrote everything.

```
feat: implement user authentication

Add JWT-based authentication with refresh tokens and secure session management.

Authored-by: Jane Doe <jane@example.com>
```

### 2. Commit-generated-by

**When**: AI only generated trivial stuff—docs, commit messages, advice. No actual code changes.

```
docs: update README installation instructions

Improved clarity and added troubleshooting section.

Commit-generated-by: GitHub Copilot <copilot@github.com>
```

### 3. Assisted-by

**When**: AI helped in spots, but the work is clearly yours.

```
fix: resolve race condition in payment processing

Added mutex locks to prevent concurrent payment processing issues.

Assisted-by: GitHub Copilot <copilot@github.com>
```

### 4. Co-authored-by

**When**: The work was meaningfully shared between you and AI.

```
feat: add data validation pipeline

Implemented validation logic with custom rules and error handling.

Co-authored-by: GitHub Copilot <copilot@github.com>
```

### 5. Generated-by

**When**: Most of the implementation came from AI output.

```
chore: update dependencies to latest versions

Updated all npm packages to latest compatible versions.

Generated-by: GitHub Copilot <copilot@github.com>
```

---

## Commit Message Structure

RAI footers go at the end, after all other Git trailers:

```
<type>(<scope>): <subject>

<body>

<other-git-trailers>

<rai-footer>
```

Example with multiple trailers:

```
feat(auth)!: add OAuth2 integration

Implemented OAuth2 authentication flow with Google and GitHub providers.
Added automatic account linking for existing users.

BREAKING CHANGE: Removed legacy session-based authentication
Closes #123
Co-authored-by: GitHub Copilot <copilot@github.com>
```

---

## CLI Usage

### Node.js / Commitlint

Test a commit message (note: you'd normally use `git commit -s`):

```bash
printf 'feat: add feature\n\nGenerated-by: GitHub Copilot <copilot@github.com>\nSigned-off-by: Your Name <your.email@example.com>\n' | npx --no-install commitlint
```

Validate the last commit:

```bash
npx --no-install commitlint --from HEAD~1
```

Validate a specific commit:

```bash
npx --no-install commitlint --from abc123f
```

Validate a commit range:

```bash
npx --no-install commitlint --from main --to develop
```

### Python / Gitlint

`gitlint-rai` wraps gitlint, loads the RAI rules automatically, and accepts all gitlint arguments. Plain `gitlint` works too if `.gitlint` sets `extra-path` (see [installation](installation.md)).

Lint the last commit (assumes you used `git commit -s`):

```bash
gitlint-rai
```

Lint a specific commit:

```bash
gitlint-rai --commit abc123f
```

Lint from a file:

```bash
gitlint-rai --msg-filename .git/COMMIT_EDITMSG
```

Test a message via stdin (note: you'd normally use `git commit -s`):

```bash
printf 'feat: add feature\n\nGenerated-by: GitHub Copilot <copilot@github.com>\nSigned-off-by: Your Name <your.email@example.com>\n' | gitlint-rai
```

---

## IDE Integration

Most IDEs don't natively support custom Git trailers. Add footers manually or use a GitHub Copilot custom prompt.

**GitHub Copilot Instructions**: See [anchildress1/awesome-github-copilot#prompts](https://github.com/anchildress1/awesome-github-copilot?tab=readme-ov-file#prompts-%E2%80%8D) for a reusable Copilot prompt that auto-generates RAI footers in commit messages.

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint Commits

on: pull_request

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v6
        with:
          node-version: 22

      - run: npm ci

      - run: npx --no-install commitlint --from ${{ github.event.pull_request.base.sha }} --to ${{ github.sha }}
```

### GitLab CI

```yaml
commitlint:
  stage: test
  image: node:22
  script:
    - npm ci
    - npx --no-install commitlint --from $CI_MERGE_REQUEST_TARGET_BRANCH_SHA --to HEAD
  only:
    - merge_requests
```

### Jenkins

```groovy
stage('Commit Lint') {
  steps {
    sh 'npm ci'
    sh 'npx --no-install commitlint --from origin/main --to HEAD'
  }
}
```

---

## Common Issues

### Footer Not Detected

**Symptoms**: Commit rejected even though footer is present.

**Causes**:

1. Extra whitespace before the footer
2. Footer not on its own line
3. Typo in the footer keyword
4. Missing angle brackets around email info

**Example**:

```bash
# ❌ Wrong
"Generatedby: GitHub Copilot copilot@github.com"

# ✅ Correct
"Generated-by: GitHub Copilot <copilot@github.com>"
```

### Multiple Footers

**Question**: Can I include multiple RAI footers?

**Answer**: Yes — the rule only checks that at least one valid footer exists. Convention: pick the one that represents the **majority AI contribution**.

### Amending Commits

Add Signed-off-by to the previous commit:

```bash
git commit --amend -s --no-edit
```

Or if you need to add an AI attribution footer too:

```bash
git commit --amend -s -m "$(git log -1 --pretty=%B)" -m "" -m "Assisted-by: GitHub Copilot <copilot@github.com>"
```

> [!WARNING]
> Requires force push permissions. If force pushes are disabled, create a new commit instead.

### Rebasing

When rebasing, ensure all commits include the required RAI footer (and Signed-off-by if you're enforcing it):

```bash
git rebase -i HEAD~5
```

For each commit without footers, use `edit`:

```bash
# Add AI attribution footer and sign off in one step
git commit --amend -s -m "$(git log -1 --pretty=%B)" -m "" -m "Assisted-by: GitHub Copilot <copilot@github.com>"
git rebase --continue
```

> [!WARNING]
> Requires force push permissions. If force pushes are disabled, create a new commit instead.
