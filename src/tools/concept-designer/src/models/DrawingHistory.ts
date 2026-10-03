import type { Drawing } from './Drawing'

export interface DrawingHistory {
  past: Drawing[][]
  future: Drawing[][]
}
