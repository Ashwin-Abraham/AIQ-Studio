# AIQ Studio Product Distribution Context

This glossary defines the product terms for distributing AIQ Studio workflows through AEC applications and AI harnesses.

## Language

**AIQ Studio**:
The user-facing name for each AIQ Studio plug-in, independent of the application in which it appears. Host names can be added internally when several plug-ins must be distinguished.
_Avoid_: AIQ Studio for Rhino or AIQ Studio for OpenAI in user-facing copy

**Host Application**:
An AEC application in which AIQ Studio can inspect or change project work, such as Rhino.
_Avoid_: Host when the application itself is meant

**AI Harness**:
An application that supplies an AI agent which can load and run AIQ Studio workflows, such as Codex or OpenCode.
_Avoid_: Model, provider, chatbot

**Host Plug-in**:
The AIQ Studio plug-in installed in a Host Application. It owns the applicable Workflow Packages and is the sole authority that creates AIQ Sessions for that Host Application.
_Avoid_: Rhino plug-in when referring to the general product role

**Harness Plug-in**:
The AIQ Studio plug-in installed in an AI Harness. It finds an applicable Host Plug-in and helps a Harness Conversation select and load a Workflow Package.
_Avoid_: AI plug-in, model plug-in

**Harness Conversation**:
A conversation in an AI Harness in which a user selects or uses an AIQ Studio workflow. It can start before an AIQ Session exists, and a later Harness Conversation can continue an existing AIQ Session.
_Avoid_: AIQ Session, chat session

**Workflow Package**:
A complete, immutable, versioned set of agent instructions, references, scripts, and assets for one AIQ Studio workflow. Each AIQ Session applies one Workflow Package.
_Avoid_: Skill when the complete distributable set is meant

**Session Runner**:
A small, versioned set of host-owned instructions that tells an AI Harness how to use a Workflow Package in an AIQ Session. It contains no workflow-specific behavior.
_Avoid_: Workflow Package, launcher skill

**AIQ Session**:
The persistent local record for one use of one Workflow Package with work in a Host Application. It can continue across more than one Harness Conversation.
_Avoid_: Harness Conversation, chat, model session

**Ask AI**:
The user action in a Host Plug-in that opens a Harness Conversation for workflow selection or resumes a Harness Conversation for an existing AIQ Session. A new AIQ Session starts only after the user selects a workflow.
_Avoid_: Run workflow
