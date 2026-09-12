# AIQ Studio Context Map

## Contexts

- [Site Model](./CONTEXT.md): defines reusable site-model work and its outputs.
- [Product Distribution](./docs/product/CONTEXT.md): defines how AIQ Studio workflows reach users through AEC host applications and AI harnesses.

## Relationships

- **Product Distribution → Site Model**: Product Distribution packages and presents the workflows that create a Rhino Site Model and Site Data Report.
- **Host Plug-in → AIQ Session**: A Host Plug-in is the sole authority that creates an AIQ Session for its Host Application.
- **AIQ Session → Workflow Package**: Each AIQ Session applies one Workflow Package.
- **Harness Conversation ↔ AIQ Session**: A Harness Conversation can start before an AIQ Session exists. An AIQ Session can continue in a later Harness Conversation.
