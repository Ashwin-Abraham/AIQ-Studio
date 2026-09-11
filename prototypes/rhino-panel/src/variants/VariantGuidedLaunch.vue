<template>
  <section class="panel panel--guided">
    <header>
      <span class="mark">AIQ</span>
      <div><b>AIQ Studio</b><small>Rhino panel</small></div>
      <button type="button" aria-label="Open panel menu">•••</button>
    </header>

    <main>
      <div class="welcome"><p>WORK WITH AI</p><h1>Start here in Rhino.<br />Continue in your AI app.</h1></div>

      <ol class="steps">
        <li :class="{ complete: companionReady, current: panelState === 'missing' }">
          <span class="step-marker">1</span>
          <div class="step-body">
            <div class="step-title"><b>Connect AIQ Studio</b><span>{{ companionReady ? 'Ready' : 'Needed' }}</span></div>
            <p v-if="companionReady">Codex or OpenCode can use the Rhino workflows.</p>
            <template v-else><p>Install the companion plug-in in your preferred AI app.</p><a href="#install">Open installation guide</a></template>
          </div>
        </li>

        <li :class="{ current: ['ready', 'starting'].includes(panelState), complete: sessionStarted }">
          <span class="step-marker">2</span>
          <div class="step-body step-body--launch">
            <div class="step-title"><b>Open your AI session</b><span v-if="sessionStarted">Open</span></div>
            <p>Select the workflow and continue the conversation in Codex or OpenCode.</p>
            <button class="ask-button" type="button" :disabled="askDisabled">{{ askLabel }} <span>↗</span></button>
          </div>
        </li>

        <li :class="{ current: panelState === 'approval', complete: panelState === 'active' }">
          <span class="step-marker">3</span>
          <div class="step-body">
            <div class="step-title"><b>Review Rhino changes</b><span v-if="panelState === 'approval'">Review</span></div>
            <template v-if="panelState === 'approval'">
              <p class="approval-copy">AIQ Studio wants to add 14 building outlines to new layers.</p>
              <div class="button-pair"><button class="approve" type="button">Approve</button><button type="button">Reject</button></div>
            </template>
            <p v-else>AIQ Studio will ask before it changes your file.</p>
          </div>
        </li>
      </ol>

      <section v-if="panelState === 'starting'" class="banner banner--working"><span class="pulse" />Opening Codex. Keep Rhino open.</section>
      <section v-if="panelState === 'active'" class="banner banner--success"><span>✓</span><div><b>Session active in Codex</b><small>Return to Codex to continue.</small></div></section>
      <section v-if="panelState === 'error'" class="banner banner--error"><span>!</span><div><b>The AI app did not open</b><small>Your Rhino file was not changed.</small><button type="button">Try again</button><a href="#help">Get help</a></div></section>

      <details class="workflows">
        <summary>2 workflows available</summary>
        <ul><li><b>Site Data Model</b><span>Buildings, terrain, and context</span></li><li><b>Plan Export</b><span>Illustrator plan and PNG preview</span></li></ul>
      </details>
    </main>

    <footer><a href="#feedback">Send feedback</a><span>AIQ Studio</span></footer>
  </section>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { PanelState } from '../models/PanelState'

export default defineComponent({
  name: 'VariantGuidedLaunch',

  props: {
    panelState: {
      type: String as PropType<PanelState>,
      required: true,
    },
  },

  computed: {
    companionReady(): boolean {
      return this.panelState !== 'missing'
    },
    sessionStarted(): boolean {
      return ['active', 'approval'].includes(this.panelState)
    },
    askDisabled(): boolean {
      return ['missing', 'starting', 'active', 'approval'].includes(this.panelState)
    },
    askLabel(): string {
      if (this.panelState === 'starting') return 'Opening Codex…'
      if (this.panelState === 'active' || this.panelState === 'approval') return 'Session active'
      return 'Ask AI'
    },
  },
})
</script>

<style scoped>
.panel { min-height: 680px; color: var(--primary-color); background: linear-gradient(180deg, #f8f9fc 0, var(--page-background-color) 58%); }
header { display: grid; grid-template-columns: 35px 1fr auto; align-items: center; gap: 10px; padding: 16px 17px; background: var(--primary-color); color: #fff; }
.mark { display: grid; place-items: center; width: 34px; height: 34px; color: var(--primary-color); background: #fff; border-radius: 50%; font-size: 10px; font-weight: 900; }
header b, header small { display: block; }
header b { font-size: 14px; letter-spacing: .02em; }
header small { margin-top: 2px; color: #d5d9e4; font-size: 8px; letter-spacing: .1em; text-transform: uppercase; }
header button { color: #fff; background: transparent; border: 0; letter-spacing: .1em; }
main { padding: 22px 18px 16px; }
.welcome p { margin: 0 0 7px; color: var(--accent-color); font-size: 8px; font-weight: 800; letter-spacing: .14em; }
h1 { margin: 0 0 22px; font-size: 19px; line-height: 1.25; }
.steps { display: grid; gap: 0; margin: 0; padding: 0; list-style: none; }
.steps li { position: relative; display: grid; grid-template-columns: 29px 1fr; gap: 10px; padding-bottom: 14px; opacity: .66; }
.steps li:not(:last-child)::before { position: absolute; top: 28px; bottom: 0; left: 13px; width: 1px; background: var(--navigation-border-color); content: ''; }
.steps li.current, .steps li.complete { opacity: 1; }
.step-marker { z-index: 1; display: grid; place-items: center; width: 27px; height: 27px; color: var(--muted-text-color); background: #fff; border: 1px solid var(--navigation-border-color); border-radius: 50%; font-size: 9px; font-weight: 800; }
.complete .step-marker { color: #fff; background: var(--success-color); border-color: var(--success-color); }
.current .step-marker { color: #fff; background: var(--accent-color); border-color: var(--accent-color); box-shadow: 0 0 0 4px #58629e18; }
.step-body { padding: 5px 0 12px; }
.step-body--launch { padding: 13px; background: #fff; border: 1px solid var(--navigation-border-color); border-radius: var(--primary-radius); box-shadow: var(--panel-shadow); }
.step-title { display: flex; justify-content: space-between; gap: 8px; }
.step-title b { font-size: 11px; }
.step-title span { color: var(--accent-color); font-size: 8px; font-weight: 800; text-transform: uppercase; }
.step-body p { margin: 5px 0; color: var(--dark-grey); font-size: 9px; line-height: 1.45; }
.step-body a { color: var(--accent-color); font-size: 9px; font-weight: 700; }
.ask-button { display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 43px; margin-top: 11px; padding: 9px 12px; color: #fff; background: var(--primary-color); border: 0; border-radius: var(--secondary-radius); font-size: 12px; font-weight: 800; }
.ask-button:disabled { background: #858b9a; }
.approval-copy { padding: 8px; background: var(--warning-surface); border-left: 2px solid #c08122; }
.button-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 8px; }
.button-pair button { min-height: 31px; color: var(--primary-color); background: #fff; border: 1px solid var(--navigation-border-color); border-radius: 5px; font-size: 9px; font-weight: 700; }
.button-pair .approve { color: #fff; background: var(--primary-color); border-color: var(--primary-color); }
.banner { display: flex; align-items: flex-start; gap: 9px; margin: 4px 0 14px 39px; padding: 10px; border-radius: 6px; font-size: 9px; }
.banner--working { color: var(--accent-color); background: #edf0fb; }
.banner--success { background: var(--success-surface); border: 1px solid #b4d6c1; }
.banner--error { background: var(--error-surface); border: 1px solid #e1aaaa; }
.banner b, .banner small { display: block; }
.banner small { margin-top: 2px; color: var(--dark-grey); }
.banner button, .banner a { margin: 6px 10px 0 0; padding: 0; color: var(--accent-color); background: transparent; border: 0; font-size: 8px; font-weight: 700; }
.pulse { flex: 0 0 auto; width: 7px; height: 7px; margin-top: 2px; background: var(--accent-color); border-radius: 50%; }
.workflows { margin: 2px 0 0 39px; padding: 9px 10px; background: #ffffffa8; border: 1px solid var(--navigation-border-color); border-radius: 6px; }
.workflows summary { color: var(--accent-color); font-size: 9px; font-weight: 700; cursor: pointer; }
.workflows ul { display: grid; gap: 8px; margin: 10px 0 0; padding: 0; list-style: none; }
.workflows li { display: block; padding: 0; opacity: 1; }
.workflows b, .workflows span { display: block; }
.workflows b { font-size: 9px; }
.workflows span { margin-top: 2px; color: var(--muted-text-color); font-size: 8px; }
footer { display: flex; justify-content: space-between; padding: 8px 18px 17px 57px; color: var(--muted-text-color); font-size: 8px; }
footer a { color: var(--accent-color); }
</style>
