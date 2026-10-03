import type Konva from 'konva'

const cursorSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><path d="M24 13a9 9 0 1 0-1 10M24 6v7h-7" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M24 13a9 9 0 1 0-1 10M24 6v7h-7" fill="none" stroke="#285b4b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`
export const rotationCursor = `url("data:image/svg+xml,${encodeURIComponent(cursorSvg)}") 16 16, crosshair`

/** Keep Konva's rotation gesture and position; change only the icon and hit area. */
export function styleRotationAnchor(anchor: Konva.Rect): void {
  if (!anchor.hasName('rotater')) return
  anchor.setAttrs({
    width: 22,
    height: 22,
    offsetX: 11,
    offsetY: 11,
    stroke: '#b88645',
    strokeWidth: 2,
    fill: '#b88645',
  })
  anchor.sceneFunc((context, shape) => {
    context.beginPath()
    context.arc(11, 11, 7, -Math.PI / 4, Math.PI * 1.4)
    context.moveTo(16, 2)
    context.lineTo(16, 6)
    context.lineTo(12, 6)
    context.strokeShape(shape)
  })
  // A larger invisible target makes rotation available as the pointer approaches the corner.
  anchor.hitFunc((context, shape) => {
    context.beginPath()
    context.arc(11, 11, 17, 0, Math.PI * 2)
    context.closePath()
    context.fillStrokeShape(shape)
  })
}
