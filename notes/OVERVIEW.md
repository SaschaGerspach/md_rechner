# Medieval Dynasty Production Planner — Overview

> Working title. A public web tool that helps Medieval Dynasty players plan and
> balance the production economy of their settlement.

## What this is

The core of the tool is a **calculator**: you describe a settlement (which
buildings, how many workers, how many residents) and the tool tells you whether
your production covers your consumption, resource by resource. On top of that it
visualizes **production chains** (raw material to intermediate to final product).

Two possible "hearts" were discussed. We settled the relationship between them:

- **Planner (what-if sandbox)** — you type a hypothetical settlement, the tool
  computes the balance. This is the foundation and works with zero save parsing.
- **Analyzer (diagnose real state)** — you upload your actual save file, the tool
  fills the planner automatically and diagnoses your current settlement.

The Analyzer is the Planner plus an auto-fill layer. So the **Planner is built
first**, and save parsing is a comfort layer added on top later.

## Where we are heading (vision)

A player who is unsure whether their village can feed 30 residents, or who wants
to know how many flax fields they need to keep a tailor running, opens the tool,
models it in a minute, and sees the answer. No spreadsheet, no guessing. Later,
they can skip the manual entry entirely by uploading their save.

## Core principles (locked in)

1. **Base values only in V1.** Worker skill and perks change how much a building
   actually produces, not just income. Modeling all of that would force a huge
   input form and rely on poorly documented multipliers. So V1 computes with
   standard base output, clearly labeled as "base values." Skill/perk modifiers
   are a deliberate later layer.
2. **Base value = 3.** A resident pulled into the settlement has a base skill of
   1 to 3. In practice you always aim for a 3 in what you need, so the dataset is
   built around the level-3 output. This also keeps the data set **finite and
   small** (one output value per building, no skill-tier matrix).
3. **Read-only save handling.** When save upload arrives, the tool only reads the
   file. It never writes a save back. This avoids the riskiest part entirely.
4. **Parse and discard.** Uploaded saves are parsed and thrown away, not stored.
   This is stated transparently in the tool.
5. **Hand-curated game data, not scraping.** Because the dataset is finite at base
   value 3, the production and consumption data is maintained by hand in a checked
   data file, not pulled from a fragile wiki scraper.
6. **Two separate data layers.** Never mix them:
   - *Static game data* — production rate per building, consumption per resident.
     Same for everyone, comes from the curated data file.
   - *Personal state* — which buildings, how many workers, population. Manual in
     V1, from the save in Phase 2.

## Decisions log

| Decision | Choice | Reason |
|---|---|---|
| Heart of the tool | Planner first, Analyzer on top | Analyzer = Planner + auto-fill |
| Values in V1 | Base values only, level 3 | Deterministic, finite dataset, manageable input |
| Tax / income | Deferred | Depends on diplomacy skill, perks, market building, market worker skill — too variable |
| Game data source | Hand-curated JSON / fixtures | Finite at base value 3, more reliable than scraping |
| Frontend | React + TypeScript | Chosen as a learning opportunity (less familiar than Angular) |
| Backend | Django + DRF | Needed for save parsing (Phase 2); fits backend-depth career goal |
| Database | SQLite for V1, Postgres later | No accounts/persistence in V1, so Postgres would be ballast for now |
| Accounts in V1 | No, anonymous | No real user data to store yet |
| Calc location (V1) | Server-side (Django + networkx) | The core reason is Phase 2: the save parser is Python and feeds the same calc, so building the chain logic (topo-sort, cycle detection, flow propagation) in TS for V1 and again in Python later would be double work. Server-side builds it once. Note this is forward-looking, not a V1 need — the V1 calc (demand balance) is light enough to run in the browser; the heavier flow propagation that would truly exercise networkx is itself a Phase 2 concern (see Calc semantics). |
| Calc semantics (V1) | Demand balance, no rationing | Each building produces at its set rate; per resource, production minus the sum of all demands (residents + every recipe input). Deficits are flagged. Every missing chain stage surfaces as its own deficit, so the bottleneck is visible without propagation. No silent capping, no allocation between competing consumers (none needed — competing consumers draw from a shared pool with no priority). The "actual achievable output" capping (min over inputs) is the Analyzer's job, deferred to Phase 2. |
| Fields in V1 | Not modeled as producers | A field harvests once per cycle (bulk, at season start) and stored material is drawn down daily — so a field has no honest daily rate. The processing chain (barn, sewing hut, …) IS genuinely day-steady and is modeled normally. V1 simply does not add field buildings; the raw harvested material (e.g. flax) appears as an unmet demand on its resource, and that deficit magnitude IS the "raw material needed per day" readout. No fiction, single day-steady model. |
| Seasonality | Deferred to Phase 3 | Bulk harvest + storage buffer + adjustable season length is what makes "do I run out in winter?" hard. V1's day-steady demand model deliberately does not answer within-year timing. Already a Phase 3 roadmap item. |
| Field-count feature ("how many fields?") | Deferred to Phase 3 | = chain demand per cycle ÷ yield per harvest. The yield is a static value, but "per cycle" needs season length (adjustable in-game) as input — which pulls a strand of Phase 3 complexity into V1. V1 shows raw-material demand only; the player divides by yield themselves. The convenience version waits for Phase 3. |
| Multi-output recipes | Byproduct variant | A recipe keeps one main `output` with its measured rate, plus an optional `byproducts` ratio map (e.g. threshing flax → flachshalme + `{stroh: N}`). Minimal change: existing single-output recipes are untouched (no `byproducts` field). Switch to a symmetric `outputs` map only if a building ever lets the player choose between two equal outputs (not main + leftover) — not on spec. |
| Data source (test vs. shipping) | Test = placeholder; shipping deferred | The dry-run uses placeholder values (invented or wiki, irrelevant) purely to verify the model computes. The shipping-dataset source is a separate, still-open decision: inputs/graph are reliable from the wiki, but players report wiki *production rates* are outdated. Leaning toward inputs-from-wiki + rates-read-off-the-in-game-assignment-screen at skill 3. Decide when real curation actually starts. |

## Honest note on scope

For the pure V1 Planner (manual input, anonymous, no persistence) a backend is
technically **over-dimensioned** — it could run entirely in the browser. This is
true of the calculation too: the V1 demand balance is a flat per-resource sum and
needs neither topological sort nor flow propagation, so the part of the stack that
would genuinely justify networkx (the min-over-inputs flow propagation) only
arrives with the Analyzer in Phase 2. The backend is added on purpose for two
reasons: save parsing must run server-side (pygvas is Python, uesave is Rust,
neither runs in the browser), and a clean DRF backend serves the goal of building
backend depth. This is a conscious, forward-looking choice, not a default — and
not something V1 alone requires.
