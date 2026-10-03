import { describe, expect, it } from 'vitest'
import { moveDrawing, recordDrawingChange, redoDrawings, undoDrawings } from '../src/drawingHistory'
import type { Drawing } from '../src/models/Drawing'
import type { DrawingHistory } from '../src/models/DrawingHistory'

describe('drawing history', () => {
  it('preserves transforms and fill through undo and redo', () => {
    const history: DrawingHistory = { past: [], future: [] }
    const original: Drawing = { id: 'shape', kind: 'rectangle', points: [0, 0, 50, 80] }
    const edited: Drawing = {
      ...original,
      x: 30,
      y: 45,
      rotation: 35,
      scaleX: 2,
      scaleY: 0.5,
      fill: '#cbdcba',
    }
    recordDrawingChange(history, [original])
    const restored = undoDrawings(history, [edited])
    expect(restored).toEqual([original])
    expect(redoDrawings(history, restored)).toEqual([edited])
  })
  it('restores additions, moves and erasures in order', () => {
    const history: DrawingHistory = { past: [], future: [] }
    const drawing: Drawing = { id: 'a', kind: 'line', points: [10, 20, 30, 40] }
    recordDrawingChange(history, [])
    recordDrawingChange(history, [drawing])
    const moved = moveDrawing(drawing, 5, -10)
    expect(moved.points).toEqual([15, 10, 35, 30])
    expect(drawing.points).toEqual([10, 20, 30, 40])
    recordDrawingChange(history, [moved])
    let current = undoDrawings(history, [])
    expect(current).toEqual([moved])
    current = undoDrawings(history, current)
    expect(current).toEqual([drawing])
    current = undoDrawings(history, current)
    expect(current).toEqual([])
    current = redoDrawings(history, current)
    current = redoDrawings(history, current)
    expect(current).toEqual([moved])
    expect(redoDrawings(history, current)).toEqual([])
  })
  it('clears redo after a new edit and keeps histories independent', () => {
    const first: DrawingHistory = { past: [], future: [] }
    const second: DrawingHistory = { past: [], future: [] }
    recordDrawingChange(first, [])
    undoDrawings(first, [{ id: 'a', kind: 'text', points: [1, 2], text: 'Note' }])
    expect(first.future).toHaveLength(1)
    recordDrawingChange(first, [])
    expect(first.future).toEqual([])
    expect(second).toEqual({ past: [], future: [] })
  })
})
