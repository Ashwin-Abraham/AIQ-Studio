import type { Drawing } from './models/Drawing'

export function drawingStroke(drawing: Drawing) {
  const width = drawing.strokeWidth ?? (drawing.kind === 'text' ? 0 : 3)
  return {
    stroke: drawing.stroke ?? '#224d45',
    strokeWidth: width,
    strokeScaleEnabled: false,
    dash:
      drawing.lineType === 'dashed'
        ? [width * 4, width * 3]
        : drawing.lineType === 'dotted'
          ? [0.1, width * 2.5]
          : [],
    lineCap: 'round' as const,
  }
}

export function defaultFill(drawing: Drawing): string {
  return (
    drawing.fill ??
    (drawing.kind === 'text' || drawing.kind === 'arrow' ? '#224d45' : 'transparent')
  )
}
