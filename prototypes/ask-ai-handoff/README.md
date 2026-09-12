# Ask AI handoff prototype

This is a throwaway prototype. It answers one question:

> Can **Ask AI** open a graphical Codex or OpenCode draft for a known folder and prompt?

The script creates an empty `AIQ-ASK-AI-LAUNCH-TEST` folder beside itself. By default, it only
prints the encoded desktop links:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\prototypes\ask-ai-handoff\Invoke-AskAiHandoffPrototype.ps1
```

To test Codex, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\prototypes\ask-ai-handoff\Invoke-AskAiHandoffPrototype.ps1 -Execute Codex
```

To test OpenCode, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\prototypes\ask-ai-handoff\Invoke-AskAiHandoffPrototype.ps1 -Execute OpenCode
```

For each test, the desktop app must show the test folder and put this text in the composer:

> Open AIQ Studio and show me the available Rhino workflows.

The app must not submit the prompt. Do not press **Send** during this test.

The intended MVP result is a graphical handoff with an unsent draft. The Harness Plug-in shows
the workflow menu after the user sends the draft. The Host Plug-in creates an AIQ Session only
after the user selects a workflow.
