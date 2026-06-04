# Roadmap

Phases are ordered by dependency first, motivation second. **Phase 1 must come
first** because every later phase fills into or extends the planner core. After
Phase 1, the order is flexible.

---

## Phase 1 — MVP Planner

The deterministic calculator core. Manual input, anonymous, base values only.

**In scope:**
- Manual input: buildings, workers, population.
- Production vs consumption balance per resource (food, water, firewood, etc.):
  show surplus or deficit.
- Production chains: raw -> intermediate -> final (e.g. flax -> linen thread ->
  linen -> clothes), modeled with networkx and shown as a Sankey diagram.
- Static game data as a curated JSON file / Django fixture (base value 3).
- SQLite, no accounts.

**Definition of done:** You can model a settlement by hand and immediately see,
per resource, whether you have a surplus or a shortfall, and see the production
chain laid out.

**Status (core done):** Backend (Django/DRF) serves `POST /api/balance/`,
`GET /api/buildings/` and `GET /api/chain/`; calc and networkx chain graph live in
`planner/`, with tests. Frontend (React/Vite) renders the planner form (dynamic
building list from the catalog), the balance table, and the chain as a D3 Sankey.
Backend is containerized (gunicorn prod / runserver dev), SQLite on a named volume.
Open: game data is still placeholder recipes on the real building set (real recipe
curation pending), styling pass, and settlement-weighted Sankey edges.

---

## Phase 2 — Save Upload (Analyzer)

The headline feature. Builds directly on the Phase 1 planner by auto-filling it
from a real save.

**In scope:**
- Server-side GVAS parsing (pygvas, or shell out to uesave).
- Reverse-engineer the field mapping for population, buildings, workers via
  save-diffing.
- Upload flow with instructions on where to find the `.sav` file.
- Auto-fill the planner from the parsed save.
- Read-only, parse-and-discard, no storage of uploaded files.
- Save-version detection that fails gracefully on unsupported versions.

**Definition of done:** A player uploads their `.sav` and sees their actual
settlement diagnosed in the planner, without typing anything in.

**Before building anything here:** run a spike. Take one of your own saves, run
it through uesave or pygvas to JSON, and just look at how readable and structured
it is. That answers in half an hour the one question the whole feature hangs on —
how deep and how ugly the reverse engineering will be.

---

## Phase 3 — Planning Depth

Deepen the planner with the "strong but not essential" features and the skill
layer.

**In scope:**
- "What do I need to support N residents?" — reverse calculation.
- Worker allocation: given X workers and a goal, suggest a distribution.
- Season effects, if production or consumption varies by season.
- Skill / perk modifier layer on top of base values (optional toggle, clearly
  separated from the base calculation).

**Definition of done:** The planner answers goal-driven questions, not just
"does this balance," and can optionally factor in skills/perks.

---

## Phase 4 — Persistence, Sharing, Reach

Everything that introduces accounts and outward reach.

**In scope:**
- Save / share plans (introduces accounts -> migrate to PostgreSQL).
- Tax and income projection (deferred from the start because it depends on
  diplomacy skill, perks, the market building, and the market worker's skill).
- Internationalization (the Medieval Dynasty community is international; German
  and English at minimum).

**Definition of done:** A plan can be saved and shared by link, and the tool is
usable in more than one language.

---

## Deferred / parked ideas

- The original Mac/Android shopping-list price-comparison app. Separate idea,
  not part of this project.
- Mobile app that reads the save directly off the gaming PC (would need the save
  synced to the NAS first). The web upload approach replaces this need.
