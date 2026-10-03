<template>
  <div>
    <div class="toolbar" role="group" aria-label="Drawing tools">
      <button
        v-for="item in tools"
        :key="item.id"
        :aria-pressed="tool === item.id"
        :title="item.name"
        :aria-label="item.name"
        @click="$emit('update:tool', item.id)"
      >
        <svg v-if="item.id === 'select'" class="tool-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M5 3L19 13L12 14L9 21Z" fill="currentColor" />
        </svg>
        <svg
          v-else-if="item.id === 'erase'"
          class="tool-icon eraser-icon"
          viewBox="0 0 24 32"
          aria-hidden="true"
        >
          <g transform="rotate(18 12 16)">
            <rect
              x="6"
              y="3"
              width="12"
              height="26"
              rx="2"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
            />
            <path d="M6 19H18V27Q18 29 16 29H8Q6 29 6 27Z" fill="currentColor" />
            <path d="M6 19H18" stroke="currentColor" stroke-width="1.7" />
          </g>
        </svg>
        <span v-else aria-hidden="true">{{ item.icon }}</span
        ><small>{{ item.name }}</small>
      </button>
      <button :disabled="!canUndo" aria-label="Undo" @click="$emit('undo')">
        ↶<small>Undo</small>
      </button>
      <button :disabled="!canRedo" aria-label="Redo" @click="$emit('redo')">
        ↷<small>Redo</small>
      </button>
    </div>
    <label v-if="tool === 'text'" class="text-label"
      >Text <input :value="textLabel" maxlength="160" @input="updateText"
    /></label>
    <label v-if="tool === 'fill'" class="fill-controls"
      >Fill colour
      <input :value="fillColor" type="color" aria-label="Fill colour" @input="updateFill" /><small
        >Click a shape to fill it.</small
      ></label
    >
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  name: 'DrawingToolbar',
  props: {
    tool: { type: String, required: true },
    textLabel: { type: String, default: 'Note' },
    fillColor: { type: String, default: '#cbdcba' },
    canUndo: { type: Boolean, default: false },
    canRedo: { type: Boolean, default: false },
  },
  emits: {
    'update:tool': (_value: string) => true,
    'update:textLabel': (_value: string) => true,
    'update:fillColor': (_value: string) => true,
    undo: () => true,
    redo: () => true,
  },
  data() {
    return {
      tools: [
        { id: 'select', name: 'Select', icon: '↖' },
        { id: 'copy', name: 'Copy', icon: '⧉' },
        { id: 'pen', name: 'Pen', icon: '∿' },
        { id: 'line', name: 'Line', icon: '╱' },
        { id: 'arrow', name: 'Arrow', icon: '↗' },
        { id: 'rectangle', name: 'Rectangle', icon: '▱' },
        { id: 'circle', name: 'Circle', icon: '◯' },
        { id: 'text', name: 'Text', icon: 'T' },
        { id: 'fill', name: 'Fill', icon: '◩' },
        { id: 'erase', name: 'Erase', icon: '⌫' },
      ],
    }
  },
  methods: {
    updateText(event: Event) {
      this.$emit('update:textLabel', (event.target as HTMLInputElement).value)
    },
    updateFill(event: Event) {
      this.$emit('update:fillColor', (event.target as HTMLInputElement).value)
    },
  },
})
</script>
