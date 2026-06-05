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

export interface MissingRate {
  building: string
  output: string
}

export interface BalanceResponse {
  errors: string[]
  production: Record<string, number>
  demand: Record<string, number>
  balance: Record<string, number>
  rates_missing: MissingRate[]
}

export interface Recipe {
  output: string
  // null until the rate is measured in-game (see backend game_data.json)
  output_per_day_at_100: number | null
  inputs: Record<string, number>
  byproducts?: Record<string, number>
}

export interface BuildingLevel {
  level: number
  // null where the worker cap is not yet known
  max_workers: number | null
  can_produce: Recipe[]
}

export interface CatalogBuilding {
  id: string
  levels: BuildingLevel[]
}

export interface BuildingsResponse {
  buildings: CatalogBuilding[]
  source: string
  verified: boolean
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
