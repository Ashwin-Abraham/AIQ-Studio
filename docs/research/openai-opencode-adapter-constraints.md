# OpenAI and OpenCode local adapter constraints

Research completed on 11 September 2026.

## Question

AIQ Studio needs two AI harness adapters for its first release:

- an OpenAI adapter for ChatGPT and Codex;
- an OpenCode adapter.

Each adapter must help a nontechnical Rhino user find AIQ Studio, start an AI session, load an agent-run workflow, and let the agent use safe Rhino functions. AIQ Studio must not pay for the user's model usage.

This report checks these areas:

- extension and plug-in surfaces;
- installation and distribution;
- skill loading;
- local commands and MCP;
- new and resumed sessions;
- account and token ownership;
- the best first-release route.

The report uses only official OpenAI and OpenCode sources. It separates documented facts from design inferences and questions that need a prototype.

## Principal conclusion

Do not make MCP the primary local bridge for the first release.

Use this arrangement:

```text
AI harness
    |
    | local shell or harness tool
    v
aiq.exe
    |
    | private, authenticated local protocol
    v
AIQ Studio Rhino plug-in
```

The harness owns the AI session and model account. The workflow skill owns the agent procedure. `aiq.exe` gives the procedure a stable set of commands. The Rhino plug-in owns Rhino state, previews, approvals, and document changes.

OpenAI and OpenCode have different distribution limits. Use one conceptual adapter contract, but do not require one identical package format.

- OpenAI has a public plug-in directory. A plug-in can contain the small AIQ router skill. Public OpenAI submissions cannot use a local MCP server through the normal submission path.
- OpenCode can install an npm plug-in and can load `.agents/skills`. Its documentation does not say that an npm plug-in can install a bundled skill. The Rhino launcher must therefore create the session skill folder, or a separate installer must add the skill.

## Verified OpenAI facts

### Plug-in and extension surfaces

OpenAI plug-ins can contain skills, an MCP server, or both. They can also contain presentation assets and Codex lifecycle hooks. A skill can contain `SKILL.md`, references, scripts, templates, and assets. OpenAI recommends skills for procedures and MCP tools for live data, authorization, and controlled actions. A skill can also work without MCP. [OpenAI plug-in architecture](https://developers.openai.com/plugins/concepts/plugins) and [OpenAI skill construction](https://developers.openai.com/plugins/build/skills)

ChatGPT and Codex use one public plug-in directory. Plug-ins work in Chat and Work on supported ChatGPT surfaces, and in Codex in the ChatGPT desktop app. Codex CLI has a plug-in browser. The IDE extension does not support plug-ins. After a CLI user installs a plug-in, the user must start a new session before its skills or tools become available. [OpenAI plug-in use](https://learn.chatgpt.com/docs/plugins)

OpenAI supports a portable Agent Plugins package. Its root contains `plugin.json`. It can also contain `skills/`, `mcp.json`, hooks, and assets. Local and repository marketplaces support development, testing, and private distribution. Public plug-ins use the shared public directory. The manifest can contain the developer name, website, brand colour, logo, screenshots, and starter prompts. [OpenAI plug-in packaging](https://developers.openai.com/plugins/build/plugins)

### Skill loading

Codex can load local skills from `.agents/skills` between the current working directory and the repository root. It can also load user, administrator, and system skills. Codex detects skill changes, but OpenAI tells users to restart Codex if a change does not appear. Plug-ins are the documented distribution method for reusable skills beyond one repository. [OpenAI local skill loading](https://learn.chatgpt.com/docs/build-skills)

Installed OpenAI plug-ins add their skills to new chats. A published skill imported from an MCP server is a snapshot. ChatGPT and Codex do not fetch that skill from the MCP server at run time. [OpenAI skill construction](https://developers.openai.com/plugins/build/skills)

### Local commands and MCP

The ChatGPT desktop app for Windows supports plug-ins and skills. Its Windows-native Codex agent runs commands in PowerShell. This gives a local skill a documented command environment in which it can call `aiq.exe`. [ChatGPT desktop app for Windows](https://learn.chatgpt.com/docs/windows/windows-app)

Installing a plug-in on the web does not deploy local hook scripts. A capability that needs software on the user's computer is therefore surface-specific. It must be marked for desktop use and must check that its local dependency is present. [OpenAI plug-in architecture](https://developers.openai.com/plugins/concepts/plugins)

OpenAI permits a skills-only public plug-in. A public MCP submission must use a stable public HTTPS endpoint. If an MCP server runs locally and cannot be deployed at a public HTTPS URL, OpenAI tells the developer to contact OpenAI for local MCP support. Secure MCP Tunnel is for development tests and does not replace the public endpoint required for submission. [OpenAI plug-in submission](https://developers.openai.com/plugins/deploy/submission) and [OpenAI plug-in testing](https://developers.openai.com/plugins/deploy/connect-chatgpt)

### Starting and resuming sessions

Codex CLI starts in a selected working directory and can return to a saved chat with `codex resume`. This makes a per-run AIQ session directory a valid local project boundary. [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)

Codex App Server is OpenAI's interface for a custom product integration. It includes authentication, conversation history, approvals, and streamed agent events. Its default transport is JSONL over standard input and output. Its WebSocket transport is experimental and unsupported. App Server has `thread/start` and `thread/resume`, and it returns the instruction sources loaded for a thread. [Codex App Server](https://learn.chatgpt.com/docs/app-server)

### Account and token boundary

Codex supports two user sign-in paths for OpenAI models:

- ChatGPT sign-in for subscription access;
- an API key for usage-based access.

The ChatGPT desktop app and Codex CLI support both methods for local work. API-key use is billed through the user's OpenAI Platform account at standard API rates. [OpenAI authentication](https://learn.chatgpt.com/docs/auth)

With managed ChatGPT sign-in, Codex owns the OAuth flow, stores the tokens, and refreshes them. App Server can start this browser or device-code flow. It can also read the account type and ChatGPT rate limits. [Codex App Server authentication](https://learn.chatgpt.com/docs/app-server)

AIQ Studio does not need to receive an OpenAI token. It can start the official Codex client or App Server and let that process use its own credential store.

## Verified OpenCode facts

### Plug-in and extension surfaces

An OpenCode plug-in is a JavaScript or TypeScript module. It can subscribe to application, session, permission, shell, and tool events. It can also add custom tools. The plug-in receives an SDK client and Bun's shell interface. [OpenCode plug-ins](https://opencode.ai/docs/plugins/)

OpenCode loads plug-ins in two ways:

- JavaScript or TypeScript files in a project or global plug-in folder;
- npm packages named in `opencode.json`.

The `opencode plugin <module>` command installs a plug-in and updates configuration. Its `--global` option installs it in global configuration. OpenCode installs configured npm plug-ins with Bun at startup and stores them in its package cache. [OpenCode plug-ins](https://opencode.ai/docs/plugins/) and [OpenCode CLI](https://opencode.ai/docs/cli/)

The official documentation links to an ecosystem list, but it does not describe a reviewed public store that is equivalent to the OpenAI universal directory.

### Skill loading

OpenCode loads skills on demand through its native `skill` tool. It discovers skills in project and global locations for `.opencode/skills`, `.claude/skills`, and `.agents/skills`. For project skills, it searches from the current working directory up to the Git worktree root. [OpenCode agent skills](https://opencode.ai/docs/skills)

OpenCode's plug-in documentation does not define a plug-in manifest field for bundled skills. Its npm plug-in installation instructions only describe a JavaScript or TypeScript plug-in module. This is an important packaging gap for AIQ Studio.

### Local commands and MCP

OpenCode has a built-in shell tool. A custom TypeScript or JavaScript tool can also invoke a script in another language. An OpenCode plug-in can add such a tool. These surfaces can call `aiq.exe` without MCP. [OpenCode custom tools](https://opencode.ai/docs/custom-tools/) and [OpenCode plug-ins](https://opencode.ai/docs/plugins/)

OpenCode also supports local MCP servers. A local MCP configuration starts a command and can set its working directory and environment. OpenCode warns that MCP tool descriptions consume model context and recommends that users enable only the servers that they need. [OpenCode MCP servers](https://opencode.ai/docs/mcp-servers/)

### Starting and resuming sessions

`opencode <project>` starts the terminal interface for a project. It accepts an initial `--prompt`. It also accepts `--continue`, `--session`, and `--fork`. The `opencode run` command gives programmatic, noninteractive access and can continue a named session. [OpenCode CLI](https://opencode.ai/docs/cli/)

OpenCode also has a local HTTP server and a JS/TS SDK. The server binds to `127.0.0.1` by default. It can create and inspect sessions, send messages, and stream events. Its TUI endpoints can append and submit a prompt. The server can use HTTP Basic authentication. [OpenCode server](https://opencode.ai/docs/server/) and [OpenCode SDK](https://opencode.ai/docs/sdk/)

### Account and token boundary

OpenCode stores provider credentials in its own user data folder. Its official provider instructions offer an OpenAI API-key path and a browser sign-in path labelled ChatGPT Plus/Pro. [OpenCode providers](https://opencode.ai/docs/providers/)

This OpenCode statement is not an OpenAI statement. The OpenAI documentation reviewed for this report documents ChatGPT subscription access for official Codex clients and App Server. It does not document third-party OpenCode use of ChatGPT subscription credentials. AIQ Studio must not promise this entitlement until OpenAI confirms it for this use.

AIQ Studio must not read or copy the OpenCode credential file. It must start OpenCode and let OpenCode manage provider login.

## Design inferences

The following points are recommendations. They are not direct platform guarantees.

### Keep the workflow in the Rhino package

The full Rhino workflow should ship with the Rhino plug-in. When a user starts a workflow, Rhino should copy an immutable workflow snapshot into an AIQ session directory.

```text
AIQ session
|-- session.json
|-- skills.lock.json
|-- .agents/skills/
|   |-- aiq-studio/
|   `-- rhino-site-data-model/
|-- inputs/
|-- outputs/
`-- logs/
```

Both Codex and OpenCode can discover `.agents/skills` from the session working directory. This gives both harnesses the same frozen workflow content. It also keeps the real workflow version under AIQ Studio control.

### Make the harness skill a small router and menu

The public OpenAI plug-in can contain an `aiq-studio` router skill. The OpenCode npm plug-in should contain a matching custom tool, while the Rhino launcher puts the router skill into the session folder.

The router should:

1. Call `aiq status --json`.
2. Find the active Rhino session.
3. Call `aiq workflow list --json`.
4. Show the user a short workflow menu.
5. Load the selected host-owned skill.
6. Explain how to install or open Rhino when no host is available.

This is more reliable than a skill that points to a fixed folder inside another installed plug-in.

### Use a command adapter, not MCP, for Rhino control

`aiq.exe` should expose a small command set with JSON input and output. It should connect to the Rhino plug-in through a per-user local channel such as a Windows named pipe. Each AIQ session should have a short-lived capability token.

This design has these benefits:

- OpenAI Codex can call it through local PowerShell.
- OpenCode can call it through its shell tool or a typed custom tool.
- No public network service is necessary.
- AIQ can test the commands without a model.
- MCP metadata does not consume agent context.
- The Rhino plug-in can approve each document-changing operation.

MCP can be a later adapter over the same command contract. It must not own the workflow logic.

### Use two launch implementations

For OpenCode, the Rhino **Ask AI** button can start OpenCode in the AIQ session directory with an initial prompt. A later version can use the local OpenCode server to create a session and then drive or attach its TUI.

For OpenAI, there are two documented technical paths:

- start Codex CLI in the AIQ session directory;
- use Codex App Server and provide an AIQ-controlled conversation window.

The first path preserves the user's normal Codex client, but the terminal interface is less suitable for a nontechnical user. The second path gives AIQ more control over the experience, but it requires AIQ to build part of the harness UI.

The official OpenAI documentation reviewed for this report does not document a public deep link that opens the ChatGPT desktop app in a new Codex thread with a chosen local directory and prompt. This is an absence in the reviewed documents, not proof that no private or future interface exists.

## Best first-release route

### OpenAI

1. Publish a skills-only AIQ Studio plug-in in the OpenAI directory.
2. Mark local Rhino operations as desktop-only behavior.
3. Put branding, the router skill, installation checks, and help in that plug-in.
4. Keep the two complete Rhino workflow skills in the Rhino plug-in and snapshot them into each AIQ session.
5. For the first tracer, launch Codex CLI in that session directory.
6. If the terminal experience fails the nontechnical-user test, use Codex App Server with a very small AIQ conversation window.
7. Let Codex own ChatGPT login, API-key login, and credential storage.

Do not include a local MCP server in the public OpenAI submission for the first release.

### OpenCode

1. Publish an AIQ Studio npm plug-in.
2. Install it with `opencode plugin <module> --global` from the Rhino onboarding flow, after user confirmation.
3. Let the plug-in add a typed AIQ tool and session hooks.
4. Put the router and complete workflow skills into the AIQ session `.agents/skills` folder.
5. Start OpenCode in that folder with the router prompt.
6. Record the OpenCode session ID against the AIQ session ID. Use `--session` to resume it.
7. Let OpenCode own model-provider login and credentials.

### User entry from the harness

The OpenAI router skill and OpenCode adapter must also support users who start in the harness. They should call `aiq status`. If the Rhino plug-in is absent, they should show the official AIQ Studio installation route. If Rhino is closed, they should ask the user to open it. If a Rhino session is active, they should show the workflow menu.

## Prototype questions

Resolve these questions before the implementation map fixes the adapter design.

### Must resolve for the tracer

1. Can Rhino start Codex CLI on native Windows with an initial prompt, a selected AIQ session directory, and the installed OpenAI plug-in skill enabled?
2. How will Rhino get and store the new Codex thread ID when the CLI owns the visible session?
3. Does ChatGPT desktop have a supported URI or automation interface for a new local Codex thread? If it does not, is a terminal acceptable for the first public release?
4. Will OpenAI review accept a skills-only plug-in whose local workflow calls an independently installed `aiq.exe`?
5. Can a native Windows OpenCode process use the required Rhino named pipe without WSL path or permission problems?
6. Can the OpenCode npm plug-in report `session.created` and write a safe AIQ-to-OpenCode session mapping?
7. What exact OpenCode installation method will remove the adapter as well as install it? The current CLI page documents plug-in installation but does not show a plug-in removal command.

### Must resolve for account claims

8. Does OpenAI authorize the ChatGPT Plus/Pro login path that OpenCode documents? Get a current, written answer before marketing it as subscription access.
9. Which fallback providers will AIQ list in OpenCode if that login path is unavailable? The safe fallback is a provider account or API key owned by the user.

### Must resolve for safety and usability

10. Which `aiq.exe` commands are read-only, which change the Rhino document, and which always need user approval?
11. How does the named-pipe handshake prevent another local process from controlling the active Rhino document?
12. How does one Rhino process distinguish simultaneous AIQ sessions and harness processes?
13. Do Codex and OpenCode reliably discover a new session skill before the first prompt, or must the launcher restart the harness?
14. What message does the user see when a skill version and Rhino plug-in version are incompatible?
15. Can a new user install the harness adapter, sign in, start **Ask AI**, select a workflow, approve a Rhino action, close the harness, and resume the same session without developer help?

## Decision summary

The evidence supports the current AIQ Studio direction with one correction: “OpenAI plug-in” and “OpenCode plug-in” are not equivalent packages.

- The OpenAI package can natively distribute the router skill and provide public discovery.
- The OpenCode package can natively distribute code, hooks, and tools through npm, but the session launcher must distribute the skill files.
- The real Rhino workflows belong to the Rhino plug-in and the versioned AIQ session.
- `aiq.exe` is the stable local adapter.
- A private local protocol connects `aiq.exe` to Rhino.
- MCP stays optional.
- The user's chosen harness owns model authentication and token cost.
- AIQ Studio owns the workflow identity, workflow version, Rhino actions, approvals, reports, and user-facing branding.
