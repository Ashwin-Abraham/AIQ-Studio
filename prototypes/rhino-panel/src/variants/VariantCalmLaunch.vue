<template>
  <section class="panel panel--calm">
    <header class="header">
      <div class="brand">
        <svg viewBox="0 0 40 40" aria-hidden="true">
          <path d="M7 33V7h26v26H20V18h13M7 33h13" />
        </svg>
        <span>AIQ<span class="divider">/</span><b>STUDIO</b></span>
      </div>
      <span class="rhino-label">RHINO</span>
    </header>

    <div class="status-line" :class="`status-line--${statusTone}`">
      <span class="status-dot" />
      <span>{{ statusLabel }}</span>
    </div>

    <main class="body">
      <section class="launch-card">
        <p class="eyebrow">DESIGN WITH YOUR AI APP</p>
        <h1>Continue your Rhino work with AI.</h1>
        <p class="intro">Open Codex or OpenCode. Choose an AIQ Studio workflow there.</p>
        <button class="ask-button" type="button" :disabled="askDisabled">{{ askLabel }}</button>
        <p class="destination">Your conversation stays in the graphical AI app.</p>
      </section>

      <section v-if="panelState === 'missing'" class="notice notice--warning">
        <b>Companion plug-in not found</b>
        <p>Install AIQ Studio in Codex or OpenCode, then check again.</p>
        <a href="#install">Open installation guide</a>
      </section>

      <section v-else-if="panelState === 'starting'" class="notice">
        <span class="spinner" aria-hidden="true" />
        <div><b>Opening Codex</b><p>This can take a few seconds.</p></div>
      </section>

      <section v-else-if="panelState === 'active'" class="notice notice--success">
        <b>Session active in Codex</b>
        <p>Return to Codex for the conversation. Keep Rhino open.</p>
        <button class="text-button" type="button">Show session folder</button>
      </section>

      <section v-else-if="panelState === 'approval'" class="notice notice--approval">
        <p class="eyebrow">APPROVAL REQUIRED</p>
        <b>Add 14 building outlines?</b>
        <p>The new objects will go on AIQ Studio layers. You can undo this change.</p>
        <div class="button-pair"><button type="button">Approve</button><button type="button">Reject</button></div>
      </section>

      <section v-else-if="panelState === 'error'" class="notice notice--error">
        <b>Codex did not open</b>
        <p>Check that Codex is installed and signed in.</p>
        <div class="button-pair"><button type="button">Try again</button><a href="#help">Get help</a></div>
      </section>

      <section class="workflows" aria-label="Available workflows">
        <div class="section-heading"><h2>Available workflows</h2><span>2 installed</span></div>
        <div class="workflow"><span class="workflow-icon">S</span><div><b>Site Data Model</b><small>Buildings, terrain, roads, and context</small></div><span class="check">✓</span></div>
        <div class="workflow"><span class="workflow-icon">P</span><div><b>Plan Export</b><small>Editable Illustrator plan and preview</small></div><span class="check">✓</span></div>
      </section>
    </main>

    <footer><button type="button">Feedback &amp; requests</button><span>AIQ Studio · Rhino panel</span></footer>
  </section>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { PanelState } from '../models/PanelState'

export default defineComponent({
  name: 'VariantCalmLaunch',

  props: {
    panelState: {
      type: String as PropType<PanelState>,
      required: true,
    },
  },

  computed: {
    askDisabled(): boolean {
      return ['missing', 'starting', 'active', 'approval'].includes(this.panelState)
    },
    askLabel(): string {
      if (this.panelState === 'starting') return 'Opening Codex…'
      if (this.panelState === 'active' || this.panelState === 'approval') return 'AI session active'
      return 'Ask AI'
    },
    statusLabel(): string {
      return {
        missing: 'Set-up needed',
        ready: 'Ready to start',
        starting: 'Opening AI app',
        active: 'Connected to Codex',
        approval: 'Waiting for your approval',
        error: 'Action needed',
      }[this.panelState]
    },
    statusTone(): string {
      if (this.panelState === 'ready' || this.panelState === 'active') return 'success'
      if (this.panelState === 'missing' || this.panelState === 'approval') return 'warning'
      if (this.panelState === 'error') return 'error'
      return 'working'
    },
  },
})
</script>

<style scoped>
.panel { min-height: 680px; color: var(--primary-color); background: var(--page-background-color); }
.header { display: flex; align-items: center; justify-content: space-between; min-height: 66px; padding: 13px 18px; background: var(--off-white); border-bottom: 1px solid var(--header-border-color); }
.brand { display: flex; align-items: center; gap: 9px; font-size: 17px; font-weight: 700; letter-spacing: .06em; }
.brand svg { width: 27px; fill: none; stroke: currentColor; stroke-width: 2; }
.brand b { font-size: 11px; font-weight: 500; letter-spacing: .15em; }
.divider { margin: 0 7px; color: var(--brand-divider-color); font-weight: 400; }
.rhino-label { color: var(--muted-text-color); font-size: 9px; font-weight: 700; letter-spacing: .13em; }
.status-line { display: flex; align-items: center; gap: 7px; min-height: 31px; padding: 6px 18px; color: var(--muted-text-color); background: #ffffff80; border-bottom: 1px solid var(--header-border-color); font-size: 10px; }
.status-dot { width: 7px; height: 7px; background: var(--accent-color); border-radius: 50%; }
.status-line--success .status-dot { background: var(--success-color); }
.status-line--warning .status-dot { background: #c08122; }
.status-line--error .status-dot { background: var(--error-color); }
.body { display: grid; gap: 14px; padding: 18px; }
.launch-card { padding: 22px 18px 18px; text-align: center; background: var(--off-white); border: 1px solid var(--header-border-color); border-radius: var(--primary-radius); box-shadow: var(--panel-shadow); }
.eyebrow { margin: 0 0 8px; color: var(--accent-color); font-size: 9px; font-weight: 700; letter-spacing: .12em; }
h1 { max-width: 270px; margin: 0 auto 8px; font-size: 22px; line-height: 1.18; }
.intro { max-width: 260px; margin: 0 auto 17px; color: var(--dark-grey); font-size: 12px; line-height: 1.5; }
.ask-button { width: 100%; min-height: 48px; color: #fff; background: var(--primary-color); border: 1px solid var(--primary-color); border-radius: var(--secondary-radius); font-size: 14px; font-weight: 700; }
.ask-button:hover:not(:disabled) { background: var(--accent-color); }
.ask-button:disabled { background: #858b9a; border-color: #858b9a; }
.destination { margin: 9px 0 0; color: var(--muted-text-color); font-size: 9px; }
.notice { display: flex; align-items: flex-start; gap: 10px; padding: 12px; background: #f5f6fa; border: 1px solid var(--navigation-border-color); border-radius: var(--secondary-radius); font-size: 11px; line-height: 1.4; }
.notice p { margin: 3px 0 0; }
.notice a, .text-button { color: var(--accent-color); font-weight: 700; }
.notice--warning, .notice--approval { display: block; background: var(--warning-surface); border-color: #e5ca98; }
.notice--success { display: block; background: var(--success-surface); border-color: #a9cfb9; }
.notice--error { display: block; background: var(--error-surface); border-color: #e1aaaa; }
.spinner { flex: 0 0 auto; width: 17px; height: 17px; border: 2px solid var(--secondary-color); border-top-color: var(--accent-color); border-radius: 50%; }
.text-button { padding: 5px 0 0; background: transparent; border: 0; font-size: 10px; }
.button-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }
.button-pair button, .button-pair a { min-height: 33px; padding: 8px; color: var(--primary-color); background: #fff; border: 1px solid var(--navigation-border-color); border-radius: 6px; font-size: 10px; font-weight: 700; text-align: center; text-decoration: none; }
.workflows { padding-top: 2px; }
.section-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 7px; }
h2 { margin: 0; font-size: 11px; }
.section-heading span { color: var(--muted-text-color); font-size: 9px; }
.workflow { display: grid; grid-template-columns: 28px 1fr auto; align-items: center; gap: 9px; padding: 9px 8px; border-top: 1px solid var(--navigation-border-color); }
.workflow-icon { display: grid; place-items: center; width: 28px; height: 28px; color: #fff; background: var(--accent-color); border-radius: 7px; font-size: 10px; font-weight: 700; }
.workflow b, .workflow small { display: block; }
.workflow b { font-size: 11px; }
.workflow small { margin-top: 2px; color: var(--muted-text-color); font-size: 9px; }
.check { color: var(--success-color); font-size: 13px; }
footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 18px 16px; color: var(--muted-text-color); font-size: 8px; }
footer button { padding: 0; color: var(--accent-color); background: transparent; border: 0; font-size: 9px; }
</style>

