import type { DesignOption } from './models/DesignOption'
import type { Drawing } from './models/Drawing'
import type { DrawingHistory } from './models/DrawingHistory'
import { recordDrawingChange, undoDrawings, redoDrawings } from './drawingHistory'

export function isCurrentDrawing(drawing: Drawing, stage: number): boolean {
  return (drawing.stage ?? 0) === stage
}

export function visibleStageDrawings(drawings: Drawing[], stage: number): Drawing[] {
  return drawings.filter((drawing) => (drawing.stage ?? 0) <= stage)
}

/** Keep every other stage unchanged, including stages hidden from the canvas. */
function replaceStage(drawings: Drawing[], stage: number, current: Drawing[]): Drawing[] {
  return [...drawings.filter((drawing) => !isCurrentDrawing(drawing, stage)), ...current].sort(
    (a, b) => (a.stage ?? 0) - (b.stage ?? 0),
  )
}

export function changeStageDrawings(
  drawings: Drawing[],
  stage: number,
  history: DrawingHistory,
  next: Drawing[],
): Drawing[] {
  recordDrawingChange(
    history,
    drawings.filter((drawing) => isCurrentDrawing(drawing, stage)),
  )
  return replaceStage(
    drawings,
    stage,
    next.filter((drawing) => isCurrentDrawing(drawing, stage)),
  )
}

export function travelStageHistory(
  drawings: Drawing[],
  stage: number,
  history: DrawingHistory,
  direction: 'undo' | 'redo',
): Drawing[] {
  const current = drawings.filter((drawing) => isCurrentDrawing(drawing, stage))
  const travel = direction === 'undo' ? undoDrawings : redoDrawings
  return replaceStage(drawings, stage, travel(history, current))
}

/** Append a stage and select it. Existing stage ownership stays unchanged. */
export function appendStage(option: DesignOption, name: string): DesignOption {
  const title = name.trim().slice(0, 40)
  if (!title) return option
  return {
    ...option,
    stage: option.stageNames.length,
    stageNames: [...option.stageNames, title],
    stageIds: [...option.stageIds, crypto.randomUUID()],
  }
}

/** Remove a stage and remap all surviving geometry and history to its new position. */
export function removeStage(
  option: DesignOption,
  histories: Record<string, DrawingHistory>,
  index: number,
) {
  if (option.stageNames.length <= 1 || index < 0 || index >= option.stageNames.length)
    return { option, histories }
  const remap = (drawings: Drawing[]) =>
    drawings
      .filter((drawing) => (drawing.stage ?? 0) !== index)
      .map((drawing) => ({
        ...drawing,
        stage: (drawing.stage ?? 0) > index ? (drawing.stage ?? 0) - 1 : (drawing.stage ?? 0),
      }))
  const nextHistories = { ...histories }
  option.stageNames.forEach((_, stage) => {
    delete nextHistories[`${option.id}-${stage}`]
  })
  option.stageNames.forEach((_, stage) => {
    if (stage === index) return
    const history = histories[`${option.id}-${stage}`] ?? { past: [], future: [] }
    nextHistories[`${option.id}-${stage > index ? stage - 1 : stage}`] = {
      past: history.past.map(remap),
      future: history.future.map(remap),
    }
  })
  const overlays = Object.fromEntries(
    Object.entries(option.overlays)
      .filter(([stage]) => Number(stage) !== index)
      .map(([stage, source]) => [
        Number(stage) > index ? Number(stage) - 1 : Number(stage),
        source,
      ]),
  )
  const activeStage =
    option.stage > index
      ? option.stage - 1
      : option.stage === index
        ? Math.max(0, index - 1)
        : option.stage
  return {
    option: {
      ...option,
      stage: activeStage,
      stageNames: option.stageNames.filter((_, stage) => stage !== index),
      stageIds: option.stageIds.filter((_, stage) => stage !== index),
      drawings: remap(option.drawings),
      overlays,
    },
    histories: nextHistories,
  }
}
