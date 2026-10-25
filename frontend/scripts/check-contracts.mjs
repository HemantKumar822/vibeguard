import { readFileSync, mkdtempSync, unlinkSync, rmdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve, join } from 'node:path'
import { spawnSync } from 'node:child_process'

const frontend = resolve(import.meta.dirname, '..')
function run(command, args) {
  const result = spawnSync(command, args, { cwd: frontend, encoding: 'utf8' })
  if (result.error) throw result.error
  if (result.status !== 0) throw new Error(result.stderr || result.stdout || 'Contract command failed')
}
run('uv', ['run', 'python', '../scripts/contracts/export.py', '--check'])
const directory = mkdtempSync(join(tmpdir(), 'vibeguard-types-'))
const generated = join(directory, 'api.ts')
let failure
try {
  run(process.execPath, ['node_modules/openapi-typescript/bin/cli.js', '../contracts/openapi.json', '-o', generated])
  const normalize = value => value.replaceAll('\r\n', '\n')
  if (normalize(readFileSync(generated, 'utf8')) !== normalize(readFileSync(join(frontend, 'src/shared/api/generated.ts'), 'utf8'))) {
    throw new Error('Generated API types are stale. Run generate:types and commit the result.')
  }
  console.log('PASS: OpenAPI, API types and typed fixtures match their sources.')
} catch (error) { failure = error }
try {
  try { unlinkSync(generated) } catch (error) { if (error.code !== 'ENOENT') failure ??= error }
  rmdirSync(directory)
} catch (error) { failure ??= error }
if (failure) throw failure
