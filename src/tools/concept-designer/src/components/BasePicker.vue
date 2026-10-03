<template>
  <section class="base-picker" aria-labelledby="base-title">
    <p class="eyebrow">START HERE · 01</p>
    <h2 id="base-title">Choose your base</h2>
    <p>Use a sketch or site boundary, or start with an empty canvas.</p>
    <div class="base-choices">
      <label class="file-button"
        >↑ Upload sketch<input
          type="file"
          accept="image/png,image/jpeg,image/webp"
          @change="chooseBase($event, 'Sketch')"
      /></label>
      <label class="file-button"
        >◇ Upload site boundary<input
          type="file"
          accept=".svg"
          @change="chooseBase($event, 'Site boundary')"
      /></label>
      <button @click="drawingBase = true">∿ Draw site boundary</button>
      <button @click="explainRhino">Rhino selection…</button>
      <button @click="startBlank">＋ No base</button>
    </div>
    <small>Sketch: PNG, JPEG or WebP. Boundary: SVG with a viewBox. Maximum 10 MB.</small>
    <div v-if="drawingBase">
      <p>Draw your boundary. This is a concept diagram with no measured scale.</p>
      <DesignCanvas :drawings="boundaryDrawings" tool="pen" @add="boundaryDrawings.push($event)" />
      <button :disabled="!boundaryDrawings.length" @click="boundaryDrawings.pop()">
        Undo last
      </button>
      <button :disabled="!boundaryDrawings.length" @click="useDrawnBoundary">
        Use this boundary
      </button>
    </div>
  </section>
</template>
<script lang="ts">
import { defineComponent } from 'vue'
import DesignCanvas from './DesignCanvas.vue'
import type { Drawing } from '../models/Drawing'
import type { BaseSelection } from '../models/BaseSelection'
import { boundaryImageSource, readBaseFile } from '../designFiles'

export default defineComponent({
  name: 'BasePicker',
  components: { DesignCanvas },
  emits: { choose: (_base: BaseSelection) => true, error: (_message: string) => true },
  data() {
    return { drawingBase: false, boundaryDrawings: [] as Drawing[] }
  },
  methods: {
    explainRhino() {
      this.$emit(
        'error',
        'Rhino is not connected in this prototype. Export the selected boundary as SVG, then use Upload site boundary.',
      )
    },
    startBlank() {
      this.$emit('choose', { name: 'No base', source: null })
    },
    useDrawnBoundary() {
      this.$emit('choose', {
        name: 'Drawn boundary',
        source: boundaryImageSource(this.boundaryDrawings),
      })
    },
    async chooseBase(event: Event, name: string) {
      const input = event.target as HTMLInputElement
      const file = input.files?.[0]
      if (!file) return
      try {
        this.$emit('choose', {
          name: `${name}: ${file.name}`,
          source: await readBaseFile(file, name),
        })
      } catch (error) {
        this.$emit('error', String(error))
      }
      input.value = ''
    },
  },
})
</script>
