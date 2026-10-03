import type { DesignOption } from './models/DesignOption'

export const canvasSize = { width: 1000, height: 600 }

export function createOptions(hasBase = false): DesignOption[] {
  const stages = hasBase ? ['Base', 'Develop'] : ['Develop']
  return ['01', '02', '03'].map((number) => ({
    id: crypto.randomUUID(),
    name: `Option ${number}`,
    stage: 0,
    stageIds: stages.map(() => crypto.randomUUID()),
    stageNames: [...stages],
    drawings: [],
    overlays: {},
    messages: [],
  }))
}
