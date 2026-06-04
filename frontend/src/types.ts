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

export interface Recipe {
  output: string
  rate_at_100: number
  inputs: Record<string, number>
}

export interface BuildingLevel {
  level: number
  max_workers: number
  can_produce: Recipe[]
}

export interface CatalogBuilding {
  id: string
  levels: BuildingLevel[]
}

export interface BuildingsResponse {
  buildings: CatalogBuilding[]
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
