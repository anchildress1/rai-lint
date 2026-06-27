# Security Policy

## Supported Versions

I'm moving fast. If you're not on the latest version, you're on your own.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

Found a security hole? **Don't tweet about it.**

If you find a vulnerability that lets someone bypass the AI attribution checks or inject malicious code via the plugins:

1. **Do not open a GitHub issue.** That just tells the bad guys where the keys are.
2. Email me directly at `anchildress1@gmail.com`.
3. Give me a chance to fix it before you go full "hacker news" on me.

### What qualifies?

- **Remote Code Execution (RCE)**: If you can make the linter run `rm -rf /` on someone's machine, that's bad. Tell me.
- **Bypass**: If you can commit AI-generated code without the footer and the linter says "looks good," that's a bug, but maybe not a CVE. Open an issue for that one.
- **Dependency Issues**: If one of my dependencies has a CVE, I probably already know because Dependabot is yelling at me. But feel free to ping me if I'm sleeping on it.

### The "Don't Be A Jerk" Clause

I'm a tinkerer, not a Fortune 500 company. I don't have a bug bounty program. I can't pay you $10,000 for finding a cross-site scripting bug in a CLI tool (how would that even work?).

But if you help me fix a serious issue responsibly, I'll happily credit you in the release notes and buy you a coffee (virtual or otherwise) if we ever meet.

**TL;DR:** Be cool, report responsibly, and let's keep the supply chain clean.
