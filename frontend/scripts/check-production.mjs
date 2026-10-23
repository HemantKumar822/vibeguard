import { readdirSync, readFileSync } from 'node:fs'
import { resolve, join } from 'node:path'

const dist = resolve(import.meta.dirname, '../dist')
function inspect(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) { inspect(path); continue }
    if (!/\.(js|html)$/.test(entry.name)) continue
    const content = readFileSync(path, 'utf8')
    for (const marker of ['development-finding', 'Boundary fixtures', 'Synthetic fixture payload', 'fixture-title']) {
      if (content.includes(marker)) throw new Error(`Development fixture marker shipped in ${entry.name}: ${marker}`)
    }
  }
}
inspect(dist)
console.log('PASS: production assets exclude development fixtures and their selector.')
