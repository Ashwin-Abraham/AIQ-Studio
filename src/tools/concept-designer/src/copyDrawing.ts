import type { Drawing } from './models/Drawing'

/** Offset in canvas coordinates, independent of shape rotation and scale. */
export function copyDrawing(drawing: Drawing, offsetX = 24, offsetY = 24): Drawing {
  return {
    ...drawing,
    id: crypto.randomUUID(),
    points: [...drawing.points],
    x: (drawing.x ?? 0) + offsetX,
    y: (drawing.y ?? 0) + offsetY,
  }
}
