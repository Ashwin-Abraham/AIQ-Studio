<script lang="ts">
import { defineComponent } from "vue";
import { statusLabels } from "../WorkflowService";
export default defineComponent({
  name: "WorkflowLegend",
  data() {
    return { statusLabels };
  },
});
</script>

<template>
  <div class="legend" aria-label="Stage status legend">
    <span v-for="(label, status) in statusLabels" :key="status"
      ><i class="status-dot" :data-status="status"></i>{{ label }}</span
    >
  </div>
</template>

<style scoped>
.legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  color: var(--muted);
  font-size: 13px;
  margin-left: auto;
}
span {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--status-color);
}
</style>
