<template>
  <div class="shape-properties" role="group" aria-label="Selected shape properties">
    <label
      >Fill
      <input
        type="color"
        aria-label="Shape fill"
        :value="fillColor"
        @input="changeColor('fill', $event)"
    /></label>
    <label><input type="checkbox" :checked="hasFill" @change="toggleFill" /> Fill enabled</label>
    <label
      >Line colour
      <input
        type="color"
        aria-label="Line colour"
        :value="drawing.stroke ?? '#224d45'"
        @input="changeColor('stroke', $event)"
    /></label>
    <label
      >Thickness
      <input
        type="number"
        aria-label="Line thickness"
        min="0"
        max="50"
        step="0.5"
        :value="lineWidth"
        @input="changeWidth"
    /></label>
    <label
      >Line type
      <select :value="drawing.lineType ?? 'solid'" @change="changeType">
        <option value="solid">Solid</option>
        <option value="dashed">Dashed</option>
        <option value="dotted">Dotted</option>
      </select></label
    >
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { Drawing } from '../models/Drawing'
import { defaultFill } from '../drawingStyle'

export default defineComponent({
  name: 'ShapeProperties',
  props: { drawing: { type: Object as PropType<Drawing>, required: true } },
  emits: { update: (_drawing: Drawing) => true },
  computed: {
    hasFill(): boolean {
      return defaultFill(this.drawing) !== 'transparent'
    },
    fillColor(): string {
      return this.hasFill ? defaultFill(this.drawing) : '#cbdcba'
    },
    lineWidth(): number {
      return this.drawing.strokeWidth ?? (this.drawing.kind === 'text' ? 0 : 3)
    },
  },
  methods: {
    changeColor(key: 'fill' | 'stroke', event: Event) {
      this.$emit('update', { ...this.drawing, [key]: (event.target as HTMLInputElement).value })
    },
    toggleFill(event: Event) {
      this.$emit('update', {
        ...this.drawing,
        fill: (event.target as HTMLInputElement).checked ? this.fillColor : 'transparent',
      })
    },
    changeWidth(event: Event) {
      const input = event.target as HTMLInputElement
      const width = input.valueAsNumber
      if (Number.isFinite(width) && width >= 0 && width <= 50)
        this.$emit('update', { ...this.drawing, strokeWidth: width })
      else input.value = String(this.lineWidth)
    },
    changeType(event: Event) {
      const lineType = (event.target as HTMLSelectElement).value as Drawing['lineType']
      this.$emit('update', { ...this.drawing, lineType })
    },
  },
})
</script>

<style scoped>
.shape-properties {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid #d5dccf;
  background: #fff;
}
label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
input[type='color'] {
  width: 30px;
  height: 28px;
  padding: 0;
  border: 0;
  background: transparent;
}
input[type='number'] {
  width: 62px;
  padding: 6px;
  border: 1px solid #ccd5ca;
  border-radius: 5px;
}
select {
  font-size: 12px;
  padding: 7px 10px;
}
</style>
