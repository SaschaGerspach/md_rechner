"""V1 Planner calc: demand balance, no rationing.

Pure Python over a settlement description plus the static game data. No Django
dependency, so it stays unit-testable on its own. See notes/ARCHITECTURE.md for
the semantics; the seed for this module is spike/calc_dryrun.py.

Rates (`output_per_day_at_100`) may be null where not yet measured in-game; such
recipes contribute nothing and are reported separately via missing_rates().
max_workers may be null where unknown; the worker cap is then not enforced.
"""


def validate(settlement, static):
    errors = []
    for b in settlement["buildings"]:
        level = static["buildings"][b["type"]]["levels"][b["level"]]
        # a building cannot hold more workers than its level allows; skip when
        # the cap is unknown (null)
        max_workers = level["max_workers"]
        if max_workers is not None and b["workers"] > max_workers:
            errors.append(
                f"{b['type']} L{b['level']}: {b['workers']} workers > "
                f"max {max_workers}"
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
        level = static["buildings"][b["type"]]["levels"][b["level"]]
        recipes = {r["output"]: r for r in level["can_produce"]}
        for output, percent in b["allocation"].items():
            recipe = recipes[output]
            rate = recipe["output_per_day_at_100"]
            # rate unknown -> this recipe cannot contribute; surfaced by
            # missing_rates() so the gap is visible rather than silently zero
            if rate is None:
                continue
            # per-recipe output scales linearly with worker count
            made = rate * (percent / 100) * b["workers"]
            production[output] = production.get(output, 0) + made
            for res, qty_per_unit in recipe["inputs"].items():
                demand[res] = demand.get(res, 0) + qty_per_unit * made
            # byproducts are extra production, scaled per main-output unit made.
            # NOTE: when Phase 2 adds min-over-inputs capping, byproducts must
            # scale off the *capped* output, not the nominal `made` used here.
            for res, ratio in recipe.get("byproducts", {}).items():
                production[res] = production.get(res, 0) + ratio * made

    # resident consumption folds into the same demand pool, no priority
    for res, per_capita in static["resident_consumption"].items():
        demand[res] = demand.get(res, 0) + per_capita * settlement["population"]

    resources = set(production) | set(demand)
    balance = {r: production.get(r, 0) - demand.get(r, 0) for r in resources}
    return production, demand, balance


def missing_rates(settlement, static):
    """Recipes used in the settlement whose rate has not been measured yet."""
    missing = []
    for b in settlement["buildings"]:
        level = static["buildings"][b["type"]]["levels"][b["level"]]
        recipes = {r["output"]: r for r in level["can_produce"]}
        for output in b["allocation"]:
            if recipes[output]["output_per_day_at_100"] is None:
                missing.append({"building": b["type"], "output": output})
    return missing
