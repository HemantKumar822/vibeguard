import { useState } from 'react'
import { fixtures } from './generated/fixtures'

export default function DevelopmentFixtures() {
  const [index, setIndex] = useState(0)
  return <section className="panel" aria-labelledby="fixture-title">
    <p className="eyebrow">Development only — synthetic contract data</p>
    <h2 id="fixture-title">Boundary fixtures</h2>
    <p>These examples test shared data shapes. They are not scanner output.</p>
    <label htmlFor="fixture">Example state</label>
    <select id="fixture" value={index} onChange={e => setIndex(Number(e.target.value))}>
      {fixtures.map((fixture, i) => <option key={fixture.name} value={i}>{fixture.name}</option>)}
    </select>
    <pre aria-label="Synthetic fixture payload">{JSON.stringify(fixtures[index].data, null, 2)}</pre>
  </section>
}
