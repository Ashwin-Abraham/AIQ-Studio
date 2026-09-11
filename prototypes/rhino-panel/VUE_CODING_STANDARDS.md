# Vue Coding Standards

This project uses Vue 3 with the Options API.

## Sources of truth

Apply these sources in this priority order:

1. Existing patterns in this repository.
2. The [Vue official Style Guide](https://vuejs.org/style-guide/).
3. The [Vue official Guide](https://vuejs.org/guide/), with Options API examples.
4. The [eslint-plugin-vue recommended rules](https://eslint.vuejs.org/rules/).

If two sources conflict, use the source with the higher priority.

## Component API

- Use the Options API. Do not migrate components to the Composition API unless the change request requires it.
- Use multi-word PascalCase names for components and component files.
- Declare props with object syntax. Include types, default values, and validators where they are applicable.
- Do not mutate props.
- Declare all emitted events with the `emits` option.

## State and behavior

- Put derived state in pure computed properties.
- Use watchers only for side effects.
- Keep API and domain logic in services. Do not duplicate this logic in components.

## Templates

- Keep complex expressions out of templates. Move them to computed properties or methods.
- Use stable, domain-specific `:key` values with `v-for`. Do not use array indexes as keys.
- Do not put `v-if` and `v-for` on the same element.

## Type organization

- Put each exported interface, type, or data-only class in its own file.
- Put feature-owned model files in the feature's `models` directory.
- Keep behavioural classes and implementation files in the feature root.
- Keep a type beside its implementation without exporting it when only that file uses it.

## Repository conventions

- Preserve the existing formatting and naming conventions.
- Prefer an established repository pattern when it is more specific than these general rules.
- Keep each change focused. Do not include unrelated component migrations or refactoring.

## Required checks

Before a change is complete, it must pass:

- ESLint.
- Type checking.
- All relevant tests.

## AIQ Studio prototype additions

- Keep the panel useful at a width of 320 pixels.
- Use Rhino theme values when production work starts.
- Send external-link requests to the native Rhino host. Do not use WebView pop-ups in production.
- Keep AI conversation and workflow selection in Codex or OpenCode.
- Do not show implementation helper names to users.

