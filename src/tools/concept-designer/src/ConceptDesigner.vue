<template>
  <main>
    <BasePicker v-if="!baseChosen" @choose="setBase" @error="error = $event" />

    <template v-else>
      <section class="workspace" aria-label="Design workspace">
        <div class="canvas-area">
          <div class="drawing-column">
            <DrawingToolbar
              v-model:tool="tool"
              v-model:text-label="textLabel"
              v-model:fill-color="fillColor"
              :can-undo="!!activeHistory.past.length"
              :can-redo="!!activeHistory.future.length"
              @undo="undo"
              @redo="redo"
            />
            <DesignCanvas
              :key="activeOption.stageIds[activeOption.stage]"
              :drawings="activeOption.drawings"
              :active-stage="activeOption.stage"
              :tool="tool"
              :text-label="textLabel"
              :fill-color="fillColor"
              :underlay="underlay"
              :overlays="overlayImages"
              :show-underlay="layers.underlay"
              :show-overlay="layers.ai"
              :show-human="layers.human"
              @add="addDrawing"
              @update="updateDrawing"
              @erase="eraseDrawing"
            />
            <div class="canvas-caption">
              <span>CONCEPT WORKSPACE</span><span>Diagram only · scale not set</span>
            </div>
          </div>
          <DesignStages
            :key="activeOption.id"
            :ids="activeOption.stageIds"
            :names="activeOption.stageNames"
            :active-stage="activeOption.stage"
            @select="activeOption.stage = $event"
            @rename="renameStage"
            @add="addStage"
            @remove="deleteStage"
          />
        </div>
        <div class="options-bar">
          <nav aria-label="Design options">
            <button
              v-for="option in options"
              :key="option.id"
              :aria-pressed="option.id === activeId"
              @click="activeId = option.id"
            >
              {{ option.name }}
            </button>
          </nav>
        </div>
      </section>
      <div class="layer-bar">
        <span class="eyebrow">VISIBLE LAYERS</span
        ><label><input v-model="layers.underlay" type="checkbox" /> Underlay</label
        ><label><input v-model="layers.ai" type="checkbox" /> AI overlay</label
        ><label><input v-model="layers.human" type="checkbox" /> Human input</label
        ><label class="file-button compact"
          >↑ Import SVG<input type="file" accept=".svg" @change="importOverlay"
        /></label>
      </div>
      <DesignConversation
        :messages="activeOption.messages"
        :options="options"
        :active-id="activeId"
        @submit="addMessage"
        @select="activeId = $event"
      />
      <div class="export-row"><button @click="exportSession">Export session ↓</button></div>
      <p class="footnote">This prototype keeps work in this tab. Export before you close it.</p>
    </template>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
  </main>
</template>

<script lang="ts">
import { defineComponent, markRaw } from 'vue'
import BasePicker from './components/BasePicker.vue'
import type { BaseSelection } from './models/BaseSelection'
import DrawingToolbar from './components/DrawingToolbar.vue'
import DesignConversation from './components/DesignConversation.vue'
import DesignStages from './components/DesignStages.vue'
import DesignCanvas from './components/DesignCanvas.vue'
import { createOptions } from './designSession'
import { loadImage, svgImageSource, readOverlayFile, exportDesignSession } from './designFiles'
import type { DesignOption } from './models/DesignOption'
import type { Drawing } from './models/Drawing'
import type { DrawingHistory } from './models/DrawingHistory'
import {
  changeStageDrawings,
  travelStageHistory,
  isCurrentDrawing,
  appendStage,
  removeStage,
} from './stageTimeline'

export default defineComponent({
  name: 'ConceptDesigner',
  components: { BasePicker, DesignCanvas, DrawingToolbar, DesignConversation, DesignStages },
  data() {
    return {
      baseChosen: false,
      baseName: '',
      baseSource: null as string | null,
      underlay: null as HTMLImageElement | null,
      overlayImages: [] as HTMLImageElement[],
      options: [] as DesignOption[],
      activeId: '',
      histories: {} as Record<string, DrawingHistory>,
      layers: { underlay: true, ai: true, human: true },
      tool: 'pen',
      textLabel: 'Note',
      fillColor: '#cbdcba',
      error: '',
    }
  },
  computed: {
    activeOption(): DesignOption {
      return this.options.find((option) => option.id === this.activeId)!
    },
    activeHistory(): DrawingHistory {
      return (
        this.histories[`${this.activeId}-${this.activeOption?.stage}`] ?? { past: [], future: [] }
      )
    },
    overlaySources(): string[] {
      if (!this.activeOption) return []
      return Object.entries(this.activeOption.overlays)
        .filter(([stage]) => Number(stage) <= this.activeOption.stage)
        .sort(([a], [b]) => Number(a) - Number(b))
        .map(([, source]) => source)
    },
  },
  watch: {
    async overlaySources(sources: string[]) {
      this.overlayImages = []
      try {
        const images = await Promise.all(sources.map((source) => loadImage(svgImageSource(source))))
        if (sources === this.overlaySources)
          this.overlayImages = images.map((image) => markRaw(image))
      } catch (error) {
        this.error = String(error)
      }
    },
  },
  methods: {
    initialise(name: string) {
      this.baseName = name
      this.options = createOptions(!!this.baseSource)
      this.histories = Object.fromEntries(
        this.options.flatMap((option) =>
          option.stageNames.map((_, stage) => [`${option.id}-${stage}`, { past: [], future: [] }]),
        ),
      )
      this.activeId = this.options[0].id
      this.baseChosen = true
      this.error = ''
    },
    async setBase(base: BaseSelection) {
      try {
        const image = base.source ? await loadImage(base.source) : null
        this.underlay = image ? markRaw(image) : null
        this.baseSource = base.source
        this.initialise(base.name)
      } catch (error) {
        this.error = String(error)
      }
    },
    async importOverlay(event: Event) {
      const input = event.target as HTMLInputElement
      const file = input.files?.[0]
      const option = this.activeOption
      const stageId = option.stageIds[option.stage]
      if (!file) return
      try {
        const source = await readOverlayFile(file)
        const current = this.options.find((item) => item.id === option.id)
        const stage = current?.stageIds.indexOf(stageId) ?? -1
        if (current && stage >= 0) current.overlays[stage] = source
        this.error = ''
      } catch (error) {
        this.error = String(error)
      }
      input.value = ''
    },
    changeDrawings(drawings: Drawing[]) {
      this.activeOption.drawings = changeStageDrawings(
        this.activeOption.drawings,
        this.activeOption.stage,
        this.activeHistory,
        drawings,
      )
      this.tool = 'select'
    },
    addDrawing(drawing: Drawing) {
      this.changeDrawings([
        ...this.activeOption.drawings,
        { ...drawing, stage: this.activeOption.stage },
      ])
    },
    updateDrawing(drawing: Drawing) {
      const original = this.activeOption.drawings.find((item) => item.id === drawing.id)
      if (!original || !isCurrentDrawing(original, this.activeOption.stage)) return
      this.changeDrawings(
        this.activeOption.drawings.map((item) => (item.id === drawing.id ? drawing : item)),
      )
    },
    eraseDrawing(id: string) {
      const original = this.activeOption.drawings.find((item) => item.id === id)
      if (!original || !isCurrentDrawing(original, this.activeOption.stage)) return
      this.changeDrawings(this.activeOption.drawings.filter((drawing) => drawing.id !== id))
    },
    undo() {
      this.activeOption.drawings = travelStageHistory(
        this.activeOption.drawings,
        this.activeOption.stage,
        this.activeHistory,
        'undo',
      )
      this.tool = 'select'
    },
    redo() {
      this.activeOption.drawings = travelStageHistory(
        this.activeOption.drawings,
        this.activeOption.stage,
        this.activeHistory,
        'redo',
      )
      this.tool = 'select'
    },
    addStage(name: string) {
      const option = appendStage(this.activeOption, name)
      if (option === this.activeOption) return
      this.histories[`${option.id}-${option.stage}`] = { past: [], future: [] }
      this.options = this.options.map((item) => (item.id === option.id ? option : item))
    },
    deleteStage(index: number) {
      const result = removeStage(this.activeOption, this.histories, index)
      this.histories = result.histories
      this.options = this.options.map((item) =>
        item.id === result.option.id ? result.option : item,
      )
    },
    renameStage(index: number, name: string) {
      this.activeOption.stageNames[index] = name
    },
    addMessage(text: string) {
      this.activeOption.messages.push({ id: crypto.randomUUID(), text })
    },
    exportSession() {
      exportDesignSession(this.baseName, this.baseSource, this.options, this.activeId)
    },
  },
})
</script>
