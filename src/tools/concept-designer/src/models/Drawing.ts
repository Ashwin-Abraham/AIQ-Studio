export interface Drawing {
  /** Zero-based creation stage. Older drawings without a stage belong to stage 1. */
  stage?: number
  id: string
  kind: 'pen' | 'arrow' | 'line' | 'rectangle' | 'circle' | 'text'
  points: number[]
  x?: number
  y?: number
  scaleX?: number
  scaleY?: number
  rotation?: number
  fill?: string
  stroke?: string
  strokeWidth?: number
  lineType?: 'solid' | 'dashed' | 'dotted'
  text?: string
}
