import { appendStage, removeStage } from '../src/stageTimeline'
import { describe, expect, it } from 'vitest'
import { createOptions } from '../src/designSession'
import {
  changeStageDrawings,
  isCurrentDrawing,
  travelStageHistory,
  visibleStageDrawings,
} from '../src/stageTimeline'
import { copyDrawing } from '../src/copyDrawing'
import type { Drawing } from '../src/models/Drawing'
import type { DrawingHistory } from '../src/models/DrawingHistory'

const shape = (id: string, stage: number): Drawing => ({
  id,
  stage,
  kind: 'rectangle',
  points: [0, 0, 40, 40],
})
const history = (): DrawingHistory => ({ past: [], future: [] })

describe('stage timeline', () => {
  it('starts at stage 1 with names based on the base choice', () => {
    expect(createOptions(true)[0].stageNames).toEqual(['Base', 'Develop'])
    expect(createOptions(false)[0].stageNames).toEqual(['Develop'])
    expect(createOptions()[0].stage).toBe(0)
  })
  it('shows earlier drawings, hides future drawings, and edits only the current stage', () => {
    const drawings = [shape('past', 0), shape('now', 1), shape('future', 2)]
    expect(visibleStageDrawings(drawings, 1).map((drawing) => drawing.id)).toEqual(['past', 'now'])
    expect(drawings.map((drawing) => isCurrentDrawing(drawing, 1))).toEqual([false, true, false])
    expect(visibleStageDrawings(drawings, 0)).toEqual([drawings[0]])
    expect(visibleStageDrawings(drawings, 2)).toEqual(drawings)
  })
  it('preserves locked and hidden stages even when a caller submits replacements', () => {
    const drawings = [shape('past', 0), shape('now', 1), shape('future', 2)]
    const changed = changeStageDrawings(drawings, 1, history(), [
      { ...drawings[0], fill: 'red' },
      { ...drawings[1], fill: 'blue' },
    ])
    expect(changed).toEqual([drawings[0], { ...drawings[1], fill: 'blue' }, drawings[2]])
  })
  it('keeps undo and redo isolated when users move backwards and forwards in time', () => {
    const first = history(),
      second = history()
    let drawings = changeStageDrawings([], 0, first, [shape('first', 0)])
    drawings = changeStageDrawings(drawings, 1, second, [shape('second', 1)])
    drawings = travelStageHistory(drawings, 0, first, 'undo')
    expect(drawings.map((drawing) => drawing.id)).toEqual(['second'])
    drawings = travelStageHistory(drawings, 0, first, 'redo')
    drawings = travelStageHistory(drawings, 1, second, 'undo')
    expect(drawings.map((drawing) => drawing.id)).toEqual(['first'])
    drawings = travelStageHistory(drawings, 1, second, 'redo')
    expect(drawings.map((drawing) => drawing.id)).toEqual(['first', 'second'])
  })
  it('keeps copied shapes in their creation stage through undo and redo', () => {
    const original = shape('original', 2)
    const duplicate = copyDrawing(original)
    const edits = history()
    let drawings = changeStageDrawings([original], 2, edits, [original, duplicate])
    expect(visibleStageDrawings(drawings, 1)).toEqual([])
    drawings = travelStageHistory(drawings, 2, edits, 'undo')
    expect(drawings).toEqual([original])
    expect(travelStageHistory(drawings, 2, edits, 'redo')).toEqual([original, duplicate])
  })
  it('treats older drawings without stage metadata as stage 1', () => {
    const legacy: Drawing = { id: 'legacy', kind: 'line', points: [0, 0, 20, 20] }
    expect(isCurrentDrawing(legacy, 0)).toBe(true)
    expect(isCurrentDrawing(legacy, 1)).toBe(false)
    expect(visibleStageDrawings([legacy], 0)).toEqual([legacy])
  })
})

describe('stage management', () => {
  it('adds named stages after the initial stage with a stable ID and selects them', () => {
    const option = createOptions()[0]
    const next = appendStage(option, '  Courtyard  ')
    expect(next.stage).toBe(1)
    expect(next.stageNames[1]).toBe('Courtyard')
    expect(new Set(next.stageIds).size).toBe(2)
    expect(next.stageIds.slice(0, 1)).toEqual(option.stageIds)
    expect(appendStage(option, '   ')).toBe(option)
  })
  it('deletes only the requested stage and preserves later-stage ownership and undo', () => {
    const option = appendStage(createOptions(true)[0], 'Review')
    option.stage = 2
    option.drawings = [shape('early', 0), shape('removed', 1), shape('later', 2)]
    option.overlays = { 0: 'early SVG', 1: 'removed SVG', 2: 'later SVG' }
    const laterHistory = { past: [[], [shape('later', 2)]], future: [[shape('redo', 2)]] }
    const histories = { [`${option.id}-2`]: laterHistory, otherOption: history() }
    const result = removeStage(option, histories, 1)
    expect(result.option.stage).toBe(1)
    expect(result.option.stageIds[1]).toBe(option.stageIds[2])
    expect(result.option.drawings).toEqual([shape('early', 0), shape('later', 1)])
    expect(result.option.overlays).toEqual({ 0: 'early SVG', 1: 'later SVG' })
    expect(result.histories.otherOption).toBe(histories.otherOption)
    const edits = result.histories[`${option.id}-1`]
    expect(edits.future).toEqual([[shape('redo', 1)]])
    expect(travelStageHistory(result.option.drawings, 1, edits, 'redo')).toEqual([
      shape('early', 0),
      shape('redo', 1),
    ])
    expect(option.drawings[2].stage).toBe(2)
  })
  it('selects the previous stage on active deletion and retains at least one stage', () => {
    let option = appendStage(createOptions(true)[0], 'Review')
    option = removeStage(option, {}, 2).option
    expect(option.stage).toBe(1)
    while (option.stageNames.length > 1) option = removeStage(option, {}, 0).option
    expect(option.stage).toBe(0)
    expect(removeStage(option, {}, 0).option).toBe(option)
  })
})
