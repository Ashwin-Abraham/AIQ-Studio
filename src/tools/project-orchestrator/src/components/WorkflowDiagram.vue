<script lang="ts">
import { defineComponent, type PropType } from "vue";
import type { WorkflowStage } from "../models/WorkflowStage";
import type { StageRecord } from "../models/StageRecord";
import { edges } from "../WorkflowService";
import { fitView, zoomView } from "../ViewportService";
import WorkflowNode from "./WorkflowNode.vue";
import WorkflowLegend from "./WorkflowLegend.vue";
import DiagramControls from "./DiagramControls.vue";

interface DragState {
  x: number;
  y: number;
  originX: number;
  originY: number;
  scaleX: number;
  scaleY: number;
}

export default defineComponent({
  name: "WorkflowDiagram",
  components: { WorkflowNode, WorkflowLegend, DiagramControls },
  props: {
    stages: { type: Array as PropType<WorkflowStage[]>, required: true },
    records: {
      type: Object as PropType<Record<string, StageRecord>>,
      required: true,
    },
    selectedId: { type: String, required: true },
  },
  emits: { select: (id: string) => Boolean(id) },
  data() {
    return { edges, view: fitView(), drag: null as DragState | null };
  },
  computed: {
    viewBox() {
      const { x, y, width, height } = this.view;
      return `${x} ${y} ${width} ${height}`;
    },
    zoomLevel() {
      return Math.round((1250 / this.view.width) * 100);
    },
  },
  methods: {
    fit() {
      this.view = fitView();
    },
    zoom(factor: number) {
      this.view = zoomView(
        this.view,
        factor,
        this.view.x + this.view.width / 2,
        this.view.y + this.view.height / 2,
      );
    },
    wheel(event: WheelEvent) {
      const svg = this.$refs.canvas as SVGSVGElement;
      const matrix = svg.getScreenCTM();
      if (!matrix) return;
      const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(
        matrix.inverse(),
      );
      this.view = zoomView(
        this.view,
        event.deltaY < 0 ? 1.12 : 1 / 1.12,
        point.x,
        point.y,
      );
    },
    startDrag(event: PointerEvent) {
      if (
        event.button !== 0 ||
        (event.target as Element).closest('[role="button"]')
      )
        return;
      const matrix = (this.$refs.canvas as SVGSVGElement).getScreenCTM();
      if (!matrix) return;
      this.drag = {
        x: event.clientX,
        y: event.clientY,
        originX: this.view.x,
        originY: this.view.y,
        scaleX: matrix.a,
        scaleY: matrix.d,
      };
      (event.currentTarget as Element).setPointerCapture(event.pointerId);
    },
    moveDrag(event: PointerEvent) {
      if (!this.drag) return;
      this.view.x =
        this.drag.originX - (event.clientX - this.drag.x) / this.drag.scaleX;
      this.view.y =
        this.drag.originY - (event.clientY - this.drag.y) / this.drag.scaleY;
    },
    stopDrag() {
      this.drag = null;
    },
  },
});
</script>

<template>
  <section class="diagram panel" aria-label="Site planning flowchart">
    <div class="diagram-header">
      <h2>Design stages</h2>
      <WorkflowLegend />
      <DiagramControls :level="zoomLevel" @zoom="zoom" @fit="fit" />
    </div>
    <div
      class="viewport"
      :class="{ dragging: drag }"
      @pointerdown="startDrag"
      @pointermove="moveDrag"
      @pointerup="stopDrag"
      @pointercancel="stopDrag"
      @lostpointercapture="stopDrag"
    >
      <svg
        ref="canvas"
        :viewBox="viewBox"
        preserveAspectRatio="xMidYMid meet"
        role="group"
        aria-label="Site planning stages"
        @wheel.prevent="wheel"
      >
        <defs>
          <marker
            id="workflow-arrow"
            viewBox="0 0 8 8"
            refX="8"
            refY="4"
            markerUnits="userSpaceOnUse"
            markerWidth="9"
            markerHeight="9"
            orient="auto"
          >
            <path d="M0 0 L8 4 L0 8 Z" fill="#63718b" />
          </marker>
        </defs>
        <path v-for="edge in edges" :key="edge" class="edge" :d="edge" />
        <WorkflowNode
          v-for="stage in stages"
          :key="stage.id"
          :stage="stage"
          :status="records[stage.id]?.status"
          :selected="selectedId === stage.id"
          @select="$emit('select', $event)"
        />
        <text x="26" y="271" class="context-label">
          Project folder structure holds the records · People can revise any
          step at any time
        </text>
      </svg>
    </div>
    <p class="diagram-note">
      Drag the blank canvas to pan. Use the wheel or the controls to zoom.
      Arrows show information flow; later work can change an earlier decision.
    </p>
  </section>
</template>

<style scoped>
.diagram {
  min-width: 0;
  overflow: hidden;
}
.diagram-header {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  padding: 18px 22px;
  border-bottom: 1px solid var(--border);
}
h2 {
  font-size: 18px;
  margin: 0;
}
.viewport {
  aspect-ratio: 1250 / 286;
  overflow: hidden;
  background-color: #f8f9fc;
  background-image:
    linear-gradient(#dce0e980 1px, transparent 1px),
    linear-gradient(90deg, #dce0e980 1px, transparent 1px);
  background-size: 24px 24px;
  cursor: grab;
  touch-action: none;
}
.dragging {
  cursor: grabbing;
}
svg {
  display: block;
  width: 100%;
  height: 100%;
}
.edge {
  fill: none;
  stroke: #63718b;
  stroke-width: 1.8;
  marker-end: url(#workflow-arrow);
}
.context-label {
  font-size: 14px;
  fill: var(--muted);
}
.diagram-note {
  padding: 12px 22px 18px;
  border-top: 1px solid var(--border);
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}
@media (max-width: 650px) {
  .viewport {
    aspect-ratio: 2;
  }
}
</style>
