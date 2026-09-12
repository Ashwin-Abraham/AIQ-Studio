# Agent-Driven Host Integration Plan

**Status:** Working proposal for refinement  
**Recorded:** 2026-09-11

## Purpose

Distribute AIQ Studio workflows to nontechnical AEC users while keeping AIQ Studio as the visible product. Let users run the workflows with their preferred AI harness, such as OpenAI Codex, Claude Code, or OpenCode.

The AI harness supplies the agent and model usage. The AIQ host plug-in supplies the professional workflow package, host application access, user interface, and branded outputs.

## Central requirement

AIQ workflows are agent-driven procedures. They are not deterministic commands that start and then return one output.

For example, the [Rhino Site Data Model skill](../.agents/skills/rhino-site-data-model/SKILL.md) requires the agent to:

- resolve the site and target document;
- select data sources and context;
- request human decisions when information is uncertain;
- run different scripts at different stages;
- inspect the Rhino document and generated previews;
- interpret validation results;
- revise the work when necessary;
- report sources, assumptions, and unresolved conditions.

Deterministic commands and scripts support the agent. They do not replace it.

## Product model

AIQ Studio has five main modules.

### AIQ workflow package

The complete agent procedure for one workflow. It contains:

- `SKILL.md`;
- references;
- scripts;
- templates and other assets;
- version and compatibility information.

The host plug-in is the authoritative source for the workflow packages that depend on that host.

### AIQ host plug-in

A plug-in for Rhino, Revit, SketchUp, or another AEC application. It contains:

- the host-specific workflow packages;
- deterministic host commands;
- access to the active document, selection, views, and application state;
- preview and approval user interfaces;
- workflow session management;
- AIQ Studio branding and output metadata.

The first implementation is **AIQ Studio for Rhino**.

### AIQ session

A local record of one agent-driven workflow. It contains a fixed snapshot of the selected workflow package, inputs, outputs, logs, decisions, and current state.

### AIQ host interface

The small interface through which an external agent can inspect and safely modify a host application. Its implementation remains inside the host plug-in.

### Harness adapter

A thin plug-in or skill package for one AI harness. It provides discovery, AIQ Studio branding, installation help, and access to the AIQ host interface. It does not contain the authoritative host workflow implementation.

Internal adapter names can include their host for clarity:

- AIQ Studio for OpenAI;
- AIQ Studio for Claude;
- AIQ Studio for OpenCode.

All plug-ins use **AIQ Studio** as their user-facing name because the containing application already identifies the host.

## Architecture

```text
OpenAI / Claude / OpenCode
        |
        | reads the session skill and invokes AIQ commands
        v
Harness adapter
        |
        v
aiq.exe command adapter
        |
        | private local protocol
        v
AIQ Studio host plug-in
        |
        +-- workflow packages
        +-- deterministic scripts and commands
        +-- active host document
        +-- previews and approvals
        +-- session state and branded outputs
```

The agent remains the workflow controller. The host plug-in remains the authority for host state and permitted host actions.

## Skill hierarchy

The harness-level skill is a router. For example, `plan-site` performs these steps:

1. Find an installed and active AIQ host.
2. Create or attach to an AIQ session.
3. Ask the host for the applicable workflow package.
4. Load the host-owned skill into the agent context.
5. Continue under the instructions in that skill.

The router uses an AIQ command instead of a direct reference to a host plug-in folder. Store-installed plug-ins can be copied to private cache paths, and external file references are not portable across harnesses.

```powershell
aiq session open --workflow plan-site --preferred-host rhino --json
```

An example result is:

```json
{
  "status": "ready",
  "host": "rhino",
  "sessionId": "7db...",
  "skill": "rhino-site-data-model",
  "skillEntrypoint": "C:\\...\\SKILL.md",
  "workflowVersion": "0.3.0"
}
```

The command returns an explicit condition when the workflow cannot start:

- `aiq_not_installed`;
- `host_plugin_not_installed`;
- `host_not_running`;
- `no_document_open`;
- `workflow_not_available`;
- `plugin_update_required`.

The harness adapter converts each condition into a branded and specific user instruction.

## Session materialization

When the user selects **Ask AI**, the host plug-in creates an AIQ session folder and copies the complete workflow package into it.

```text
AIQ Session/
  session.json
  skills.lock.json
  .agents/skills/rhino-site-data-model/
    SKILL.md
    references/
    scripts/
  inputs/
  outputs/
  logs/
```

The launcher can also create harness-specific compatibility paths when a harness does not read `.agents/skills`.

Copying the package freezes the exact skill, references, and scripts used for the Workflow Application. A later plug-in update does not change an active or completed session.

The session record must include:

- workflow and host plug-in versions;
- active host and document identity;
- document revision or equivalent change marker;
- selected AI harness and provider;
- user decisions and approvals;
- source and output artifact paths;
- action history and errors;
- completion or interruption state.

## Ask AI flow

### Start from the host application

1. The user opens a document in Rhino.
2. The user selects **Ask AI** in the AIQ Studio panel.
3. AIQ Studio asks for the workflow and preferred harness when necessary.
4. The host plug-in creates the session and materializes its workflow package.
5. The launcher opens the harness in the session folder.
6. The harness loads the materialized skill.
7. The agent runs the skill and uses AIQ commands to interact with Rhino.
8. Rhino shows previews and approvals for material changes.
9. The session records all actions and outputs.

### Start from an AI harness

1. The user invokes a harness-level skill such as `plan-site`.
2. The harness adapter runs the AIQ installation and host checks.
3. If the Rhino plug-in is missing, the adapter shows the Rhino Package Manager installation route.
4. If Rhino is not running, the adapter asks the user to open it and the applicable document.
5. When Rhino is available, the adapter creates or attaches to a session.
6. The agent loads and runs the host-owned workflow skill.

## Local host connection

### Command adapter

`aiq.exe` is the primary adapter for coding-agent harnesses. The skill invokes it through the harness command tool.

Example operations are:

```powershell
aiq status --json
aiq session state --json
aiq rhino document describe --json
aiq rhino selection describe --json
aiq rhino preview show plan.json
aiq rhino action run import-site-data --input processed.json
aiq rhino validation run --json
```

The command adapter sends structured requests to the active host plug-in. It returns structured results, artifact paths, progress, and errors.

### Private protocol

On Windows, the first implementation can use a per-session named pipe:

```text
\\.\pipe\AIQStudio.Rhino.<session-id>
```

The pipe is restricted to the current user. The session supplies a short-lived connection token. The connection is local and does not carry OpenAI or Anthropic credentials.

The Rhino implementation performs these steps for each request:

1. Validate the session and requested action.
2. Check that the active document still matches the expected revision.
3. Send Rhino work to the Rhino user-interface thread.
4. Show a preview or approval when required.
5. Run the permitted action.
6. Return a structured result.
7. Append the result to the session journal.

The interface exposes an allowlist of AIQ actions. It does not expose unrestricted Python execution or arbitrary Rhino commands.

## Role of MCP

MCP is an optional adapter. It is not the workflow engine and it is not the authoritative host interface.

```text
MCP adapter
      |
      v
AIQ host interface
```

An MCP adapter can translate MCP tool calls into the same local AIQ requests when a harness works better with MCP. The command adapter and MCP adapter must share the same host interface and behavior.

This design keeps workflow logic in the agent skill and host behavior in the host plug-in. Removing or replacing one adapter does not change the workflows.

## Human control and document safety

The agent can inspect and prepare work without repeated approval. Rhino remains the authority for material document changes.

Use these controls:

- show the target document and proposed action;
- show a preview when the result can be previewed;
- require approval for material or destructive changes;
- reject an action when the document changed after the agent prepared it;
- keep partial outputs when they are useful;
- record validation failures instead of presenting them as success;
- let the user cancel and resume a session.

## Branding and professional identity

The host plug-in is the primary product surface. The harness is a conversation surface.

Use **AIQ Studio** as the user-facing product name in each host. Use these qualified names only in code, packages, issue titles, and technical documents that discuss several hosts:

- **AIQ Studio for Rhino**;
- **AIQ Studio for Revit**;
- **AIQ Studio for SketchUp**;
- **AIQ Studio for OpenAI**;
- **AIQ Studio for Claude**;
- **AIQ Studio for OpenCode**;
- **AIQ Bridge** for the shared local connection implementation.

Each output must record:

- AIQ Studio workflow name and version;
- host application and plug-in version;
- AI provider and harness;
- source and assumption records;
- validation status;
- a link to AIQ Studio documentation.

The Rhino panel owns progress, warnings, previews, approvals, and final outputs. This keeps AIQ Studio visible throughout the work.

## Distribution model

### Host distribution

Publish AIQ Studio for Rhino through Rhino Package Manager. The package contains the host plug-in, workflow packages, command adapter, and required local assets.

### Harness distribution

Publish a thin branded adapter through each supported harness distribution route:

- OpenAI public plug-in directory or local marketplace;
- Claude community or official marketplace;
- OpenCode skill catalog, configuration, or package ecosystem.

The first public release includes the Rhino Host Plug-in plus OpenAI and OpenCode Harness Plug-ins. Claude remains in the shared architecture and is planned after the first release.

The adapter should provide useful functions before the host is installed. These can include workflow documentation, installation checks, compatibility checks, and inspection of existing AIQ reports.

Actual control of a local Rhino process is available only from a harness that can run locally and reach the AIQ command adapter.

The first release can assume that the user has Rhino 8, one supported local AI Harness, a valid account for that harness, and permission to install both plug-ins.

Implementation can proceed with broad agent autonomy. Human approval is required for public names, external data and privacy behavior, pricing or entitlements, store submissions, promotional wording, destructive changes, and hard-to-reverse architecture decisions.

An end-of-workflow promotional note is outside the first-release scope. Keep it as a future decision about store policy, user experience, placement, frequency, wording, and opt-out behavior.

## Revised ideas

The following earlier ideas changed during discussion:

- **Deterministic workflow runner:** The agent runs the workflow. Deterministic operations support individual stages.
- **Host skill folder reference:** The host materializes a versioned session copy instead of relying on a direct path from a cached harness plug-in.
- **MCP as the bridge:** The AIQ host interface and private local protocol are primary. MCP is one optional adapter.
- **Provider-specific host integration:** The host plug-in integrates with AIQ Bridge. Provider-specific behavior stays in harness adapters.

## Open questions

### Skill loading

- Which common session directory layout works across Codex, Claude Code, and OpenCode?
- Which harnesses can reload a new skill during an active conversation?
- When must the launcher start a new conversation after it materializes the skill?
- Should the session contain one portable skill tree or generated compatibility trees?

### Host interface

- What is the smallest useful set of inspection and action operations?
- Which actions require a Rhino-side preview or approval?
- How should long-running data downloads and processing report progress?
- How should the interface represent document revisions and stale requests?

### Session lifecycle

- Where should AIQ sessions be stored?
- How does a user resume a session from Rhino and from a harness?
- Can a user change harness during one Workflow Application?
- Which session files belong in final project deliverables?

### Distribution

- Can the command adapter ship inside the Rhino package on all target platforms?
- What signing and update process is required for `aiq.exe`?
- Which OpenAI surfaces can run the local command adapter?
- What review conditions apply to a harness plug-in that depends on a separate Rhino plug-in?

### Security and privacy

- Which model and document data can leave the machine?
- How does the user approve the data sent to the selected provider?
- How are session connection tokens created, stored, and revoked?
- What audit information is required for professional use?

### Commercial model

- Which functions are free, paid, or licensed by organization?
- How does the host plug-in verify an AIQ Studio entitlement without controlling model billing?
- Which workflow packages can be installed independently?

## Recommended prototype

Build one narrow prototype before committing to all harnesses.

1. Package the existing Rhino Site Data Model skill inside a mock AIQ Studio for Rhino installation folder.
2. Add an **Ask AI** command that creates a versioned session copy.
3. Launch one local harness in that session folder.
4. Implement `aiq status`, `aiq rhino document describe`, and one harmless Rhino action.
5. Connect `aiq.exe` to a Rhino test plug-in through a named pipe.
6. Confirm that the agent can load the skill, ask the user a workflow question, inspect Rhino state, and perform the approved action.
7. Record every request and result in the session journal.
8. Evaluate whether the interface remains suitable for a second host or harness.

The prototype is complete when one agent can progress through several skill stages, pause for a human decision, inspect live Rhino state, perform one approved document action, and resume from the recorded session state.

## Current recommendation

Keep the agent in control of the workflow. Keep the complete workflow package in the applicable AIQ host plug-in. Materialize a fixed workflow copy for each session. Use a small command adapter and private local protocol as the primary host connection. Add MCP only where it improves a specific harness integration.

This structure keeps AIQ Studio independent of model providers while retaining its workflow knowledge, host integration, professional identity, and output record.

## Platform references

These links describe current platform behavior and can change:

- [OpenAI plug-in packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude Code plug-ins](https://code.claude.com/docs/en/plugins)
- [Claude Code plug-in file rules](https://code.claude.com/docs/en/plugins-reference)
- [OpenCode skills](https://opencode.ai/docs/skills)
- [OpenCode MCP servers](https://opencode.ai/docs/mcp-servers/)
- [Rhino Package Manager](https://developer.rhino3d.com/guides/yak/what-is-yak/)
