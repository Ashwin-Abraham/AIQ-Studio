<template>
  <section class="panel panel--docked">
    <header>
      <div><span class="product">AIQ STUDIO</span><span class="surface">RHINO PANEL</span></div>
      <span class="status-chip" :class="`status-chip--${statusTone}`">{{ statusLabel }}</span>
    </header>

    <main>
      <section class="workspace-summary">
        <p class="eyebrow">CURRENT RHINO FILE</p>
        <h1>Riverside Quarter.3dm</h1>
        <p>Changes need your approval before AIQ Studio adds them to this file.</p>
      </section>

      <section v-if="panelState === 'missing'" class="event event--warning">
        <span class="event-number">!</span><div><b>Install the companion plug-in</b><p>AIQ Studio was not found in Codex or OpenCode.</p><a href="#install">View installation steps →</a></div>
      </section>
      <section v-else-if="panelState === 'starting'" class="event event--working">
        <span class="event-number">···</span><div><b>Opening your AI app</b><p>A new AIQ Studio project is being prepared.</p></div>
      </section>
      <section v-else-if="panelState === 'active'" class="event event--success">
        <span class="event-number">✓</span><div><b>Codex session is active</b><p>Continue the conversation in Codex.</p><button type="button">Show session details</button></div>
      </section>
      <section v-else-if="panelState === 'approval'" class="approval">
        <div class="approval-heading"><span>APPROVAL</span><b>Site Data Model</b></div>
        <h2>Add site context to Rhino?</h2>
        <dl><div><dt>New objects</dt><dd>14 buildings</dd></div><div><dt>Target</dt><dd>AIQ Studio layers</dd></div><div><dt>Undo</dt><dd>Available</dd></div></dl>
        <div class="button-pair"><button class="approve" type="button">Approve change</button><button type="button">Reject</button></div>
      </section>
      <section v-else-if="panelState === 'error'" class="event event--error">
        <span class="event-number">!</span><div><b>Connection stopped</b><p>Your Rhino file was not changed.</p><button type="button">Reconnect</button><a href="#help">Get help</a></div>
      </section>
      <section v-else class="event event--neutral">
        <span class="event-number">✓</span><div><b>{{ panelState === 'ready' ? 'Ready for a new session' : 'AIQ Studio is ready' }}</b><p>Open your graphical AI app when you are ready.</p></div>
      </section>

      <section class="workflow-strip">
        <p class="eyebrow">INSTALLED WORKFLOWS</p>
        <div class="workflow-tags"><span>Site Data Model</span><span>Plan Export</span></div>
      </section>

      <a class="feedback" href="#feedback">Feedback &amp; requests ↗</a>
    </main>

    <section class="launch-dock">
      <div><b>Work with AIQ Studio</b><span>Workflow choice opens in Codex or OpenCode.</span></div>
      <button type="button" :disabled="askDisabled">{{ askLabel }} <span>↗</span></button>
    </section>
  </section>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { PanelState } from '../models/PanelState'

export default defineComponent({
  name: 'VariantDockedControl',

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
      if (this.panelState === 'starting') return 'Opening…'
      if (this.panelState === 'active' || this.panelState === 'approval') return 'Session active'
      return 'Ask AI'
    },
    statusLabel(): string {
      return {
        missing: 'SET-UP NEEDED',
        ready: 'READY',
        starting: 'STARTING',
        active: 'CONNECTED',
        approval: 'YOUR REVIEW',
        error: 'OFFLINE',
      }[this.panelState]
    },
    statusTone(): string {
      if (this.panelState === 'ready' || this.panelState === 'active') return 'success'
      if (this.panelState === 'error') return 'error'
      if (this.panelState === 'starting') return 'working'
      return 'warning'
    },
  },
})
</script>

<style scoped>
.panel { position: relative; min-height: 680px; padding-bottom: 126px; color: var(--primary-color); background: var(--off-white); border-left: 5px solid var(--accent-color); }
header { display: flex; align-items: center; justify-content: space-between; min-height: 72px; padding: 14px 15px 14px 17px; border-bottom: 1px solid var(--header-border-color); }
.product, .surface { display: block; }
.product { font-size: 14px; font-weight: 800; letter-spacing: .11em; }
.surface { margin-top: 3px; color: var(--muted-text-color); font-size: 8px; letter-spacing: .18em; }
.status-chip { padding: 5px 7px; color: var(--accent-color); background: #edf0fb; border-radius: 4px; font-size: 8px; font-weight: 800; letter-spacing: .06em; }
.status-chip--success { color: var(--success-color); background: var(--success-surface); }
.status-chip--warning { color: var(--warning-color); background: var(--warning-surface); }
.status-chip--error { color: var(--error-color); background: var(--error-surface); }
main { padding: 21px 17px; }
.eyebrow { margin: 0 0 6px; color: var(--muted-text-color); font-size: 8px; font-weight: 800; letter-spacing: .12em; }
.workspace-summary { padding-bottom: 20px; border-bottom: 1px solid var(--header-border-color); }
h1 { overflow: hidden; margin: 0 0 6px; font-size: 18px; text-overflow: ellipsis; white-space: nowrap; }
.workspace-summary > p:last-child { max-width: 285px; margin: 0; color: var(--dark-grey); font-size: 10px; line-height: 1.5; }
.event { display: grid; grid-template-columns: 31px 1fr; gap: 11px; margin: 18px 0; padding: 13px; background: var(--page-background-color); border-left: 3px solid var(--accent-color); }
.event--warning { background: var(--warning-surface); border-color: #c08122; }
.event--success { background: var(--success-surface); border-color: var(--success-color); }
.event--error { background: var(--error-surface); border-color: var(--error-color); }
.event-number { display: grid; place-items: center; width: 29px; height: 29px; color: #fff; background: var(--accent-color); border-radius: 2px; font-size: 10px; font-weight: 800; }
.event--warning .event-number { background: #c08122; }
.event--success .event-number { background: var(--success-color); }
.event--error .event-number { background: var(--error-color); }
.event b, .event p { display: block; }
.event b { font-size: 11px; }
.event p { margin: 4px 0; color: var(--dark-grey); font-size: 10px; line-height: 1.4; }
.event a, .event button { margin: 3px 10px 0 0; padding: 0; color: var(--accent-color); background: transparent; border: 0; font-size: 9px; font-weight: 700; }
.approval { margin: 18px 0; padding: 15px; background: var(--warning-surface); border: 1px solid #e5ca98; }
.approval-heading { display: flex; justify-content: space-between; color: var(--warning-color); font-size: 8px; letter-spacing: .08em; }
.approval-heading b { color: var(--primary-color); letter-spacing: 0; }
h2 { margin: 15px 0 10px; font-size: 15px; }
dl { margin: 0; border-top: 1px solid #e5ca98; }
dl div { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #e5ca98; font-size: 9px; }
dt { color: var(--muted-text-color); }
dd { margin: 0; font-weight: 700; }
.button-pair { display: grid; grid-template-columns: 1.4fr 1fr; gap: 7px; margin-top: 12px; }
.button-pair button { min-height: 34px; color: var(--primary-color); background: #fff; border: 1px solid var(--navigation-border-color); font-size: 9px; font-weight: 700; }
.button-pair .approve { color: #fff; background: var(--primary-color); border-color: var(--primary-color); }
.workflow-strip { padding-top: 4px; }
.workflow-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.workflow-tags span { padding: 6px 8px; color: var(--accent-color); background: #edf0fb; border: 1px solid #d6dcef; border-radius: 3px; font-size: 9px; font-weight: 700; }
.feedback { display: inline-block; margin-top: 24px; color: var(--accent-color); font-size: 9px; }
.launch-dock { position: absolute; right: 0; bottom: 0; left: 0; padding: 13px 17px 16px; background: var(--primary-color); box-shadow: 0 -8px 25px #333c5521; }
.launch-dock b, .launch-dock span { display: block; }
.launch-dock b { color: #fff; font-size: 11px; }
.launch-dock > div > span { margin: 3px 0 10px; color: #d9ddeb; font-size: 8px; }
.launch-dock button { display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 43px; padding: 10px 13px; color: var(--primary-color); background: #fff; border: 0; border-radius: 3px; font-size: 12px; font-weight: 800; }
.launch-dock button:disabled { color: #717687; background: #d4d7df; }
.launch-dock button span { font-size: 14px; }
</style>

