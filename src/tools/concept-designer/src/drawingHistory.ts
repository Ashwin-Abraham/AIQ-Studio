import type { Drawing } from './models/Drawing'
import type { DrawingHistory } from './models/DrawingHistory'

function copy(drawings: Drawing[]): Drawing[] {
  return drawings.map((drawing) => ({ ...drawing, points: [...drawing.points] }))
}

export function recordDrawingChange(history: DrawingHistory, current: Drawing[]): void {
  history.past.push(copy(current))
  history.future = []
}

export function undoDrawings(history: DrawingHistory, current: Drawing[]): Drawing[] {
  const previous = history.past.pop()
  if (!previous) return current
  history.future.push(copy(current))
  return previous
}

export function redoDrawings(history: DrawingHistory, current: Drawing[]): Drawing[] {
  const next = history.future.pop()
  if (!next) return current
  history.past.push(copy(current))
  return next
}

export function moveDrawing(drawing: Drawing, x: number, y: number): Drawing {
  return { ...drawing, points: drawing.points.map((point, index) => point + (index % 2 ? y : x)) }
}
