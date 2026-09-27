# Maintain the AIQ Site Tools package

The maintained skills are in `.agents/skills/`. The packaged copies are in `plugins/aiq-site-tools/skills/`. Change the maintained skills, then run `python scripts/build_site_tools.py`. Run `python scripts/build_site_tools.py --check` before a release. The build includes required guidance and the image capture helper. It keeps two skills visible to users.

Keep the site model and map skills in one package. The map skill reads the site model data contract. The Codex marketplace is in `.agents/plugins/marketplace.json`; the Claude marketplace is in `.claude-plugin/marketplace.json`.

Before a public release, select a licence and test installation on clean devices with Codex, Claude Code, and OpenCode. Test a live run in Rhino and check `.ai` output in the selected authoring application.

## Checks on 2026-09-27

- The package build matched its sources, and all local links in packaged Markdown resolved.
- The Codex plugin validator passed. Both marketplace files and all plugin manifests parsed as JSON.
- The OpenCode installer copied both skills to a temporary project. `opencode debug skill` found both.
- The site model suite ran 82 tests: 72 passed and 10 live Rhino tests were skipped outside Rhino.
- Claude Code was absent from the test device. The installed Codex CLI had no `plugin` command. Those install routes still need checks on supported versions.
