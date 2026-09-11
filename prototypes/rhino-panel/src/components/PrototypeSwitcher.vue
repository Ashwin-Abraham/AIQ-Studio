<template>
  <aside class="switcher" aria-label="Prototype controls">
    <div class="variant-controls">
      <button type="button" aria-label="Previous variant" @click="cycleVariant(-1)">←</button>
      <strong>{{ currentVariant }} · {{ variantName }}</strong>
      <button type="button" aria-label="Next variant" @click="cycleVariant(1)">→</button>
    </div>

    <label>
      State
      <select :value="currentState" @change="selectState">
        <option v-for="state in states" :key="state.id" :value="state.id">
          {{ state.label }}
        </option>
      </select>
    </label>
  </aside>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { PanelState } from '../models/PanelState'
import type { PanelStateDefinition } from '../models/PanelStateDefinition'
import type { VariantId } from '../models/VariantId'

const variants: VariantId[] = ['A', 'B', 'C']

export default defineComponent({
  name: 'PrototypeSwitcher',

  props: {
    currentVariant: {
      type: String as PropType<VariantId>,
      required: true,
    },
    currentState: {
      type: String as PropType<PanelState>,
      required: true,
    },
    states: {
      type: Array as PropType<PanelStateDefinition[]>,
      required: true,
    },
  },

  emits: {
    'change-variant': (value: VariantId) => variants.includes(value),
    'change-state': (value: PanelState) => value.length > 0,
  },

  computed: {
    variantName(): string {
      return {
        A: 'Calm launch',
        B: 'Docked control',
        C: 'Guided launch',
      }[this.currentVariant]
    },
  },

  mounted() {
    window.addEventListener('keydown', this.handleKeydown)
  },

  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeydown)
  },

  methods: {
    cycleVariant(direction: number): void {
      const currentIndex = variants.indexOf(this.currentVariant)
      const nextIndex = (currentIndex + direction + variants.length) % variants.length
      this.$emit('change-variant', variants[nextIndex]!)
    },
    selectState(event: Event): void {
      this.$emit('change-state', (event.target as HTMLSelectElement).value as PanelState)
    },
    handleKeydown(event: KeyboardEvent): void {
      const target = event.target as HTMLElement | null

      if (target?.matches('input, textarea, select, [contenteditable]')) {
        return
      }

      if (event.key === 'ArrowLeft') {
        this.cycleVariant(-1)
      }

      if (event.key === 'ArrowRight') {
        this.cycleVariant(1)
      }
    },
  },
})
</script>

<style scoped>
.switcher {
  position: fixed;
  bottom: 18px;
  left: 50%;
  z-index: 100;
  display: grid;
  grid-template-columns: auto auto;
  align-items: center;
  gap: 16px;
  min-width: 340px;
  padding: 9px 12px;
  color: #ffffff;
  background: #20242e;
  border: 1px solid #ffffff28;
  border-radius: 14px;
  box-shadow: 0 10px 32px #00000048;
  transform: translateX(-50%);
}

.variant-controls {
  display: grid;
  grid-template-columns: 30px minmax(120px, 1fr) 30px;
  align-items: center;
  gap: 6px;
}

button {
  width: 30px;
  height: 30px;
  color: #ffffff;
  background: #ffffff13;
  border: 1px solid #ffffff2b;
  border-radius: 7px;
}

strong {
  font-size: 11px;
  text-align: center;
}

label {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 7px;
  font-size: 10px;
}

select {
  max-width: 150px;
  min-height: 30px;
  padding: 4px 24px 4px 7px;
  color: #ffffff;
  background: #303641;
  border: 1px solid #ffffff30;
  border-radius: 6px;
  font-size: 10px;
}

@media (max-width: 600px) {
  .switcher {
    bottom: 8px;
    grid-template-columns: 1fr;
    gap: 7px;
    width: calc(100% - 16px);
    min-width: 0;
  }

  label {
    grid-template-columns: 45px 1fr;
  }

  select {
    max-width: none;
  }
}
</style>

