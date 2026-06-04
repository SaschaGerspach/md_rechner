import { useState } from 'react'
import './App.css'
import { postBalance } from './api'
import type { BalanceResponse, Settlement } from './types'

const RECIPES = ['leinengarn', 'leinengewebe', 'einfaches_leinenhemd']

function App() {
  const [population, setPopulation] = useState(10)
  const [workers, setWorkers] = useState(2)
  const [allocation, setAllocation] = useState<Record<string, number>>({
    leinengarn: 50,
    leinengewebe: 30,
    einfaches_leinenhemd: 20,
  })
  const [result, setResult] = useState<BalanceResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const allocTotal = Object.values(allocation).reduce((a, b) => a + b, 0)

  async function compute() {
    setLoading(true)
    setError(null)
    const settlement: Settlement = {
      population,
      buildings: [{ type: 'sewing_hut', level: 3, workers, allocation }],
    }
    try {
      setResult(await postBalance(settlement))
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <h1>Production Planner</h1>
      <p className="note">Base values (level 3), demand balance — no rationing.</p>

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

        <fieldset>
          <legend>Sewing hut (level 3)</legend>
          <label>
            Workers
            <input
              type="number"
              min={0}
              value={workers}
              onChange={(e) => setWorkers(Number(e.target.value))}
            />
          </label>
          {RECIPES.map((recipe) => (
            <label key={recipe}>
              {recipe} %
              <input
                type="number"
                min={0}
                value={allocation[recipe]}
                onChange={(e) =>
                  setAllocation({ ...allocation, [recipe]: Number(e.target.value) })
                }
              />
            </label>
          ))}
          <p className={allocTotal > 100 ? 'warn' : ''}>allocation total: {allocTotal}%</p>
        </fieldset>

        <button onClick={compute} disabled={loading}>
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
    </main>
  )
}

export default App
