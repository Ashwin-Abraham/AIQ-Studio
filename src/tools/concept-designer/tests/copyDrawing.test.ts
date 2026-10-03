import { describe, expect, it } from 'vitest'
import { copyDrawing } from '../src/copyDrawing'
import { recordDrawingChange, undoDrawings, redoDrawings } from '../src/drawingHistory'
import type { Drawing } from '../src/models/Drawing'
import type { DrawingHistory } from '../src/models/DrawingHistory'

const source: Drawing = {
  id: 'original',
  kind: 'rectangle',
  points: [10, 20, 100, 80],
  x: 15,
  y: 30,
  rotation: 45,
  scaleX: 2,
  fill: '#ff0000',
  lineType: 'dashed',
}

describe('copy drawing', () => {
  it('offsets the copy without changing geometry, style or the original', () => {
    const copy = copyDrawing(source)
    expect(copy).toEqual({ ...source, id: copy.id, x: 39, y: 54 })
    expect(copy.id).not.toBe(source.id)
    copy.points[0] = 500
    expect(source.points[0]).toBe(10)
  })
  it('preserves the drag destination without adding the toolbar offset', () => {
    const copy = copyDrawing({ ...source, x: 150, y: 200 }, 0, 0)
    expect([copy.x, copy.y]).toEqual([150, 200])
    expect([source.x, source.y]).toEqual([15, 30])
  })
  it('undoes and redoes a copy as one action while preserving the original', () => {
    const history: DrawingHistory = { past: [], future: [] }
    const copy = copyDrawing(source)
    recordDrawingChange(history, [source])
    const undone = undoDrawings(history, [source, copy])
    expect(undone).toEqual([source])
    expect(redoDrawings(history, undone)).toEqual([source, copy])
  })
})
