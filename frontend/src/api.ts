import type { BalanceResponse, Settlement } from './types'

const API_BASE = 'http://localhost:8000/api'

export async function postBalance(settlement: Settlement): Promise<BalanceResponse> {
  const res = await fetch(`${API_BASE}/balance/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settlement),
  })
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`)
  }
  return res.json()
}
