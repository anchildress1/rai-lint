# Contributing to RAI Lint

Thank you for your interest in RAI Lint!

## AI Attribution Policy

All commits to this repository must include an AI attribution footer using standard Git trailer format:

1. **`Authored-by: [Human] <email>`** - Human only, no AI involvement
2. **`Commit-generated-by: [AI Tool] <email>`** - Trivial AI (docs, commit msg, reviews, advice, etc)
3. **`Assisted-by: [AI Tool] <email>`** - AI helped, but primarily human code
4. **`Co-authored-by: [AI Tool] <email>`** - Roughly half is AI generated and half human-authored content
5. **`Generated-by: [AI Tool] <email>`** - Majority of code was AI generated

Examples:

```plaintext
Authored-by: Jane Doe <jane@example.com>
Commit-generated-by: ChatGPT <chatgpt@openai.com>
Assisted-by: GitHub Copilot <copilot@github.com>
Co-authored-by: GitHub Copilot <copilot@github.com>
Generated-by: GitHub Copilot <copilot@github.com>
```

## Development Setup

### Project Development

Projects are defined individually per solution, but are managed by workspaces and a single makefile.

```bash
make install
make format
make lint
make test
make build

# For AI validation, instruct the agent to confirm results with
make ai-checks
```

## Running Tests

### Node.js Tests

```bash
cd packages/node-commitlint
npm test
npm run test:watch
```

### Python Tests

```bash
cd packages/python-gitlint
pytest tests/ -v
pytest tests/ --cov=gitlint_rai
```

## Code Style

### Node.js

- Follow Airbnb JavaScript Style Guide
- Use ESLint for linting: `npm run lint`
- Format with Prettier: `npm run format`

### Python

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Run all checks before committing

## Commit Message Format

Follow Conventional Commits specification:

```plaintext
<type>(<scope>): <subject>

<body>

<footer>

<rai-footer>
Signed-off-by: Your Name <you@example.com>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`

### Sign-off

Every commit must carry a DCO-style `Signed-off-by` footer — use `git commit -s` and it's
handled for you. This is the same footer the `rai-signed-off-by` rule in both plugins enforces.
The template line above is what `-s` produces — don't also type it by hand or you'll end up
with two.

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Commit with sign-off (`git commit -s`) and proper RAI footer
6. Push to your fork
7. Open a pull request

## Testing Requirements

- All new features must include tests
- Maintain or improve code coverage
- Tests must pass in CI across all Node/Python versions

## Documentation

- Update relevant documentation for new features
- Add examples for new functionality
- Keep architecture diagrams current

## Questions?

Open an issue for any questions or concerns.
