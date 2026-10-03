import type { Drawing } from './Drawing'

export interface DesignOption {
  id: string
  name: string
  stage: number
  stageIds: string[]
  stageNames: string[]
  drawings: Drawing[]
  overlays: Record<number, string>
  messages: { id: string; text: string }[]
}
