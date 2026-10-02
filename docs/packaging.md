# Maintain the AIQ Site Tools package

The skill instructions, references, scripts, and map templates live in `plugins/aiq-site-tools/skills/`. This is the maintained source and the installable package. The two small entries in `.agents/skills/` make these skills visible when an agent works in this repository. They point to the package and hold no workflow code.

The site model tests live in `tests/rhino-site-data-model/`. Run them with:

```text
python -B -m unittest discover -s tests/rhino-site-data-model -q
```

The Codex marketplace is in `.agents/plugins/marketplace.json`. The Claude marketplace is in `.claude-plugin/marketplace.json`. Both point to the same package. The OpenCode installer copies the package skills to a user's personal skills folder.

Before a public release, select a licence and test installation in Codex, Claude Code, and OpenCode. Test a live run in Rhino and check `.ai` output in the selected authoring application.

## Desktop setup pages

GitHub Pages serves the `docs` folder from `main`. Each README app button opens its page in `setup/`. Each page makes one attempt to open the local app. The user accepts any browser prompt. Manual launch links and installation guides remain available if the browser blocks the launch. The `.nojekyll` file keeps this site as static files.

Codex and Claude Code receive a prepared installation request. The user reviews and sends it in the app. Claude Code uses the [documented Claude Desktop link](https://support.claude.com/en/articles/14729294-open-claude-desktop-with-a-link), so this route needs Claude Desktop with Claude Code access.

OpenCode opens through its registered `opencode://` protocol. The user copies the request from the page, selects a project in the app, and pastes it into a new chat. OpenCode's [new-session link parser](https://github.com/anomalyco/opencode/blob/dev/packages/app/src/pages/layout/deep-links.ts) needs a local directory. The website cannot determine that directory. Check the desktop handoff on supported app versions before a release.
