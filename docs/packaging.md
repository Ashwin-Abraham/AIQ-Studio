# Maintain the AIQ Site Tools package

The skill instructions, references, scripts, and map templates live in `plugins/aiq-site-tools/skills/`. This is the maintained source and the installable package. The two small entries in `.agents/skills/` make these skills visible when an agent works in this repository. They point to the package and hold no workflow code.

The site model tests live in `tests/rhino-site-data-model/`. Run them with:

```text
python -B -m unittest discover -s tests/rhino-site-data-model -q
```

The Codex marketplace is in `.agents/plugins/marketplace.json`. The Claude marketplace is in `.claude-plugin/marketplace.json`. Both point to the same package. The OpenCode installer copies the package skills to a user's personal skills folder.

Before a public release, select a licence and test installation in Codex, Claude Code, and OpenCode. Test a live run in Rhino and check `.ai` output in the selected authoring application.
