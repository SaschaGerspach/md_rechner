# Architecture

## Stack at a glance

| Layer | Choice | Notes |
|---|---|---|
| Frontend | React + TypeScript | Learning goal; HttpClient equivalent via fetch/axios |
| Backend | Django + Django REST Framework | API; required for save parsing |
| Database | SQLite (V1) → PostgreSQL (later) | Switch when accounts/saved plans arrive |
| Calculation | Plain Python + networkx | Core logic; networkx for chains |
| Save parsing | pygvas or uesave (Phase 2) | Server-side only |
| Visualization | D3 (Sankey) + light chart lib | Chains as Sankey, balance as bars |
| Hosting | all-inkl (frontend) + Hostinger VPS (backend) | Reuse existing infra |

## Backend (Django + DRF)

The calculation itself is a **pure function** over input plus the static game
data, so most of it is plain Python and needs no framework magic. DRF provides
the API surface: an endpoint that takes a settlement description and returns the
resource balance and the chain breakdown.

### networkx for production chains

A chain like `flax -> linen thread -> linen -> clothes` is a directed graph.
networkx gives us:
- **Topological sort** to process the chain in the right order.
- **Cycle detection** to catch bad data early (a recipe should never depend on
  itself).

This is the one place a library clearly earns its place over hand-rolled code.

### Save parsing (Phase 2 only)

The save is a standard Unreal Engine GVAS `.sav` file. The parsing layer is a
solved problem with existing libraries:
- **pygvas** (PyPI) — pure Python, deserializes UE4/5 GVAS into Python objects.
  Keeps everything in the Python stack.
- **uesave** (Rust) — robust CLI that converts saves to JSON; can be shelled out
  from Django if pure Python struggles with this specific game.

The library gives the raw JSON structure. The **real work** is mapping which JSON
keys mean population, buildings, workers — that part is Medieval Dynasty specific
and undocumented. Standard approach: parse a save, make a targeted in-game change,
save again, diff the two JSON outputs to find the field. Map it field by field.

Two risks to plan for:
- **Format fragility across game versions.** Medieval Dynasty still updates. If
  the devs change the save structure, the field mapping breaks. We need at least
  a version check that reports "this save version is not supported yet" instead
  of silently producing wrong numbers.
- **Performance.** Parsing per upload uses CPU/RAM. Fine at hobby scale, but keep
  the option to process asynchronously if traffic grows.

## Data model

Two strictly separated layers (see OVERVIEW principle 6). The shapes below are
the canonical structure; real numeric values are curated by hand from the source
in "Game data strategy" and are not invented here.

### Static game data (same for every player)

A building owns a list of **levels**. Everything that a level can change —
maximum worker count, production speed, and which recipes are available — lives
inside that level, because level can alter any of them independently. A level is
a full snapshot of what the building can do at that level; it does not inherit
from lower levels.

```json
{
  "id": "sewing_hut",
  "levels": [
    {
      "level": 1,
      "max_workers": 1,
      "can_produce": [
        { "output": "linen_thread", "output_per_day_at_100": null, "inputs": { "flax": null } }
      ]
    },
    {
      "level": 3,
      "max_workers": 3,
      "can_produce": [
        { "output": "linen_thread", "output_per_day_at_100": null, "inputs": { "flax": null } },
        { "output": "linen",        "output_per_day_at_100": null, "inputs": { "linen_thread": null } },
        { "output": "clothes",      "output_per_day_at_100": null, "inputs": { "linen": null } }
      ]
    }
  ]
}
```

- `output_per_day_at_100` is the output at 100% allocation to that one recipe.
  It is **per recipe**, because crafting duration differs between products — at
  the same percentage, faster products yield more units per day.
- `inputs` is a map, so a recipe can require **several** inputs (e.g. a soup
  needing a wooden plate, water, and a carrot). A single input is just the
  one-key case.
- `byproducts` (optional) is a ratio map of secondary outputs produced alongside
  the main `output` — e.g. threshing flax yields flachshalme as the main output
  plus `{ "stroh": N }` per main-output unit. Recipes without a secondary output
  simply omit the field, so single-output recipes are unaffected. The main output
  still carries the rate; byproducts scale off it.

### Personal state (this player's settlement)

```json
{
  "population": 12,
  "buildings": [
    {
      "type": "sewing_hut",
      "level": 2,
      "workers": 1,
      "allocation": { "linen_thread": 30, "linen": 40 }
    }
  ]
}
```

- `allocation` is a **percentage split** of the building's total work across the
  recipes it is set to produce. All workers in a building act as **one unit**
  sharing this single split (not one worker per recipe).
- The split may sum to **at most 100**, not exactly 100. 30 + 40 = 70 means the
  building idles 30% of the time. A recipe not listed is 0%.

### Calculation rules

**V1 (Planner) computes a demand balance — it does not ration or cap.** Every
building is assumed to produce at its set rate; the calc reports, per resource,
production minus the sum of all demands.

- **Per-recipe output:** `output_per_day_at_100 × (percent / 100) × workers`.
  Output scales **linearly** with worker count (two workers produce twice one).
  Input consumption scales the same way.
- **Per-resource balance:** for each resource, `sum(production) − sum(demand)`,
  where demand is resident consumption plus every recipe input that uses it. A
  negative result is a deficit and is flagged. Competing consumers (e.g. residents
  eating carrots and a kitchen using carrots for soup) draw from one shared pool
  with **no priority** — so demand is a flat sum, with no allocation logic needed.
- **Bottlenecks surface on their own.** Because each recipe's inputs are counted
  as demand, a missing chain stage shows up as its own deficit: set a sewing hut
  to 100% clothes with no flax, and `linen`, `linen_thread`, and `flax` each go
  negative. The calc does **not** silently cap clothes output to what flax allows;
  it shows the intended output alongside the deficits that block it. This is the
  more useful behaviour for a what-if sandbox — the gap is the actionable signal.
- The recipe inputs double as the **graph edges** for networkx (for the Sankey and
  for cycle detection on the data) and as the **quantity constraints** for the
  balance — one source, two uses, so balance and chain cannot drift apart. Because
  recipes can have multiple inputs, the "chain" is in general a directed acyclic
  **graph** (convergent edges), not a single strand; networkx handles this natively.

**Deferred to the Analyzer (Phase 2): min-over-inputs capping.** Computing the
*actual achievable* output — where the scarcest input sets the ceiling and the
surplus of the others is left unused, propagated stage by stage in topological
order — is what diagnoses a real settlement ("you actually produce 3 clothes/day").
This is the heavier flow-propagation use of networkx and belongs with the save
analyzer, not the V1 planner. The data model above is built so this is an
*extension* of the same graph, not a rebuild: the edges and quantity constraints
are already in place — and byproducts must then scale off the capped output, not
the nominal one (in V1, with no capping, the two coincide).

**Fields and raw materials in V1.** Fields are **not** modeled as producers. A
field harvests once per cycle (bulk, at season start) while the chain draws stored
material down daily, so a field has no honest daily rate. The processing chain
(barn, sewing hut, …) is genuinely day-steady and is modeled normally. In V1 a raw
harvested material (e.g. `flachs`) is therefore a **leaf with no producer**: its
balance is `0 − demand`, i.e. a deficit equal to what the chain consumes per day.
That deficit magnitude IS the "raw material needed per day" readout — no fictional
field rate is invented. Seasonality (bulk harvest, storage buffer, adjustable
season length) and the "how many fields?" convenience calc are deferred to Phase 3.

### Validation

- `workers ≤ max_workers` of the selected level.
- `sum(allocation) ≤ 100` per building.

## Frontend (React + TypeScript)

Two main views:
- **Balance view** — surplus/deficit per resource. Simple bar charts.
- **Chain view** — production chains as a Sankey diagram via D3.

State is local for V1 (no persistence). The calculation runs **server-side**
(Django + networkx), decided at the start of Phase 1 — see the decisions log in
OVERVIEW. The frontend sends the settlement description to the DRF API and renders
the returned balance and chain breakdown.

## Database

- **V1: SQLite.** The static game data is read-only reference data; there are no
  accounts and nothing user-specific to persist. SQLite is enough.
- **Later: PostgreSQL.** Introduce only when saved plans or accounts arrive
  (Phase 4). Do not provision Postgres-in-Docker by reflex the way join-v2 did —
  here it would be ballast until persistence exists.

## Game data strategy

Maintained **by hand** as a JSON file or Django fixture, not scraped. At base
value 3 the dataset stays finite: a few dozen buildings and resources. Note that
"finite" does not mean "one value per building" — a building can expose several
recipes and several levels (see Data model) — but the total remains small enough
to curate by hand. The effort is paid once, and a checked data file is far more
reliable than a scraper that breaks when the wiki HTML changes.

**Source, split by reliability (RESOLVED).** The graph (which input makes which
output), input quantities, byproducts, building assignment, tool-wear, item prices
and resident consumption values come from `notes/md_manager_extract.json` —
extracted from MD Manager v1.3 (Xarmo / r00t @ Toplitz Discord, Nexus mod 25;
license permits reuse **with credit** — keep attribution). The **production rates**
are NOT in that source (and the wiki's rates lag the game): the rate
(`output_per_day_at_100`) is measured on the **in-game assignment screen** — assign
a skill-3 worker, set one recipe to 100%, read the per-day output. Building
**levels / max_workers** are also not in the extract; curate them separately (e.g.
from the wiki). The extract is a *curation source*, not the shippable fixture: it
uses display names (map to snake_case IDs), targets MD Manager v1.3's game version
(verify against the current game before shipping), and field processes are excluded
in V1. (Datamining the encrypted `.pak` was investigated and rejected — see
`spike/datamine_spike.md`.)

## Hosting

Reuse the existing setup:
- **Frontend** static build on all-inkl.
- **Backend** on the Hostinger VPS with Nginx reverse proxy, Certbot SSL, UFW,
  Docker. The existing `setup_full.sh` deployment script applies directly.
