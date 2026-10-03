import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'

const destination = new URL('../../../../.agents/skills/concept-design/assets/', import.meta.url)
mkdirSync(fileURLToPath(destination), { recursive: true })
const build = new URL('../dist/', import.meta.url)
let html = readFileSync(new URL('index.html', build), 'utf8')
html = html.replace(/<script[^>]*src="([^"]+)"[^>]*><\/script>/g, (_tag, path) => {
  const script = readFileSync(new URL(path, build), 'utf8').replace(/<\/script/gi, '<\\/script')
  return `<script type="module">${script}</script>`
})
html = html.replace(/<link[^>]*href="([^"]+\.css)"[^>]*>/g, (_tag, path) => {
  return `<style>${readFileSync(new URL(path, build), 'utf8')}</style>`
})
writeFileSync(new URL('concept-designer.html', destination), html)
