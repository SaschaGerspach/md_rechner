"""Static game data, loaded from the curated game_data.json.

Two kinds of static data (see notes/OVERVIEW.md principle 6): production per
building, and consumption per resident. Shape matches notes/ARCHITECTURE.md
(building -> levels -> level -> can_produce).

The data is a CURATED CORE SUBSET from MD Manager v1.3 (see game_data.json for
the source/attribution and the curation notes). Recipes, inputs and byproducts
come from that source; `output_per_day_at_100` is null until rates are measured
in-game; `max_workers` is only known for sewing_hut. Values are unverified
against the current game (`VERIFIED` is False). byproducts are stored but not yet
evaluated by calc/graph.
"""

import json
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent / "game_data.json"

with _DATA_PATH.open(encoding="utf-8") as _f:
    _raw = json.load(_f)


def _build_static(raw):
    buildings = {}
    for building_id, building in raw["buildings"].items():
        # JSON object keys are strings; levels are int-keyed everywhere else
        levels = {int(level): body for level, body in building["levels"].items()}
        buildings[building_id] = {"levels": levels}
    # keys starting with "_" are notes, not resources
    consumption = {
        res: qty
        for res, qty in raw["resident_consumption"].items()
        if not res.startswith("_")
    }
    return {"buildings": buildings, "resident_consumption": consumption}


STATIC = _build_static(_raw)
SOURCE = _raw.get("_source", "")
VERIFIED = bool(_raw.get("verified", False))
