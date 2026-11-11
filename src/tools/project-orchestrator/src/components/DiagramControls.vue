<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({
  name: "DiagramControls",
  props: { level: { type: Number, required: true } },
  emits: { zoom: (factor: number) => factor > 0, fit: () => true },
});
</script>

<template>
  <div class="controls" aria-label="Canvas controls">
    <button type="button" aria-label="Zoom out" @click="$emit('zoom', 1 / 1.2)">
      −
    </button>
    <output aria-label="Zoom level">{{ level }}%</output>
    <button type="button" aria-label="Zoom in" @click="$emit('zoom', 1.2)">
      +
    </button>
    <button type="button" @click="$emit('fit')">Fit</button>
  </div>
</template>

<style scoped>
.controls {
  display: flex;
  gap: 5px;
  align-items: center;
  margin-left: auto;
}
button {
  height: 31px;
  min-width: 31px;
  padding: 0 9px;
  background: #d1d6e3;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--ink);
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
}
button:hover {
  background: #e3e6ee;
}
button:focus-visible {
  outline: 3px solid #a8b6ff;
  outline-offset: 2px;
}
output {
  min-width: 43px;
  text-align: center;
  font-size: 13px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
</style>
