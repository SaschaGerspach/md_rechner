"""
V1 Planner calc — dry run against a TEST fixture.

Purpose: verify the MODEL computes as documented (demand balance, no rationing),
not that the numbers match the real game. Every rate below is INVENTED test data,
chosen to trigger the tricky cases:
  - a resource with two competing consumers (leinengarn)
  - a bottleneck (flax source too small to feed the thread recipe)
  - a multi-input recipe (einfaches_leinenhemd)
  - an idle building (allocation sums to < 100)
  - validation (workers <= max_workers, allocation <= 100)
  - cycle detection on bad data (the wool chain from the wiki)

Real rates will later be read off the in-game assignment screen at skill 3.
"""

import networkx as nx


# ---------------------------------------------------------------------------
# STATIC GAME DATA  (TEST VALUES — not curated, not from the game)
# Shape matches ARCHITECTURE.md: building -> levels -> level -> can_produce.
# ---------------------------------------------------------------------------
STATIC = {
    "field_flax": {
        "levels": {
            1: {
                "max_workers": 1,
                # rate is per worker-day at 100% allocation to this recipe
                "can_produce": [
                    {"output": "flachs", "rate_at_100": 50, "inputs": {}},
                ],
            },
        },
    },
    "sewing_hut": {
        "levels": {
            1: {"max_workers": 1, "can_produce": None},   # filled below
            2: {"max_workers": 1, "can_produce": None},
            3: {"max_workers": 2, "can_produce": None},
        },
    },
}

# Recipes are identical across sewing-hut levels (verified: levels change only
# worker slots + storage, not the recipe list). Defined once, shared.
_SEWING_RECIPES = [
    {"output": "leinengarn",          "rate_at_100": 20, "inputs": {"flachs": 5}},
    {"output": "leinengewebe",        "rate_at_100": 30, "inputs": {"leinengarn": 1}},
    {"output": "einfaches_leinenhemd","rate_at_100": 5,  "inputs": {"leinengewebe": 1, "leinengarn": 2}},
]
for lvl in STATIC["sewing_hut"]["levels"].values():
    lvl["can_produce"] = _SEWING_RECIPES


# ---------------------------------------------------------------------------
# PERSONAL STATE  (this player's hypothetical settlement)
# ---------------------------------------------------------------------------
SETTLEMENT = {
    "population": 10,
    "buildings": [
        {"type": "field_flax", "level": 1, "workers": 1,
         "allocation": {"flachs": 100}},
        # 2 workers (level 3), split across three recipes, sums to exactly 100
        {"type": "sewing_hut", "level": 3, "workers": 2,
         "allocation": {"leinengarn": 50, "leinengewebe": 30, "einfaches_leinenhemd": 20}},
    ],
}


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------
def validate(settlement, static):
    errors = []
    for b in settlement["buildings"]:
        level = static[b["type"]]["levels"][b["level"]]
        # why: a building cannot hold more workers than its level allows
        if b["workers"] > level["max_workers"]:
            errors.append(
                f"{b['type']} L{b['level']}: {b['workers']} workers > "
                f"max {level['max_workers']}")
        # why: allocation is a share of one work-unit; >100% is impossible
        total = sum(b["allocation"].values())
        if total > 100:
            errors.append(f"{b['type']}: allocation sums to {total}% (> 100)")
    return errors


# ---------------------------------------------------------------------------
# CALC — demand balance, no rationing (V1 semantics)
# ---------------------------------------------------------------------------
def compute_balance(settlement, static):
    production = {}   # resource -> units/day produced
    demand = {}       # resource -> units/day consumed (recipe inputs only here)

    for b in settlement["buildings"]:
        level = static[b["type"]]["levels"][b["level"]]
        recipes = {r["output"]: r for r in level["can_produce"]}
        for output, percent in b["allocation"].items():
            recipe = recipes[output]
            # per-recipe output: rate * (percent/100) * workers  (linear)
            made = recipe["rate_at_100"] * (percent / 100) * b["workers"]
            production[output] = production.get(output, 0) + made
            # input consumption scales the same way, per output unit
            for res, qty_per_unit in recipe["inputs"].items():
                demand[res] = demand.get(res, 0) + qty_per_unit * made

    # (resident consumption would be added into `demand` here in the real calc;
    #  no resident-consumed resource exists in this test fixture)

    resources = set(production) | set(demand)
    balance = {r: production.get(r, 0) - demand.get(r, 0) for r in resources}
    return production, demand, balance


# ---------------------------------------------------------------------------
# CYCLE DETECTION on the static data graph (catches bad curation early)
# ---------------------------------------------------------------------------
def build_graph(recipes):
    g = nx.DiGraph()
    for r in recipes:
        for inp in r["inputs"]:
            g.add_edge(inp, r["output"])   # edge: input -> output
    return g


def check_cycles(recipes, label):
    g = build_graph(recipes)
    cycles = list(nx.simple_cycles(g))
    if cycles:
        print(f"  [{label}] CYCLE DETECTED (bad data): {cycles}")
    else:
        order = list(nx.topological_sort(g))
        print(f"  [{label}] acyclic. topo order: {' -> '.join(order)}")


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== VALIDATION ===")
    errs = validate(SETTLEMENT, STATIC)
    print("  OK, no validation errors" if not errs else "\n".join("  " + e for e in errs))

    print("\n=== BALANCE (demand balance, no capping) ===")
    prod, dem, bal = compute_balance(SETTLEMENT, STATIC)
    for r in sorted(bal):
        flag = "  <-- DEFICIT" if bal[r] < 0 else ""
        print(f"  {r:24} produced {prod.get(r,0):6.1f}  demand {dem.get(r,0):6.1f}  "
              f"balance {bal[r]:+6.1f}{flag}")

    print("\n=== CYCLE CHECK: leinen chain (should be clean) ===")
    check_cycles(_SEWING_RECIPES, "leinen")

    print("\n=== CYCLE CHECK: wool chain from wiki (the suspected bad data) ===")
    # The wiki says: wollgarn <- wollstoff, wollgewebe <- wollgarn,
    # and wollstoff is also used to make wollgarn -> circular.
    bad_wool = [
        {"output": "wollgarn",   "rate_at_100": 20, "inputs": {"wollstoff": 6}},
        {"output": "wollgewebe", "rate_at_100": 30, "inputs": {"wollgarn": 1}},
        {"output": "wollstoff",  "rate_at_100": 10, "inputs": {"wollgewebe": 1}},
    ]
    check_cycles(bad_wool, "wool")
