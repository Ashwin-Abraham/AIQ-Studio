<script lang="ts">
import { defineComponent, type PropType } from "vue";
import type { WorkflowStage } from "../models/WorkflowStage";
import type { WorkflowStatus } from "../models/WorkflowStatus";
import { statusLabels } from "../WorkflowService";
export default defineComponent({
  name: "WorkflowNode",
  props: {
    stage: { type: Object as PropType<WorkflowStage>, required: true },
    status: {
      type: String as PropType<WorkflowStatus>,
      default: "not-started",
      validator: (value: string) => value in statusLabels,
    },
    selected: { type: Boolean, default: false },
  },
  emits: { select: (id: string) => Boolean(id) },
  computed: {
    transform() {
      return `translate(${this.stage.x} ${this.stage.y})`;
    },
    label() {
      return this.stage.subtitle
        ? this.stage.label.split(" ")[0]
        : this.stage.label;
    },
    accessibleLabel() {
      return `${this.stage.label}, ${statusLabels[this.status]}`;
    },
  },
});
</script>

<template>
  <g
    class="workflow-node"
    :class="{ selected }"
    :data-status="status"
    :transform="transform"
    tabindex="0"
    role="button"
    :aria-label="accessibleLabel"
    :aria-pressed="selected"
    @click="$emit('select', stage.id)"
    @keydown.enter.prevent="$emit('select', stage.id)"
    @keydown.space.prevent="$emit('select', stage.id)"
  >
    <rect :width="stage.width" height="54" rx="6" />
    <circle class="status" cx="18" cy="23" r="5" />
    <text x="31" y="27">{{ label }}</text>
    <text v-if="stage.subtitle" class="subtitle" x="31" y="45">
{{
      stage.subtitle
    }}
</text>
  </g>
</template>

<style scoped>
.workflow-node {
  cursor: pointer;
}
rect {
  fill: white;
  stroke: var(--border);
  stroke-width: 1.5;
}
.workflow-node:hover rect,
.workflow-node:focus rect {
  stroke: var(--blue);
  stroke-width: 3;
}
.workflow-node:focus {
  outline: none;
}
.selected rect {
  fill: var(--ink);
  stroke: var(--ink);
  stroke-width: 3;
}
text {
  fill: var(--ink);
  font-size: 19px;
  font-weight: 600;
  pointer-events: none;
}
.subtitle {
  font-size: 14px;
  font-weight: 400;
  fill: var(--muted);
}
.selected text {
  fill: white;
}
.status {
  fill: var(--status-color);
}
.selected .status {
  stroke: white;
  stroke-width: 1px;
  vector-effect: non-scaling-stroke;
}
</style>
