# commitlint-plugin-rai

<p align="center">
  <img
    src="https://raw.githubusercontent.com/anchildress1/rai-lint/main/docs/assets/rai-lint-logo.svg"
    alt="RAI Lint"
    width="160"
  />
</p>

<p align="center">
  A commitlint plugin that enforces exactly one thing:<br />
  if AI touched the code, say so in the commit. ⚖️
</p>

<p align="center">
  That’s it. No philosophy, no negotiations. Pick a trailer and move on.
</p>

## Installation 🔧

```bash
npm install --save-dev commitlint-plugin-rai
```

## Usage 🚦

Add the plugin to your `commitlint.config.js`:

```js
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

Once this is in place, commitlint will refuse to proceed until a valid RAI trailer is present — and, with `rai-signed-off-by` enabled, a `Signed-off-by: Your Name <email>` footer too.

## Valid Trailers 📌

Pick the one that matches the **majority AI contribution**.
Skip it entirely and the commit fails.
Extra footers are fine — the rule only checks that at least one valid footer exists.

No negotiations.

1. `Authored-by: [Human] <email>` — all you, no AI involved
2. `Commit-generated-by: [AI Tool] <email>` — AI wrote the commit message, you wrote the code
3. `Assisted-by: [AI Tool] <email>` — AI helped some, you were still driving
4. `Co-authored-by: [AI Tool] <email>` — roughly 50/50, like actual pair programming
5. `Generated-by: [AI Tool] <email>` — AI did most of it, you supervised

All patterns are case-insensitive, because enforcing honesty does not require enforcing capitalization.

## Why This Exists ⚖️

If two humans pair program, both names go on the commit.
If an AI helps and we pretend it didn’t happen, that’s a choice, but it’s a strange one.

Git already supports trailers. This plugin just closes the gap between “we could do this” and “we actually do this,” by making attribution a default instead of a discussion.

If you want the longer version of that reasoning, it’s written up at [Did AI Erase Attribution?](https://dev.to/anchildress1/did-ai-erase-attribution-your-git-history-is-missing-a-co-author-1m2l).

This plugin is the boring enforcement layer that follows.

## Requirements ⚙️

- Node.js >= 22.0.0, < 27.0.0
- @commitlint/cli >= 19.0.0

## License 📄

[PolyForm Shield License 1.0.0](./LICENSE) — free to use anywhere, including inside commercial products. What's off the table: providing anything that competes with this tool — selling it, rebranding it, hosting it, or shipping a practical substitute, paid or free. This is a plain-language summary; the [LICENSE](./LICENSE) is what actually controls. Commercial licensing questions: [anchildress1@gmail.com](mailto:anchildress1@gmail.com).
