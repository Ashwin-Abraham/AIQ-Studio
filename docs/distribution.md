# Install AIQ Site Tools

AIQ Site Tools has two skills:

- **Rhino Site Data Model** builds a checked `.3dm` model from a site boundary.
- **Vector Site Maps** makes analysis boards from the model's checked 2D data.

## What you need

- Windows and Rhino 8 for a live Rhino model.
- Internet access to download Overture map data.
- An application that can save and check `.ai` files if you need finished Illustrator files.

The site model also needs an external Python environment. Ask the agent to run the skill's `scripts/preflight.py` with that Python before it starts. The check reports missing Python packages. The agent can then set up a managed environment outside your project folder.

## Install in Codex

1. Open the AIQ Studio repository as a project in the Codex app.
2. Restart the app. Open the Plugins Directory and select **AIQ Studio**.
3. Install **AIQ Site Tools**. Start a new chat.

## Install in Claude Code

Add the AIQ Studio marketplace and install the plugin:

```text
claude plugin marketplace add Ashwin-Abraham/AIQ-Studio
claude plugin install aiq-site-tools@aiq-studio
```

Start a new Claude Code session.

## Install in OpenCode

Download or clone the AIQ Studio repository. Open PowerShell in that folder and run:

```powershell
.\scripts\install_opencode_skills.ps1
```

The script copies both skills to your personal OpenCode skills folder. Restart OpenCode. To get an update, download the new package and run the script again. If PowerShell blocks the script, copy both folders from `plugins/aiq-site-tools/skills/` to `%USERPROFILE%\.config\opencode\skills\`.

## Start a project

Give the agent a site boundary or an existing Rhino model, plus a project folder. You can use these requests:

- “Use Rhino Site Data Model to build a 2D site model for this boundary.”
- “Use Vector Site Maps to make site analysis boards from this checked model.”

For a 3D model, the agent will ask about terrain. For finished `.ai` files, make sure your vector authoring application is available.
