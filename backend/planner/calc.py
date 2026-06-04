"""V1 Planner calc: demand balance, no rationing.

Pure Python over a settlement description plus the static game data. No Django
dependency, so it stays unit-testable on its own. See notes/ARCHITECTURE.md for
the semantics; the seed for this module is spike/calc_dryrun.py.
"""


def validate(settlement, static):
    errors = []
    for b in settlement["buildings"]:
        level = static[b["type"]]["levels"][b["level"]]
        # a building cannot hold more workers than its level allows
        if b["workers"] > level["max_workers"]:
            errors.append(
                f"{b['type']} L{b['level']}: {b['workers']} workers > "
                f"max {level['max_workers']}"
            )
        # allocation is a share of one work-unit; >100% is impossible
        total = sum(b["allocation"].values())
        if total > 100:
            errors.append(f"{b['type']}: allocation sums to {total}% (> 100)")
    return errors


def compute_balance(settlement, static):
    production = {}  # resource -> units/day produced
    demand = {}      # resource -> units/day consumed (recipe inputs only here)

    for b in settlement["buildings"]:
        level = static[b["type"]]["levels"][b["level"]]
        recipes = {r["output"]: r for r in level["can_produce"]}
        for output, percent in b["allocation"].items():
            recipe = recipes[output]
            # per-recipe output scales linearly with worker count
            made = recipe["rate_at_100"] * (percent / 100) * b["workers"]
            production[output] = production.get(output, 0) + made
            for res, qty_per_unit in recipe["inputs"].items():
                demand[res] = demand.get(res, 0) + qty_per_unit * made

    resources = set(production) | set(demand)
    balance = {r: production.get(r, 0) - demand.get(r, 0) for r in resources}
    return production, demand, balance
