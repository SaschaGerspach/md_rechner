"""Static game data, loaded from the curated game_data.json.

Two kinds of static data (see notes/OVERVIEW.md principle 6): production per
building, and consumption per resident. Shape matches notes/ARCHITECTURE.md
(building -> levels -> level -> can_produce).

The real data (game_data.json) is a CURATED CORE SUBSET from MD Manager v1.3 and
is kept local/gitignored. When it is absent (e.g. a fresh clone), we fall back to
the checked-in game_data.example.json, which has the same structure but invented
dummy buildings — enough to run, not the real catalog. Recipes, inputs and
byproducts come from the source; `output_per_day_at_100` is null until rates are
measured in-game; `max_workers` is only known for some buildings.
"""

import json
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_DATA_PATH = _DIR / "game_data.json"
_EXAMPLE_PATH = _DIR / "game_data.example.json"


def _read_raw(data_path=_DATA_PATH, example_path=_EXAMPLE_PATH):
    if data_path.exists():
        path = data_path
    else:
        path = example_path
        print(
            f"planner: using example data ({example_path.name}), real "
            f"{data_path.name} not found — catalog is dummy schema data only.",
            file=sys.stderr,
        )
    with path.open(encoding="utf-8") as f:
        return json.load(f)


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


_raw = _read_raw()
STATIC = _build_static(_raw)
SOURCE = _raw.get("_source", "")
VERIFIED = bool(_raw.get("verified", False))
