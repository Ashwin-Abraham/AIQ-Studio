// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h, nextTick, type PropType } from 'vue'
import { mount, type VueWrapper } from '@vue/test-utils'
import ConceptDesigner from '../src/ConceptDesigner.vue'
import DesignCanvas from '../src/components/DesignCanvas.vue'
import type { Drawing } from '../src/models/Drawing'

// Replace only the renderer. Real Vue components, DOM controls, and event listeners stay mounted.
// This does not test Konva hit detection or native browser colour/dialog behaviour.
const renderer = (name: string) =>
  defineComponent({
    name,
    props: { config: { type: Object as PropType<Record<string, unknown>>, default: () => ({}) } },
    methods: {
      getNode() {
        return { findOne: () => ({}), nodes: () => {}, forceUpdate: () => {}, getLayer: () => null }
      },
    },
    render() {
      return h('div', this.$slots.default?.())
    },
  })
const rendererNames = [
  'Stage',
  'Layer',
  'Image',
  'Group',
  'Line',
  'Arrow',
  'Rect',
  'Ellipse',
  'Text',
  'Transformer',
]
const stubs = Object.fromEntries(rendererNames.map((name) => [`V${name}`, renderer(`V${name}`)]))
let app: VueWrapper

beforeEach(() => {
  vi.stubGlobal(
    'ResizeObserver',
    class {
      constructor(private callback: (entries: unknown[]) => void) {}
      observe() {
        this.callback([{ contentRect: { width: 500 } }])
      }
      disconnect() {}
    },
  )
  // jsdom has no native modal dialog implementation.
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute('open', '')
  }
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute('open')
  }
})
afterEach(() => {
  app?.unmount()
  vi.unstubAllGlobals()
  document.body.innerHTML = ''
})

async function start() {
  app = mount(ConceptDesigner, { attachTo: document.body, global: { stubs } })
  const blank = app.findAll('button').find((button) => button.text().includes('No base'))!
  await blank.trigger('click')
}
const canvas = () => app.findComponent(DesignCanvas)
const drawings = () => canvas().props('drawings') as Drawing[]
const stage = () => canvas().findComponent({ name: 'VStage' })
const groups = () => canvas().findAllComponents({ name: 'VGroup' })
async function tool(name: string) {
  await app.get(`button[aria-label="${name}"]`).trigger('click')
}
async function pointer(event: string, x: number, y: number, button = 0) {
  const surface = {
    getStage: () => surface,
    getPointerPosition: () => ({ x, y }),
    scaleX: () => 0.5,
    scaleY: () => 0.5,
  }
  stage().vm.$emit(event, { target: surface, evt: { button, altKey: false } })
  await nextTick()
}
async function draw(name = 'Rectangle') {
  await tool(name)
  await pointer('pointerdown', 50, 60)
  await pointer('pointermove', 100, 120)
  await pointer('pointerup', 100, 120)
}
async function pick(index = 0) {
  groups()[index].vm.$emit('pointerdown')
  await nextTick()
}
async function addStage(name: string) {
  await app.get('button[aria-label="Add stage"]').trigger('click')
  await app.get('#new-stage-name').setValue(name)
  await app.get('dialog form').trigger('submit')
}

describe('workspace user actions', () => {
  it.each(['Pen', 'Line', 'Arrow', 'Rectangle', 'Circle'])(
    '%s creates one correctly scaled drawing, returns to Select, and supports undo/redo',
    async (name) => {
      await start()
      await tool(name)
      await pointer('pointerdown', 50, 60)
      await pointer('pointermove', 100, 120)
      expect(drawings()).toHaveLength(0) // The unfinished gesture is not yet saved.
      expect(app.get(`button[aria-label="${name}"]`).attributes('aria-pressed')).toBe('true')
      await pointer('pointerup', 100, 120)
      expect(drawings()).toHaveLength(1)
      expect(drawings()[0].points.slice(0, 2)).toEqual([100, 120])
      expect(drawings()[0].points.slice(-2)).toEqual([200, 240])
      expect(app.get('button[aria-label="Select"]').attributes('aria-pressed')).toBe('true')
      const saved = [...drawings()[0].points]
      await pointer('pointerdown', 150, 150)
      await pointer('pointerup', 150, 150)
      expect(drawings()).toHaveLength(1) // A second click must not repeat the tool.
      await tool('Undo')
      expect(drawings()).toHaveLength(0)
      await tool('Redo')
      expect(drawings()[0].points).toEqual(saved)
    },
  )

  it('previews text without saving it, then stamps once and clears the preview', async () => {
    await start()
    await tool('Text')
    await app.get('.text-label input').setValue('Courtyard')
    await pointer('pointermove', 40, 50)
    const preview = canvas().findComponent({ name: 'VText' }).props('config')
    expect(preview.text).toBe('Courtyard')
    expect(preview.opacity).toBeGreaterThan(0)
    expect(preview.opacity).toBeLessThan(0.5)
    expect(preview.x).toBeGreaterThan(80)
    expect(preview.listening).toBe(false)
    expect(drawings()).toHaveLength(0)
    await pointer('pointerleave', 40, 50)
    expect(canvas().findComponent({ name: 'VText' }).exists()).toBe(false)
    await pointer('pointerdown', 40, 50)
    await pointer('pointerup', 40, 50)
    expect(drawings()).toHaveLength(1)
    expect(drawings()[0]).toMatchObject({
      kind: 'text',
      text: 'Courtyard',
      points: [80, 100, 80, 100],
    })
    expect(canvas().findAllComponents({ name: 'VText' })).toHaveLength(1)
    expect(app.get('button[aria-label="Select"]').attributes('aria-pressed')).toBe('true')
  })

  it('copies, fills and erases once, with each action independently undoable', async () => {
    await start()
    await draw()
    const originalId = drawings()[0].id
    await tool('Copy')
    await pick()
    expect(drawings()).toHaveLength(2)
    expect(drawings()[1].id).not.toBe(originalId)
    expect(app.get('button[aria-label="Select"]').attributes('aria-pressed')).toBe('true')
    await tool('Fill')
    await app.get('input[aria-label="Fill colour"]').setValue('#ff0000')
    await pick(1)
    expect(drawings()[1].fill).toBe('#ff0000')
    expect(drawings()[0].fill).toBeUndefined()
    expect(app.get('button[aria-label="Select"]').attributes('aria-pressed')).toBe('true')
    await tool('Erase')
    await pick(1)
    expect(drawings().map((item) => item.id)).toEqual([originalId])
    expect(app.get('button[aria-label="Select"]').attributes('aria-pressed')).toBe('true')
    await tool('Undo')
    expect(drawings()[1].fill).toBe('#ff0000')
    await tool('Undo')
    expect(drawings()[1].fill).toBeUndefined()
    await tool('Undo')
    expect(drawings()).toHaveLength(1)
  })

  it('applies colour input before blur and protects the selected shape from Delete in a property field', async () => {
    await start()
    await draw()
    await pick()
    const fill = app.get('input[aria-label="Shape fill"]')
    ;(fill.element as HTMLInputElement).value = '#123456'
    await fill.trigger('input') // Deliberately no change or blur event.
    expect(drawings()[0].fill).toBe('#123456')
    await app.get('input[aria-label="Line thickness"]').trigger('keydown', { key: 'Delete' })
    expect(drawings()).toHaveLength(1)
    await app.get('[aria-label="Drawing canvas"]').trigger('keydown', { key: 'Delete' })
    expect(drawings()).toHaveLength(0)
    await tool('Undo')
    expect(drawings()[0].fill).toBe('#123456')
  })

  it('locks past shapes, hides future shapes, and keeps edits and undo scoped to each option and stage', async () => {
    await start()
    await draw()
    const first = drawings()[0].id
    await addStage('Review')
    await draw('Circle')
    expect(groups()).toHaveLength(2)
    expect(groups()[0].props('config')).toMatchObject({ listening: false, draggable: false })
    await tool('Erase')
    await pick(0) // Even a stray event must not edit a locked drawing.
    expect(drawings()).toHaveLength(2)
    await app.get('button[aria-label="Select stage 1: Develop"]').trigger('click')
    expect(groups()).toHaveLength(1)
    await tool('Undo')
    expect(drawings()).toHaveLength(1)
    expect(drawings()[0].kind).toBe('circle') // Hidden future stage survived Undo.
    await tool('Redo')
    expect(drawings().some((item) => item.id === first)).toBe(true)
    await app.get('.options-bar button:nth-child(2)').trigger('click')
    expect(drawings()).toHaveLength(0)
    expect(app.get('button[aria-label="Undo"]').attributes()).toHaveProperty('disabled')
    await app.get('.options-bar button:nth-child(1)').trigger('click')
    expect(drawings()).toHaveLength(2)
  })

  it('shows inactive names and requires selection before a second click can rename a stage', async () => {
    await start()
    await addStage('Review')
    expect(app.get('button[aria-label="Stage 1: Develop"]').text()).toBe('Develop')
    expect(app.find('.stage-entry input').exists()).toBe(false)
    await app.get('button[aria-label="Stage 1: Develop"]').trigger('click')
    expect(app.get('button[aria-label="Select stage 1: Develop"]').attributes('aria-current')).toBe(
      'step',
    )
    expect(app.find('.stage-entry input').exists()).toBe(false)
    await app.get('button[aria-label="Stage 1: Develop"]').trigger('click')
    const name = app.get('input[aria-label="Stage 1 name"]')
    expect(document.activeElement).toBe(name.element)
    await name.setValue('Courtyard')
    await name.trigger('blur')
    expect(app.get('button[aria-label="Stage 1: Courtyard"]').text()).toBe('Courtyard')
    expect(app.find('.stage-entry input').exists()).toBe(false)
    await app.get('button[aria-label="Stage 2: Review"]').trigger('click')
    expect(app.get('button[aria-label="Stage 1: Courtyard"]').text()).toBe('Courtyard')
    expect(app.find('.stage-entry input').exists()).toBe(false)
  })

  it('cancels stage deletion without changes, then removes only the confirmed stage', async () => {
    await start()
    await draw()
    await addStage('Review')
    await draw('Circle')
    await app.get('button[aria-label="Delete stage 2: Review"]').trigger('click')
    const dialog = app.get('dialog[aria-labelledby="delete-stage-title"]')
    await dialog.get('button').trigger('click')
    expect(drawings()).toHaveLength(2)
    expect(app.find('button[aria-label="Select stage 2: Review"]').exists()).toBe(true)
    await app.get('button[aria-label="Delete stage 2: Review"]').trigger('click')
    await dialog.get('button.primary').trigger('click')
    expect(drawings()).toHaveLength(1)
    expect(drawings()[0].kind).toBe('rectangle')
    expect(app.find('button[aria-label="Select stage 2: Review"]').exists()).toBe(false)
    expect(app.get('button[aria-label="Delete stage 1: Develop"]').attributes()).toHaveProperty(
      'disabled',
    )
    await tool('Undo')
    expect(drawings()).toHaveLength(0) // Surviving stage history still works.
  })

  it('Alt-drag creates one copy at the drop point, leaves the source in place, and undoes in one step', async () => {
    await start()
    await draw()
    const original = { ...drawings()[0], points: [...drawings()[0].points] }
    const group = groups()[0]
    let position = { x: 0, y: 0 }
    const node = {
      x: () => position.x,
      y: () => position.y,
      scaleX: () => 1,
      scaleY: () => 1,
      rotation: () => 0,
      position: (next: { x: number; y: number }) => {
        position = next
      },
    }
    group.vm.$emit('dragstart', { target: node, evt: { altKey: true } })
    await nextTick()
    expect(drawings()).toHaveLength(1) // The temporary source preview is not saved.
    position = { x: 90, y: 45 }
    group.vm.$emit('dragend', { target: node, evt: { altKey: false } })
    await nextTick()
    expect(drawings()).toHaveLength(2)
    expect(drawings()[0]).toEqual(original)
    expect(drawings()[1]).toMatchObject({ x: 90, y: 45, points: [100, 120, 200, 240] })
    expect(position).toEqual({ x: 0, y: 0 })
    await tool('Undo')
    expect(drawings()).toEqual([original])
    await tool('Redo')
    expect(drawings()).toHaveLength(2)
  })

  it('ignores right-click drawing and blocks drawing while the human layer is hidden', async () => {
    await start()
    await tool('Rectangle')
    await pointer('pointerdown', 10, 20, 2)
    await pointer('pointerup', 10, 20, 2)
    expect(drawings()).toHaveLength(0)
    await app.get('.layer-bar label:nth-of-type(3) input').setValue(false)
    await pointer('pointerdown', 10, 20)
    await pointer('pointermove', 40, 50)
    await pointer('pointerup', 40, 50)
    expect(drawings()).toHaveLength(0)
  })
})
