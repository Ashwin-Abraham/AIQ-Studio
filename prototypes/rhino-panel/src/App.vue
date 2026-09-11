<template>
  <main class="prototype-shell">
    <p class="prototype-label">THROWAWAY UI PROTOTYPE · AIQ STUDIO RHINO PANEL</p>

    <div class="rhino-frame" aria-label="Simulated narrow Rhino panel">
      <VariantCalmLaunch v-if="variant === 'A'" :panel-state="panelState" />
      <VariantDockedControl v-else-if="variant === 'B'" :panel-state="panelState" />
      <VariantGuidedLaunch v-else :panel-state="panelState" />
    </div>

    <PrototypeSwitcher
      :current-state="panelState"
      :current-variant="variant"
      :states="states"
      @change-state="changeState"
      @change-variant="changeVariant"
    />
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PanelState } from './models/PanelState'
import type { PanelStateDefinition } from './models/PanelStateDefinition'
import type { VariantId } from './models/VariantId'
import PrototypeSwitcher from './components/PrototypeSwitcher.vue'
import VariantCalmLaunch from './variants/VariantCalmLaunch.vue'
import VariantDockedControl from './variants/VariantDockedControl.vue'
import VariantGuidedLaunch from './variants/VariantGuidedLaunch.vue'

interface AppData {
  variant: VariantId
  panelState: PanelState
  states: PanelStateDefinition[]
}

function getInitialVariant(): VariantId {
  const requestedVariant = new URLSearchParams(window.location.search).get('variant')
  return requestedVariant === 'B' || requestedVariant === 'C' ? requestedVariant : 'A'
}

function getInitialState(): PanelState {
  const requestedState = new URLSearchParams(window.location.search).get('state')
  const allowedStates: PanelState[] = ['missing', 'ready', 'starting', 'active', 'approval', 'error']

  return allowedStates.includes(requestedState as PanelState)
    ? (requestedState as PanelState)
    : 'ready'
}

export default defineComponent({
  name: 'App',

  components: {
    PrototypeSwitcher,
    VariantCalmLaunch,
    VariantDockedControl,
    VariantGuidedLaunch,
  },

  data(): AppData {
    return {
      variant: getInitialVariant(),
      panelState: getInitialState(),
      states: [
        { id: 'missing', label: 'Companion missing' },
        { id: 'ready', label: 'Ready' },
        { id: 'starting', label: 'Starting app' },
        { id: 'active', label: 'Session active' },
        { id: 'approval', label: 'Approval needed' },
        { id: 'error', label: 'Error and recovery' },
      ],
    }
  },

  methods: {
    changeVariant(variant: VariantId): void {
      this.variant = variant
      const url = new URL(window.location.href)
      url.searchParams.set('variant', variant)
      window.history.replaceState({}, '', url)
    },
    changeState(panelState: PanelState): void {
      this.panelState = panelState
      const url = new URL(window.location.href)
      url.searchParams.set('state', panelState)
      window.history.replaceState({}, '', url)
    },
  },
})
</script>

<style scoped>
.prototype-shell {
  min-height: 100vh;
  padding: 32px 18px 110px;
}

.prototype-label {
  max-width: 360px;
  margin: 0 auto 10px;
  color: #4f535c;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-align: center;
}

.rhino-frame {
  width: min(100%, 360px);
  min-height: 680px;
  margin: 0 auto;
  overflow: hidden;
  background: var(--page-background-color);
  border: 1px solid #aaadb5;
  border-radius: 4px;
  box-shadow: 0 22px 60px #2229362b;
}

@media (max-width: 420px) {
  .prototype-shell {
    padding: 0 0 110px;
  }

  .prototype-label {
    padding: 10px 8px;
    margin: 0 auto;
  }

  .rhino-frame {
    width: 100%;
    min-height: calc(100vh - 128px);
    border-right: 0;
    border-left: 0;
    border-radius: 0;
  }
}
</style>
