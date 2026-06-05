import { useEffect, useState } from 'react'
import './App.css'
import ChainView from './ChainView'
import { getBuildings, postBalance } from './api'
import type { BalanceResponse, BuildingInput, CatalogBuilding, Settlement } from './types'

function App() {
  const [catalog, setCatalog] = useState<CatalogBuilding[] | null>(null)
  const [source, setSource] = useState('')
  const [verified, setVerified] = useState(true)
  const [population, setPopulation] = useState(10)
  const [buildings, setBuildings] = useState<BuildingInput[]>([])
  const [result, setResult] = useState<BalanceResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getBuildings()
      .then((data) => {
        setCatalog(data.buildings)
        setSource(data.source)
        setVerified(data.verified)
        if (data.buildings.length > 0) {
          setBuildings([newRow(data.buildings[0])])
        }
      })
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
  }, [])

  function newRow(building: CatalogBuilding): BuildingInput {
    return { type: building.id, level: building.levels[0].level, workers: 1, allocation: {} }
  }

  function findBuilding(id: string): CatalogBuilding | undefined {
    return catalog?.find((b) => b.id === id)
  }

  function updateRow(index: number, patch: Partial<BuildingInput>) {
    setBuildings((rows) => rows.map((row, i) => (i === index ? { ...row, ...patch } : row)))
  }

  function changeType(index: number, id: string) {
    const building = findBuilding(id)
    if (!building) return
    // level set and recipes differ per building, so reset both
    updateRow(index, { type: id, level: building.levels[0].level, allocation: {} })
  }

  function changeLevel(index: number, level: number) {
    // recipes may differ between levels, so the allocation is reset
    updateRow(index, { level, allocation: {} })
  }

  function setAlloc(index: number, output: string, percent: number) {
    setBuildings((rows) =>
      rows.map((row, i) =>
        i === index ? { ...row, allocation: { ...row.allocation, [output]: percent } } : row,
      ),
    )
  }

  function addBuilding() {
    if (catalog && catalog.length > 0) setBuildings((rows) => [...rows, newRow(catalog[0])])
  }

  function removeBuilding(index: number) {
    setBuildings((rows) => rows.filter((_, i) => i !== index))
  }

  async function compute() {
    setLoading(true)
    setError(null)
    const settlement: Settlement = { population, buildings }
    try {
      setResult(await postBalance(settlement))
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  if (error && !catalog) return <p className="error">{error}</p>
  if (!catalog) return <p className="note">Loading building catalog…</p>

  return (
    <main>
      <h1>Production Planner</h1>
      <p className="note">Base values, demand balance — no rationing.</p>
      {!verified && (
        <p className="warn">
          Placeholder data ({source}) — unverified, and recipe rates are not yet
          measured, so the balance can't be computed yet.
        </p>
      )}

      <section className="inputs">
        <label>
          Population
          <input
            type="number"
            min={0}
            value={population}
            onChange={(e) => setPopulation(Number(e.target.value))}
          />
        </label>

        {buildings.map((row, index) => {
          const building = findBuilding(row.type)
          const level = building?.levels.find((l) => l.level === row.level)
          const allocTotal = Object.values(row.allocation).reduce((a, b) => a + b, 0)
          return (
            <fieldset key={index}>
              <legend>Building {index + 1}</legend>
              <label>
                Type
                <select value={row.type} onChange={(e) => changeType(index, e.target.value)}>
                  {catalog.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.id}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Level
                <select
                  value={row.level}
                  onChange={(e) => changeLevel(index, Number(e.target.value))}
                >
                  {building?.levels.map((l) => (
                    <option key={l.level} value={l.level}>
                      {l.level}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Workers{level && level.max_workers != null ? ` (max ${level.max_workers})` : ''}
                <input
                  type="number"
                  min={0}
                  value={row.workers}
                  onChange={(e) => updateRow(index, { workers: Number(e.target.value) })}
                />
              </label>
              {level?.can_produce.map((recipe) => (
                <label key={recipe.output}>
                  {recipe.output} %
                  <input
                    type="number"
                    min={0}
                    value={row.allocation[recipe.output] ?? 0}
                    onChange={(e) => setAlloc(index, recipe.output, Number(e.target.value))}
                  />
                </label>
              ))}
              <p className={allocTotal > 100 ? 'warn' : ''}>allocation total: {allocTotal}%</p>
              <button type="button" onClick={() => removeBuilding(index)}>
                Remove building
              </button>
            </fieldset>
          )
        })}

        <button type="button" onClick={addBuilding}>
          Add building
        </button>

        <button onClick={compute} disabled={loading || buildings.length === 0}>
          {loading ? 'Computing…' : 'Compute balance'}
        </button>
      </section>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="results">
          {result.errors.length > 0 && (
            <ul className="validation">
              {result.errors.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          )}
          {result.rates_missing.length > 0 && (
            <p className="warn">
              Rate not measured yet for:{' '}
              {result.rates_missing.map((m) => `${m.building}/${m.output}`).join(', ')} —
              these produce 0 until a rate is entered.
            </p>
          )}
          <table>
            <thead>
              <tr>
                <th>resource</th>
                <th>produced</th>
                <th>demand</th>
                <th>balance</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(result.balance)
                .sort()
                .map((res) => (
                  <tr key={res} className={result.balance[res] < 0 ? 'deficit' : 'surplus'}>
                    <td>{res}</td>
                    <td>{(result.production[res] ?? 0).toFixed(1)}</td>
                    <td>{(result.demand[res] ?? 0).toFixed(1)}</td>
                    <td>{result.balance[res].toFixed(1)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </section>
      )}

      <section className="chain">
        <h2>Production chain</h2>
        <ChainView />
      </section>
    </main>
  )
}

export default App
