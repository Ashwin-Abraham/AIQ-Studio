import type { Drawing } from './models/Drawing'
import type { DesignOption } from './models/DesignOption'
import { canvasSize } from './designSession'

export function validateSvg(source: string): string {
  const document = new DOMParser().parseFromString(source, 'image/svg+xml')
  const root = document.documentElement
  if (root.localName !== 'svg' || document.querySelector('parsererror')) {
    throw new Error('Select a valid SVG file.')
  }
  // Keep imported overlays self-contained. Render them as images, never as page HTML.
  const allowed = new Set([
    'svg',
    'g',
    'path',
    'rect',
    'circle',
    'ellipse',
    'line',
    'polyline',
    'polygon',
    'text',
    'tspan',
    'defs',
    'marker',
    'title',
    'desc',
  ])
  for (const element of [root, ...root.querySelectorAll('*')]) {
    if (!allowed.has(element.localName))
      throw new Error(`Unsupported SVG element: ${element.localName}. Use plain vector shapes.`)
    for (const attribute of [...element.attributes]) {
      if (
        /^on/i.test(attribute.name) ||
        /href/i.test(attribute.name) ||
        /url\s*\(\s*[^#]/i.test(attribute.value) ||
        /@import/i.test(attribute.value)
      ) {
        throw new Error('Use an SVG with local shapes and no external content.')
      }
    }
  }
  if (!root.hasAttribute('viewBox'))
    throw new Error('The SVG needs a viewBox to align with the canvas.')
  return source
}

export function loadImage(source: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = () => reject(new Error('The image could not be read.'))
    image.src = source
  })
}

export function readFile(file: File): Promise<string> {
  if (file.size > 10 * 1024 * 1024) throw new Error('Use a file smaller than 10 MB.')
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error('The file could not be read.'))
    reader.readAsDataURL(file)
  })
}

export function svgImageSource(svg: string): string {
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
}

export function boundaryImageSource(drawings: Drawing[]): string {
  const lines = drawings
    .map(
      (drawing) =>
        `<polyline points="${drawing.points.join(' ')}" fill="none" stroke="#8c9688" stroke-width="3"/>`,
    )
    .join('')
  return svgImageSource(
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">${lines}</svg>`,
  )
}

export async function readBaseFile(file: File, kind: string): Promise<string> {
  const source = await readFile(file)
  if (kind === 'Site boundary') return svgImageSource(validateSvg(await file.text()))
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type))
    throw new Error('Select a PNG, JPEG or WebP sketch.')
  return source
}

export async function readOverlayFile(file: File): Promise<string> {
  if (file.size > 10 * 1024 * 1024) throw new Error('Use a file smaller than 10 MB.')
  return validateSvg(await file.text())
}

export function exportDesignSession(
  baseName: string,
  baseSource: string | null,
  options: DesignOption[],
  activeId: string,
): void {
  const data = {
    version: 2,
    canvas: canvasSize,
    base: { name: baseName, source: baseSource },
    options,
    activeId,
  }
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }),
  )
  const link = document.createElement('a')
  link.href = url
  link.download = 'concept-session.json'
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
