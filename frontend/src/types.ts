export interface BuildingInput {
  type: string
  level: number
  workers: number
  allocation: Record<string, number>
}

export interface Settlement {
  population: number
  buildings: BuildingInput[]
}

export interface BalanceResponse {
  errors: string[]
  production: Record<string, number>
  demand: Record<string, number>
  balance: Record<string, number>
}

export interface ChainEdge {
  source: string
  target: string
}

export interface ChainResponse {
  nodes: string[]
  edges: ChainEdge[]
  cycles: string[][]
  topo_order: string[]
}
