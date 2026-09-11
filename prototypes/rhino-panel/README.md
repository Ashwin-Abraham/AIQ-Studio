# AIQ Studio Rhino Panel Prototype

This is a throwaway UI prototype. It answers this question:

> Which simple-launcher layout gives a nontechnical Rhino user the clearest path to **Ask AI**, while Codex or OpenCode owns the conversation and workflow choice?

The route has three visual variants. Use the floating prototype control to change the variant and the representative product state.

## Run

Install the dependencies once:

```powershell
npm install
```

Start the prototype:

```powershell
npm run prototype
```

Open the local URL that Vite prints. You can also open a specific variant:

- `?variant=A` — Calm launch
- `?variant=B` — Docked control
- `?variant=C` — Guided launch

Add `&state=` to open a representative state directly. The values are `missing`, `ready`,
`starting`, `active`, `approval`, and `error`.

This prototype has no Rhino or AI harness connection. Its controls only change local memory.
