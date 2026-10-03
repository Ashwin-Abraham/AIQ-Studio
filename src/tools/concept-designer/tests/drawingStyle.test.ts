import { describe, expect, it } from 'vitest'
import { defaultFill, drawingStroke } from '../src/drawingStyle'
import type { Drawing } from '../src/models/Drawing'

const shape: Drawing = { id: 'shape', kind: 'rectangle', points: [0, 0, 10, 10] }

describe('shape styles', () => {
  it('keeps existing shapes and text appearance compatible', () => {
    expect(drawingStroke(shape).strokeWidth).toBe(3)
    expect(defaultFill(shape)).toBe('transparent')
    expect(drawingStroke({ ...shape, kind: 'text' }).strokeWidth).toBe(0)
    expect(defaultFill({ ...shape, kind: 'text' })).toBe('#224d45')
  })
  it('supports explicit no fill and zero line thickness', () => {
    expect(defaultFill({ ...shape, kind: 'arrow', fill: 'transparent' })).toBe('transparent')
    expect(drawingStroke({ ...shape, strokeWidth: 0 }).strokeWidth).toBe(0)
  })
  it('scales dash spacing with line thickness and keeps strokes independent of shape scale', () => {
    const stroke = drawingStroke({
      ...shape,
      stroke: '#ff0000',
      strokeWidth: 4,
      lineType: 'dashed',
    })
    expect(stroke.stroke).toBe('#ff0000')
    expect(stroke.dash).toEqual([16, 12])
    expect(stroke.strokeScaleEnabled).toBe(false)
    expect(drawingStroke({ ...shape, lineType: 'dotted' }).dash).toEqual([0.1, 7.5])
    expect(drawingStroke(shape).dash).toEqual([])
  })
})
