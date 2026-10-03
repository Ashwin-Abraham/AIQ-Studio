// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import { createOptions } from '../src/designSession'
import { validateSvg } from '../src/designFiles'

describe('design session', () => {
  it('keeps drawings, stages and conversations separate for each option', () => {
    const options = createOptions()
    options[0].drawings.push({ id: 'line', kind: 'line', points: [0, 0, 10, 10] })
    options[0].messages.push({ id: 'note', text: 'Keep the courtyard open.' })
    options[0].stage = 3
    expect(options).toHaveLength(3)
    expect(new Set(options.map((option) => option.id)).size).toBe(3)
    expect(options[1].drawings).toEqual([])
    expect(options[1].messages).toEqual([])
    expect(options[1].stage).toBe(0)
  })
  it('accepts a plain vector overlay', () => {
    const source =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600"><path d="M 0 0 L 10 10"/></svg>'
    expect(validateSvg(source)).toBe(source)
  })
  it.each([
    '<svg viewBox="0 0 100 100"><script>alert(1)</script></svg>',
    '<svg viewBox="0 0 100 100" onload="alert(1)"/>',
    '<svg viewBox="0 0 100 100"><image href="https://example.com/tracker"/></svg>',
    '<svg><path/></svg>',
    '<svg viewBox="0 0 100 100"><rect fill="url(https://example.com/a)"/></svg>',
    '<svg><broken>',
  ])('rejects invalid or external SVG content', (source) => {
    expect(() => validateSvg(source)).toThrow()
  })
})
