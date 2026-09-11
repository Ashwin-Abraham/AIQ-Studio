# Rhino Vue UI and plug-in distribution constraints

Research checked on 11 September 2026.

Issue: [AIQ Studio #15](https://github.com/Ashwin-Abraham/AIQ-Studio/issues/15)

## Research question

What technical limits affect an AIQ Studio plug-in for Rhino 8 that has a Vue and TypeScript panel, packaged workflow skills and assets, an **Ask AI** action, and a local connection to an external AI harness?

## Answer

The proposed product is feasible, with one important correction: it is a C# and RhinoCommon plug-in with a Vue user interface. Vue cannot replace the Rhino host layer. The C# layer must register commands and panels, access Rhino documents, control process lifetime, and apply all document changes.

Use this first technical shape:

```text
AIQ Studio Rhino plug-in (.rhp, C#/RhinoCommon, .NET 8)
├── Eto.Forms.WebView
│   └── compiled Vue 3 + TypeScript panel
├── host services
│   ├── document-specific state
│   ├── safe Rhino actions
│   ├── approval and undo boundaries
│   └── harness process/session control
└── packaged resources
    ├── workflow skills
    ├── scripts
    ├── references
    ├── templates
    └── compiled panel files
```

Use two different connections:

1. Use the Eto WebView message channel between Vue and C#.
2. Use a private process or local IPC connection between C# and the AI harness.

MCP can be an optional harness adapter. It does not need to be the main connection, and it must not contain workflow logic.

For the fastest first release, target current Rhino 8 on Windows. A practical initial minimum is Rhino 8.20 because current McNeel guidance says that Rhino 8.20 installs and uses .NET 8 by default. Confirm the exact minimum release in a prototype before the package manifest and Yak distribution tag become final. Treat macOS as a separate build and validation track, even if most C# source remains shared.

## Verified facts

### Rhino host and runtime

- RhinoCommon is McNeel's cross-platform .NET plug-in SDK for Rhino on Windows and macOS. RhinoCommon gives a plug-in access to Rhino, and Eto supplies cross-platform user-interface controls ([RhinoCommon overview](https://developer.rhino3d.com/guides/rhinocommon/what-is-rhinocommon/)).
- Rhino 8 introduced .NET Core on Windows and macOS. Current McNeel guidance recommends `net8.0` for Rhino 8 in .NET Core mode. Rhino 8.20 and later use .NET 8 by default. Windows still has a deprecated .NET Framework fallback. macOS uses .NET Core only ([moving to .NET Core](https://developer.rhino3d.com/guides/rhinocommon/moving-to-dotnet-core/)).
- A managed cross-platform plug-in must use `AnyCPU`. Native dependencies for Rhino 8 on macOS must support the required Intel and Apple Silicon architectures. McNeel recommends a Universal Binary when both architectures are in scope ([moving to .NET Core](https://developer.rhino3d.com/guides/rhinocommon/moving-to-dotnet-core/)).
- A plug-in will not load if it uses an API that is not in the user's installed Rhino version. The selected RhinoCommon NuGet version therefore sets a real minimum Rhino service release ([using NuGet](https://developer.rhino3d.com/en/guides/rhinocommon/using-nuget/)).
- Code that changes the Rhino document or user interface must run in the correct Rhino context. RhinoCommon supplies `RhinoApp.InvokeOnUiThread` for work that must return to the Rhino user-interface thread ([RhinoCommon API](https://developer.rhino3d.com/api/rhinocommon/rhino.rhinoapp/invokeonuithread)).
- Calling arbitrary Rhino command scripts from another plug-in command has special rules. McNeel warns that `RhinoApp.RunScript` can invalidate references to the runtime document database and can cause a crash when those references are reused ([running Rhino commands from a plug-in](https://developer.rhino3d.com/en/guides/rhinocommon/run-rhino-command-from-plugin/)).

### Vue and TypeScript in a Rhino panel

- Rhino plug-ins can add docked panels. Eto panels work on Windows and macOS. WinForms and WPF panels work only on Windows ([Rhino tabbed panels](https://developer.rhino3d.com/en/guides/rhinocommon/tabbed-panels/)).
- Eto has a `WebView` control that displays HTML and executes JavaScript. Its upstream API includes `LoadHtml`, `ExecuteScriptAsync`, and a `MessageReceived` event for calls to `window.eto.postMessage(string)` ([Eto WebView source](https://github.com/picoe/Eto/blob/1868ea986cab440bb22e471d977ceefcda2f2239/src/Eto/Forms/Controls/WebView.cs)).
- Eto's Windows implementation selects WebView2 by default and has a fallback path when it cannot create that handler ([Eto WPF platform source](https://github.com/picoe/Eto/blob/1868ea986cab440bb22e471d977ceefcda2f2239/src/Eto.Wpf/Platform.cs)). Eto has a separate WKWebView handler for macOS ([Eto macOS WebView source](https://github.com/picoe/Eto/blob/1868ea986cab440bb22e471d977ceefcda2f2239/src/Eto.Mac/Forms/Controls/WKWebViewHandler.cs)).
- McNeel has an experimental TypeScript WebView panel in its RhinoAI repository. The experiment loads one compiled HTML file as an embedded resource. It uses `window.eto.postMessage` from the page and `ExecuteScriptAsync` from C# ([panel design](https://github.com/mcneel/RhinoAI/blob/d06dd9ae9a9f7e8fb98ff95fe54eae8b08ce643c/rhino/panel/README.md), [C# panel bridge](https://github.com/mcneel/RhinoAI/blob/d06dd9ae9a9f7e8fb98ff95fe54eae8b08ce643c/rhino/plugin/WebPanel/PanelBridge.ai.cs), [compiled panel build](https://github.com/mcneel/RhinoAI/blob/d06dd9ae9a9f7e8fb98ff95fe54eae8b08ce643c/rhino/panel/build.mjs)). This is useful implementation evidence. It is not a stable Rhino 8 support contract.

Vue 3 is therefore feasible as the view layer. Build Vue, TypeScript, and CSS before packaging. Do not require Node.js, Vite, or a development server on the user's computer.

### Windows and macOS differences

| Area | Windows | macOS | Effect on AIQ Studio |
| --- | --- | --- | --- |
| Rhino 8 runtime | .NET Core, with a deprecated .NET Framework fallback | .NET Core only | Use .NET 8 for new work. Do not make the design depend on .NET Framework. |
| Panel technology | Eto, WPF, or WinForms | Eto or native macOS view | Use Eto for shared source. |
| Web engine | WebView2 by default in current Eto WPF | WKWebView | Test both engines. Do not assume equal browser behavior. |
| Panel lifetime | A per-document panel is created for each document and disposed when it closes | A panel instance can exist for each inspector panel that contains it | Keep state keyed by the Rhino document. Do not use one global panel state. |
| Rhino 8 hardware | 64-bit Intel or AMD; Windows ARM is not supported | Intel and Apple Silicon | Keep native helper builds and Yak distributions platform-specific. |
| Minimum operating system | Windows 10 in the current Rhino 8 system requirements | macOS 12.4 in the current Rhino 8 system requirements | Old WKWebView versions are a compatibility risk. |
| Signing | Authenticode applies to Windows executables and DLLs | Developer ID and notarization apply to software distributed outside the App Store | Sign each native helper separately. Do not assume that a Yak upload signs it. |

Rhino's current operating-system and processor limits are in the [Rhino 8 system requirements](https://www.rhino3d.com/8/system-requirements/). Rhino also documents that panel lifetime differs between Windows and macOS ([Rhino tabbed panels](https://developer.rhino3d.com/en/guides/rhinocommon/tabbed-panels/)).

The panel must not depend on browser features without a compatibility check. McNeel's experimental panel had to account for an older system WebKit on Rhino 8 for macOS. It also moved file selection into the native host because its macOS WKWebView did not supply a usable file picker ([RhinoAI panel notes](https://github.com/mcneel/RhinoAI/blob/d06dd9ae9a9f7e8fb98ff95fe54eae8b08ce643c/rhino/panel/README.md), [native attachment picker](https://github.com/mcneel/RhinoAI/blob/d06dd9ae9a9f7e8fb98ff95fe54eae8b08ce643c/rhino/plugin/WebPanel/AttachmentPicker.ai.cs)). AIQ Studio must test browser links, file selection, clipboard behavior, focus, keyboard shortcuts, scaling, and dark mode on both platforms.

### Skills, scripts, and other assets

- A `.yak` file is a ZIP archive. It must contain `manifest.yml` at its root. An `.rhp` plug-in must be at the package root or in a supported framework folder. A package can also contain other files and directories ([Yak package anatomy](https://developer.rhino3d.com/guides/yak/the-anatomy-of-a-package/)).
- Rhino's script-project documentation shows data files of any type in a `shared/` folder. These files are put in the Yak package and deployed with the plug-in. The installed location can be found from the plug-in ID with `PlugIn.PathFromId` ([Rhino shared resources](https://developer.rhino3d.com/en/guides/scripting/projects-create/#shared-resources)).
- Yak supports separate `win`, `mac`, and `any` distributions for one package version. Rhino only shows versions that have a compatible distribution ([Yak package anatomy](https://developer.rhino3d.com/guides/yak/the-anatomy-of-a-package/)).

These facts support this package layout:

```text
manifest.yml
net8.0/
  AIQStudio.rhp
  AIQStudio.dll
  ui/
    panel.html
  workflows/
    rhino-site-data-model/
      SKILL.md
      references/
      scripts/
    rhino-plan-export/
      SKILL.md
      references/
      scripts/
  templates/
  assets/
  helpers/
```

This layout is a recommendation. The prototype must confirm where Yak places each folder and how `PlugIn.PathFromId` resolves it. The plug-in must treat the installed package as read-only. It must copy a versioned workflow package to a user-writable AIQ session folder before an agent runs it.

Embed the initial Vue panel as one self-contained HTML resource, or load it with a verified base URI. A single embedded file reduces path, cache, and update failures. If the final Vue build keeps separate hashed files, the package test must confirm that CSS, JavaScript, fonts, and images load from the installed Yak location.

### External process launch

.NET can start an executable with `Process.Start`. Microsoft warns that untrusted launch data is a security risk. A started process also needs an explicit close and failure policy ([`Process.Start` API](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.start?view=net-8.0)).

The **Ask AI** implementation must:

- use an executable path from trusted configuration or from a verified discovery step;
- pass each argument as a separate argument, not as one shell command string;
- pass only a generated AIQ session path and a small fixed start instruction;
- support spaces and non-ASCII characters in paths;
- report when the harness is not installed;
- detect an early process exit;
- define whether Rhino owns and closes the child process; and
- prevent model or prompt text from becoming executable command text.

McNeel's current RhinoAI source is useful precedent. It resolves AI command-line programs, uses `ProcessStartInfo.ArgumentList`, communicates through process standard input and output, and closes the process tree when it owns the session ([CLI process source](https://github.com/mcneel/RhinoAI/blob/8f625a2fd062ac18df5579195b2062e56bc7f7ef/rhino/plugin/Agents/CliProcess.cs), [process transport source](https://github.com/mcneel/RhinoAI/blob/8f625a2fd062ac18df5579195b2062e56bc7f7ef/rhino/plugin/Agents/ProcessStdioTransport.cs)). This is a precedent, not a requirement to use RhinoAI or MCP.

The exact command that starts or attaches to OpenAI Codex and OpenCode is outside this Rhino research. Each harness adapter must prove that behavior against its own supported interface.

### Local IPC choices

No one transport solves both connections.

| Connection | Recommended transport | Reason |
| --- | --- | --- |
| Vue panel to Rhino plug-in | Eto `window.eto.postMessage` and `ExecuteScriptAsync` | It is private to the panel and needs no port or server. |
| Rhino plug-in to a child process that it owns | Standard input/output | Process lifetime and one-session routing are simple. |
| Separate `aiq` helper to a running Rhino process | Named pipe on Windows; select and test the macOS equivalent | It supports duplex local IPC without a listening TCP port. |
| Browser development panel to a mock host | Loopback HTTP or WebSocket | It is easy to inspect during development. Do not make it the default production path without authentication and origin controls. |
| Harness that only supports MCP | Thin optional MCP adapter | It can translate MCP calls into the same safe AIQ host operations. |

.NET supports duplex named-pipe clients and servers ([Microsoft named-pipe guidance](https://learn.microsoft.com/en-us/dotnet/standard/io/how-to-use-named-pipes-for-network-interprocess-communication)). The choice of pipe names, access control, discovery, reconnect rules, and multi-Rhino routing is still an AIQ design decision.

The local contract must expose a small allowlist of typed AIQ operations. It must not expose unrestricted Python, C#, shell commands, or `RhinoApp.RunScript`. The skill owns workflow reasoning. C# owns safe host actions and document validation.

### Yak publication, installation, and updates

- Rhino Package Manager gives users in-Rhino search, installation, removal, and update functions. Installed packages update automatically when new versions are available ([Rhino Package Manager help](https://docs.mcneel.com/rhino/8/help/en-us/commands/packagemanager.htm)).
- A new Yak package is loaded on the next Rhino start. Yak controls the installation folder structure ([installing and managing packages](https://developer.rhino3d.com/en/guides/yak/installing-and-managing-packages/)).
- A publisher must authorize Yak with a Rhino Account. The first publisher owns the package name. A published version cannot be overwritten. A bad version can be yanked, but its version number cannot be reused ([pushing a package](https://developer.rhino3d.com/en/guides/yak/pushing-a-package-to-the-server/), [Yak CLI reference](https://developer.rhino3d.com/en/guides/yak/yak-cli-reference/)).
- The manifest requires a name, version, authors, and description. It can also contain a URL, search keywords, and a packaged icon. These fields give AIQ Studio a clear identity in Rhino Package Manager ([Yak manifest](https://developer.rhino3d.com/en/guides/yak/the-package-manifest/)).
- McNeel supplies a test Yak server. It is cleared each night. Use it for installation tests before the public push ([pushing a package](https://developer.rhino3d.com/en/guides/yak/pushing-a-package-to-the-server/)).

The reviewed Yak documentation does not define a general signing step for the `.yak` archive. McNeel documents a separate plug-in signing process when a plug-in uses LAN Zoo licensing ([LAN Zoo plug-in signing](https://developer.rhino3d.com/en/guides/rhinocommon/digitally-signing-plugins-for-zoo/)). Do not treat Yak publisher authentication as executable code signing.

For public Windows distribution, sign the `.rhp`, supporting DLLs, and any helper `.exe` with a trusted Authenticode certificate. Microsoft states that unsigned software can receive a strong SmartScreen block ([Windows code-signing options](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options)). For a later macOS package, test Developer ID signing and notarization for the plug-in bundle and each helper. Apple states that macOS checks plug-ins distributed outside the App Store and normally requires notarization under default Gatekeeper settings ([Apple Gatekeeper guidance](https://support.apple.com/en-ug/102445)).

An automatic Yak update must not change an active AIQ workflow in place. A session must keep a copied workflow version and a lock file. The new plug-in version can apply when Rhino restarts or when the user creates a new session.

## AIQ Resi UI guidance

The local AIQ Resi UI repository is a suitable style and code reference. These observations use commit [`f6f6927`](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/tree/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c).

- Its Vue standard selects Vue 3 with the Options API. It requires typed props, declared emits, pure computed state, service-owned domain logic, stable list keys, ESLint, type checking, and relevant tests ([Vue coding standard](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/blob/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c/VUE_CODING_STANDARDS.md)).
- It keeps component CSS scoped and keeps shared colors and sizes in CSS custom properties ([README](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/blob/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c/README.md), [design tokens](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/blob/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c/src/styles/Variables.css)).
- Its main palette uses `#333c55`, `#58629e`, `#d1d6e3`, and light neutral surfaces. AIQ Studio can reuse these as brand tokens. The Rhino panel must also read Rhino theme colors so that text, fields, and base surfaces remain clear in light and dark modes. McNeel's experimental panel shows one way to convert Rhino colors into CSS custom properties ([RhinoAI theme adapter](https://github.com/mcneel/RhinoAI/blob/d06dd9ae9a9f7e8fb98ff95fe54eae8b08ce643c/rhino/plugin/WebPanel/PanelTheme.ai.cs)).
- The feedback action keeps its HTTPS destination in configuration, validates the URL, opens it in a new browser context, removes the opener reference, and shows a small error when opening fails ([feedback component](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/blob/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c/src/components/FeedbackAction.vue), [feedback service](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/blob/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c/src/services/feedback/openFeedback.ts), [feedback configuration](https://github.com/Ashwin-Abraham/AIQ-Resi-UI/blob/f6f69275b4a342a97aa682e1974fa77b7f4c0f0c/src/config/feedback.ts)).

Copy the visible feedback pattern, the test seam, and the error behavior. Adapt the implementation for the Rhino WebView: Vue should send a typed `open-external-url` command to C#. C# must allow only the configured HTTPS feedback origin and then open the user's default browser. Do not depend on WebView popup behavior.

When the Vue project is created, copy `VUE_CODING_STANDARDS.md` into that project and state that AIQ Studio-specific rules take priority. Keep the detailed palette and component references in UI guidance, not in the domain glossary.

## Recommended first-release constraints

1. Support Rhino 8 on Windows first.
2. Select and document one minimum Rhino 8 service release after the WebView prototype. Prefer Rhino 8.20 or later if no user need requires an older release.
3. Use C#, RhinoCommon, .NET 8, and an Eto per-document panel.
4. Compile Vue 3 and TypeScript into static production assets. Package no Node.js runtime.
5. Use an embedded, self-contained HTML file for the first panel.
6. Use typed WebView messages for all Vue-to-C# actions.
7. Keep all Rhino mutations in named C# operations on the Rhino user-interface thread.
8. Package both existing workflow skills and their references, scripts, templates, and notices.
9. Copy the selected workflow package into a versioned user-writable session folder before use.
10. Start the selected AI harness from **Ask AI** with trusted process configuration and structured arguments.
11. Prefer owned-process standard input/output for the first tracer. Add a named-pipe helper only if process ownership or harness limits require it.
12. Keep MCP as an optional adapter for harnesses that require it.
13. Build a `rh8_<minimum>-win` Yak distribution. Use the Yak test server before the public version.
14. Sign native Windows binaries before public distribution.
15. Do not label the package `any` until a macOS build passes the full acceptance suite.

## Prototype questions

These questions do not have a reliable answer from documentation alone.

### Rhino and WebView

1. Which minimum Rhino 8 service release includes the required Eto `MessageReceived`, `ExecuteScriptAsync`, and WebView2 behavior?
2. Can a packaged Vue page send a typed command to C#, and can C# return state without message loss during page load or reload?
3. Do embedded or installed assets load correctly when paths contain spaces and non-ASCII characters?
4. What clear error must appear when WebView2 is missing or Eto uses a fallback engine?
5. Does the panel keep the correct state with two open Rhino documents, panel close and reopen, document close, and Rhino restart?
6. Do keyboard shortcuts, focus, scaling, dark mode, clipboard access, external links, and file selection work on the selected Windows versions?

### Harness process and IPC

7. Can **Ask AI** start a new Codex and OpenCode session in the generated AIQ session folder through a documented interface?
8. Can the plug-in distinguish a new session from activation of an existing harness process?
9. Does standard input/output support all required agent events, user questions, cancellation, and resume behavior?
10. If a separate helper is required, can a named-pipe connection enforce current-user access and route two concurrent Rhino sessions correctly?
11. What happens when Rhino closes, the harness closes, the helper crashes, the user cancels, or a reply arrives after its document closes?
12. Can a plug-in update leave an active session and child process on the old locked workflow version until completion?

### Yak and signing

13. Does the built Yak package contain every workflow file and preserve executable permissions where required?
14. Does a clean machine install load the plug-in only after the documented Rhino restart and then show the correct panel, icon, and commands?
15. Does Windows trust the signed `.rhp`, DLLs, and helper executable after download through Package Manager?
16. Which files does a future macOS distribution require to be signed and notarized, and how does Yak preserve those signatures?

### macOS follow-up

17. Does the same compiled Vue panel work in Rhino 8's WKWebView on the oldest supported macOS version?
18. Must the macOS helper be Universal Binary, or can the first macOS release require Apple Silicon?
19. What process launch method reliably starts each supported harness on macOS?
20. Which local IPC transport has the simplest secure behavior on macOS?

## Acceptance test for the Rhino tracer

The Rhino tracer is successful when a clean Windows user can:

1. Install a prerelease Yak package from the test source.
2. Restart Rhino and open the AIQ Studio panel.
3. Select **Ask AI**.
4. Start a supported harness in a generated AIQ session folder.
5. See both packaged workflow choices.
6. Start the Rhino Site Data Model workflow.
7. Send one read request from the agent to Rhino.
8. Preview and approve one harmless document change.
9. Receive the structured result in the agent session.
10. Cancel or close the session without an orphan helper process.
11. Submit feedback through the configured external HTTPS form.
12. Open a second Rhino document without state leaking from the first document.

Do not start public Yak publication or macOS distribution until this tracer fixes the minimum Rhino version, process ownership, session routing, update behavior, and signing plan.
