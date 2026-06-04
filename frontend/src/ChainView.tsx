import { useEffect, useMemo, useState } from 'react'
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'
import { getChain } from './api'
import type { ChainResponse } from './types'

interface NodeDatum {
  name: string
}
type LinkDatum = object

const WIDTH = 680
const HEIGHT = 360

function ChainView() {
  const [data, setData] = useState<ChainResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getChain()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
  }, [])

  // structural Sankey: uniform link value (1). settlement-weighted flows are a
  // later refinement (see decisions log). sankey needs a DAG, so skip on cycles.
  const graph = useMemo(() => {
    if (!data || data.cycles.length > 0 || data.nodes.length === 0) return null
    const layout = sankey<NodeDatum, LinkDatum>()
      .nodeId((d) => d.name)
      .nodeWidth(14)
      .nodePadding(14)
      .extent([
        [1, 1],
        [WIDTH - 1, HEIGHT - 1],
      ])
    return layout({
      nodes: data.nodes.map((name) => ({ name })),
      links: data.edges.map((e) => ({ source: e.source, target: e.target, value: 1 })),
    })
  }, [data])

  if (error) return <p className="error">{error}</p>
  if (!data) return <p className="note">Loading chain…</p>
  if (data.cycles.length > 0)
    return (
      <p className="error">
        Chain has a cycle (bad data): {data.cycles.map((c) => c.join(' → ')).join('; ')}
      </p>
    )
  if (!graph) return <p className="note">No chain data.</p>

  const linkPath = sankeyLinkHorizontal<NodeDatum, LinkDatum>()

  return (
    <svg width={WIDTH} height={HEIGHT} className="sankey">
      <g>
        {graph.links.map((link, i) => (
          <path
            key={i}
            d={linkPath(link) ?? undefined}
            fill="none"
            stroke="#8899aa"
            strokeOpacity={0.4}
            strokeWidth={Math.max(1, link.width ?? 1)}
          />
        ))}
      </g>
      <g>
        {graph.nodes.map((node, i) => {
          const x0 = node.x0 ?? 0
          const x1 = node.x1 ?? 0
          const y0 = node.y0 ?? 0
          const y1 = node.y1 ?? 0
          const leftHalf = x0 < WIDTH / 2
          return (
            <g key={i}>
              <rect x={x0} y={y0} width={x1 - x0} height={Math.max(1, y1 - y0)} fill="#4a90d9" />
              <text
                x={leftHalf ? x1 + 6 : x0 - 6}
                y={(y0 + y1) / 2}
                dy="0.35em"
                textAnchor={leftHalf ? 'start' : 'end'}
                fontSize={12}
              >
                {node.name}
              </text>
            </g>
          )
        })}
      </g>
    </svg>
  )
}

export default ChainView
