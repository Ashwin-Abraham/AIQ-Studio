<template>
  <div
    ref="host"
    :class="['drawing-surface', `tool-${tool}`]"
    tabindex="0"
    aria-label="Drawing canvas"
    @keydown="handleKeydown"
  >
    <v-stage
      ref="stage"
      :config="stageConfig"
      @pointerdown="start"
      @pointerenter="move"
      @pointermove="move"
      @pointerup="finish"
      @pointerleave="leaveCanvas"
    >
      <v-layer :config="{ listening: false }">
        <v-image v-if="underlay && showUnderlay" :config="{ image: underlay, ...canvasSize }" />
        <template v-if="showOverlay">
          <v-image
            v-for="(image, index) in overlays"
            :key="image.src + index"
            :config="{ image, ...canvasSize }"
          />
        </template>
      </v-layer>
      <v-layer :config="{ visible: showHuman }">
        <v-group
          v-for="drawing in visibleDrawings"
          :key="drawing.id"
          :config="groupConfig(drawing)"
          @pointerdown="pick(drawing.id)"
          @dragstart="beginDrag(drawing, $event)"
          @dragend="endDrag(drawing, $event)"
          @transformend="saveTransform(drawing, $event)"
        >
          <v-line
            v-if="drawing.kind === 'pen' || drawing.kind === 'line'"
            :config="lineConfig(drawing)"
          />
          <v-arrow
            v-else-if="drawing.kind === 'arrow'"
            :config="{
              ...lineConfig(drawing),
              fill: defaultFill(drawing),
              pointerLength: 15,
              pointerWidth: 13,
            }"
          />
          <v-rect v-else-if="drawing.kind === 'rectangle'" :config="shapeConfig(drawing)" />
          <v-ellipse v-else-if="drawing.kind === 'circle'" :config="ellipseConfig(drawing)" />
          <v-text
            v-else
            :config="{
              x: drawing.points[0],
              y: drawing.points[1],
              text: drawing.text,
              fontSize: 20,
              ...drawingStroke(drawing),
              fill: defaultFill(drawing),
            }"
          />
        </v-group>
        <v-transformer ref="transformer" :config="transformerConfig" />
      </v-layer>
      <v-layer :config="{ listening: false }">
        <v-text v-if="textPreviewConfig" :config="textPreviewConfig" />
      </v-layer>
    </v-stage>
    <ShapeProperties
      v-if="selectedDrawing && showHuman"
      :drawing="selectedDrawing"
      @update="$emit('update', $event)"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { KonvaEventObject } from 'konva/lib/Node'
import type { Drawing } from '../models/Drawing'
import { canvasSize } from '../designSession'
import type Konva from 'konva'
import { isCurrentDrawing, visibleStageDrawings } from '../stageTimeline'
import { rotationCursor, styleRotationAnchor } from '../rotationControl'
import { copyDrawing } from '../copyDrawing'
import ShapeProperties from './ShapeProperties.vue'
import { drawingStroke, defaultFill } from '../drawingStyle'

type NodeRef<T> = { getNode(): T }

export default defineComponent({
  name: 'DesignCanvas',
  components: { ShapeProperties },
  props: {
    drawings: { type: Array as PropType<Drawing[]>, required: true },
    tool: { type: String, required: true },
    textLabel: { type: String, default: 'Note' },
    fillColor: { type: String, default: '#cbdcba' },
    underlay: { type: Object as PropType<HTMLImageElement | null>, default: null },
    overlays: { type: Array as PropType<HTMLImageElement[]>, default: () => [] },
    activeStage: { type: Number, default: 0 },
    showUnderlay: { type: Boolean, default: true },
    showOverlay: { type: Boolean, default: true },
    showHuman: { type: Boolean, default: true },
  },
  emits: {
    add: (_drawing: Drawing) => true,
    update: (_drawing: Drawing) => true,
    erase: (_id: string) => true,
  },
  data() {
    return {
      canvasSize,
      width: 1000,
      selectedId: null as string | null,
      copyPreview: null as Drawing | null,
      altAtPointerDown: false,
      draft: null as Drawing | null,
      hoverPoint: null as number[] | null,
      observer: null as ResizeObserver | null,
    }
  },
  computed: {
    textPreviewConfig() {
      if (this.tool !== 'text' || !this.showHuman || !this.hoverPoint) return null
      const offset = 12 / (this.width / canvasSize.width)
      return {
        x: this.hoverPoint[0] + offset,
        y: this.hoverPoint[1] + offset,
        text: this.textLabel,
        fontSize: 20,
        fill: '#224d45',
        opacity: 0.35,
        listening: false,
      }
    },
    selectedDrawing(): Drawing | undefined {
      return this.drawings.find(
        (drawing) => drawing.id === this.selectedId && isCurrentDrawing(drawing, this.activeStage),
      )
    },
    transformerConfig() {
      return {
        rotateEnabled: true,
        rotateAnchorCursor: rotationCursor,
        rotateAnchorAngle: 45,
        rotateAnchorOffset: 32,
        flipEnabled: false,
        keepRatio: false,
        borderStroke: '#b88645',
        anchorStroke: '#b88645',
        anchorFill: '#fff',
        anchorSize: 9,
        padding: 5,
        rotateLineVisible: false,
        shouldOverdrawWholeArea: true,
        boundBoxFunc: (
          oldBox: { width: number; height: number },
          newBox: { width: number; height: number },
        ) => (Math.abs(newBox.width) < 8 || Math.abs(newBox.height) < 8 ? oldBox : newBox),
        anchorStyleFunc: styleRotationAnchor,
      }
    },
    stageConfig() {
      const scale = this.width / canvasSize.width
      return { width: this.width, height: canvasSize.height * scale, scaleX: scale, scaleY: scale }
    },
    visibleDrawings(): Drawing[] {
      const visible = visibleStageDrawings(this.drawings, this.activeStage)
      const drawings = this.draft ? [...visible, this.draft] : visible
      return this.copyPreview ? [this.copyPreview, ...drawings] : drawings
    },
  },
  watch: {
    activeStage() {
      this.hoverPoint = null
      this.selectedId = null
      this.draft = null
      this.copyPreview = null
    },
    selectedId() {
      this.$nextTick(this.attachTransformer)
    },
    tool() {
      this.hoverPoint = null
      this.selectedId = null
    },
    showHuman() {
      this.hoverPoint = null
      this.selectedId = null
    },
    drawings() {
      if (!this.drawings.some((drawing) => drawing.id === this.selectedId)) this.selectedId = null
      this.$nextTick(this.attachTransformer)
    },
  },
  mounted() {
    this.observer = new ResizeObserver(([entry]) => {
      this.width = entry.contentRect.width
    })
    this.observer.observe(this.$refs.host as HTMLElement)
  },
  beforeUnmount() {
    this.observer?.disconnect()
  },
  methods: {
    drawingStroke,
    defaultFill,
    handleKeydown(event: KeyboardEvent) {
      const target = event.target as HTMLElement
      if (target.closest('input, textarea, select, button, [contenteditable]')) return
      if (
        event.key === 'Delete' &&
        this.selectedDrawing &&
        this.tool === 'select' &&
        this.showHuman
      ) {
        event.preventDefault()
        event.stopPropagation()
        this.deleteSelected()
      }
    },
    deleteSelected() {
      if (this.selectedId) this.$emit('erase', this.selectedId)
      this.selectedId = null
      ;(this.$refs.host as HTMLElement).focus({ preventScroll: true })
    },
    point(event: KonvaEventObject<PointerEvent>): number[] | null {
      const stage = event.target.getStage()
      const position = stage?.getPointerPosition()
      if (!position || !stage) return null
      return [position.x / stage.scaleX(), position.y / stage.scaleY()]
    },
    start(event: KonvaEventObject<PointerEvent>) {
      this.altAtPointerDown = event.evt.altKey
      ;(this.$refs.host as HTMLElement).focus({ preventScroll: true })
      if (this.tool === 'select') {
        if (event.target === event.target.getStage()) this.selectedId = null
        return
      }
      if (
        !this.showHuman ||
        ['erase', 'fill', 'copy'].includes(this.tool) ||
        event.evt.button !== 0
      )
        return
      const point = this.point(event)
      if (!point) return
      this.draft = {
        id: crypto.randomUUID(),
        stage: this.activeStage,
        kind: this.tool as Drawing['kind'],
        points: [...point, ...point],
        text: this.textLabel,
      }
      if (this.tool === 'text') this.finish()
    },
    move(event: KonvaEventObject<PointerEvent>) {
      const point = this.point(event)
      this.hoverPoint = point
      if (!this.draft || !point) return
      this.draft.points =
        this.tool === 'pen'
          ? [...this.draft.points, ...point]
          : [...this.draft.points.slice(0, 2), ...point]
    },
    leaveCanvas() {
      this.hoverPoint = null
      this.finish()
    },
    finish() {
      if (this.draft) this.$emit('add', this.draft)
      this.draft = null
    },
    beginDrag(drawing: Drawing, event: KonvaEventObject<DragEvent>) {
      if (this.tool === 'select' && (this.altAtPointerDown || event.evt.altKey)) {
        this.copyPreview = copyDrawing(drawing, 0, 0)
      }
    },
    endDrag(drawing: Drawing, event: KonvaEventObject<DragEvent>) {
      this.altAtPointerDown = false
      if (!this.copyPreview) {
        this.saveTransform(drawing, event)
        return
      }
      const node = event.target
      const duplicate = copyDrawing({ ...drawing, x: node.x(), y: node.y() }, 0, 0)
      node.position({ x: drawing.x ?? 0, y: drawing.y ?? 0 })
      this.copyPreview = null
      this.$emit('add', duplicate)
      this.selectedId = duplicate.id
    },
    pick(id: string) {
      const target = this.drawings.find((drawing) => drawing.id === id)
      if (!target || !isCurrentDrawing(target, this.activeStage)) return
      if (this.tool === 'copy') {
        const drawing = this.drawings.find((item) => item.id === id)
        if (drawing) this.$emit('add', copyDrawing(drawing))
      }
      if (this.tool === 'erase') this.$emit('erase', id)
      if (this.tool === 'select') this.selectedId = id
      if (this.tool === 'fill') {
        const drawing = this.drawings.find((item) => item.id === id)
        if (drawing && drawing.kind !== 'line' && drawing.fill !== this.fillColor)
          this.$emit('update', { ...drawing, fill: this.fillColor })
      }
    },
    groupConfig(drawing: Drawing) {
      return {
        id: `drawing-${drawing.id}`,
        draggable:
          this.tool === 'select' &&
          isCurrentDrawing(drawing, this.activeStage) &&
          drawing.id !== this.copyPreview?.id,
        listening:
          isCurrentDrawing(drawing, this.activeStage) && drawing.id !== this.copyPreview?.id,
        x: drawing.x ?? 0,
        y: drawing.y ?? 0,
        scaleX: drawing.scaleX ?? 1,
        scaleY: drawing.scaleY ?? 1,
        rotation: drawing.rotation ?? 0,
      }
    },
    attachTransformer() {
      const stage = (this.$refs.stage as NodeRef<Konva.Stage> | undefined)?.getNode()
      const transformer = (
        this.$refs.transformer as NodeRef<Konva.Transformer> | undefined
      )?.getNode()
      if (!stage || !transformer) return
      const node =
        this.selectedId && this.tool === 'select' && this.showHuman
          ? stage.findOne(`#drawing-${this.selectedId}`)
          : null
      transformer.nodes(node ? [node] : [])
      transformer.forceUpdate()
      transformer.getLayer()?.batchDraw()
    },
    saveTransform(drawing: Drawing, event: KonvaEventObject<Event>) {
      const node = event.target
      const updated = {
        ...drawing,
        x: node.x(),
        y: node.y(),
        scaleX: node.scaleX(),
        scaleY: node.scaleY(),
        rotation: node.rotation(),
      }
      if (
        updated.x !== (drawing.x ?? 0) ||
        updated.y !== (drawing.y ?? 0) ||
        updated.scaleX !== (drawing.scaleX ?? 1) ||
        updated.scaleY !== (drawing.scaleY ?? 1) ||
        updated.rotation !== (drawing.rotation ?? 0)
      )
        this.$emit('update', updated)
    },
    lineConfig(drawing: Drawing) {
      return {
        points: drawing.points,
        closed: drawing.kind === 'pen' && !!drawing.fill && drawing.fill !== 'transparent',
        fill: drawing.fill,
        ...drawingStroke(drawing),
        lineCap: 'round',
        lineJoin: 'round',
        hitStrokeWidth: 15,
      }
    },
    shapeConfig(drawing: Drawing) {
      const [x, y, endX, endY] = drawing.points
      return {
        x: Math.min(x, endX),
        y: Math.min(y, endY),
        fill: drawing.fill || 'rgba(0,0,0,0)',
        hitStrokeWidth: 15,
        width: Math.abs(endX - x),
        height: Math.abs(endY - y),
        ...drawingStroke(drawing),
      }
    },
    ellipseConfig(drawing: Drawing) {
      const rect = this.shapeConfig(drawing)
      return {
        x: rect.x + rect.width / 2,
        y: rect.y + rect.height / 2,
        fill: drawing.fill || 'rgba(0,0,0,0)',
        hitStrokeWidth: 15,
        radiusX: rect.width / 2,
        radiusY: rect.height / 2,
        ...drawingStroke(drawing),
      }
    },
  },
})
</script>
