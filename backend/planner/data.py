"""Static game data: PLACEHOLDER VALUES, not curated.

Two kinds of static data live here, both the same for every player (see
notes/OVERVIEW.md principle 6): production per building, and consumption per
resident. Shape matches notes/ARCHITECTURE.md (building -> levels -> level ->
can_produce).

The building set uses the real Medieval Dynasty production buildings (Kitchen,
Sewing Hut, Smithy, Tavern, Workshop) plus the Barn and the Well, taken from the
wiki's Buildings page. The recipes, inputs and rates below are still PLACEHOLDERS
chosen to exercise the model (multi-stage chains, multi-input recipes,
level-dependent recipe sets) — they are NOT the curated shipping data. Real rates
will be read off the in-game assignment screen at skill 3 when curation starts.

Raw materials with no producer here (flachs, getreide, eisenerz, holz) surface as
leaf deficits equal to what their chain consumes per day: V1 does not model
fields, which harvest in bulk seasonally rather than at a steady daily rate. A
well IS a steady daily producer (a worker draws water continuously), so unlike a
field it is modelled as a producer.
"""

_SEWING_RECIPES = [
    {"output": "leinengarn",           "rate_at_100": 20, "inputs": {"flachs": 5}},
    {"output": "leinengewebe",         "rate_at_100": 30, "inputs": {"leinengarn": 1}},
    {"output": "einfaches_leinenhemd", "rate_at_100": 5,  "inputs": {"leinengewebe": 1, "leinengarn": 2}},
]

_KITCHEN_RECIPES = [
    {"output": "essen", "rate_at_100": 10, "inputs": {"mehl": 1, "wasser": 1}},
]

_TAVERN_RECIPES = [
    {"output": "bier", "rate_at_100": 12, "inputs": {"getreide": 1, "wasser": 1}},
]

# workshop and smithy recipe sets grow with level.
_WORKSHOP_RECIPES_L1 = [
    {"output": "bretter", "rate_at_100": 20, "inputs": {"holz": 2}},
]
_WORKSHOP_RECIPES_L2 = [
    {"output": "bretter", "rate_at_100": 20, "inputs": {"holz": 2}},
    {"output": "griff",   "rate_at_100": 15, "inputs": {"holz": 1}},
]
_SMITHY_RECIPES_L1 = [
    {"output": "eisenbarren", "rate_at_100": 8, "inputs": {"eisenerz": 2}},
]
_SMITHY_RECIPES_L2 = [
    {"output": "eisenbarren", "rate_at_100": 8, "inputs": {"eisenerz": 2}},
    {"output": "werkzeug",    "rate_at_100": 5, "inputs": {"eisenbarren": 1, "griff": 1}},
]

STATIC = {
    "buildings": {
        "well": {
            "levels": {
                1: {"max_workers": 1, "can_produce": [
                    {"output": "wasser", "rate_at_100": 30, "inputs": {}},
                ]},
            },
        },
        "barn": {
            "levels": {
                1: {"max_workers": 1, "can_produce": [
                    {"output": "mehl", "rate_at_100": 18, "inputs": {"getreide": 2}},
                ]},
            },
        },
        "kitchen": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _KITCHEN_RECIPES},
                2: {"max_workers": 2, "can_produce": _KITCHEN_RECIPES},
            },
        },
        "tavern": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _TAVERN_RECIPES},
                2: {"max_workers": 2, "can_produce": _TAVERN_RECIPES},
            },
        },
        "sewing_hut": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _SEWING_RECIPES},
                2: {"max_workers": 1, "can_produce": _SEWING_RECIPES},
                3: {"max_workers": 2, "can_produce": _SEWING_RECIPES},
            },
        },
        "workshop": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _WORKSHOP_RECIPES_L1},
                2: {"max_workers": 2, "can_produce": _WORKSHOP_RECIPES_L2},
            },
        },
        "smithy": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _SMITHY_RECIPES_L1},
                2: {"max_workers": 2, "can_produce": _SMITHY_RECIPES_L2},
            },
        },
    },
    # Per-resident daily consumption. Residents draw from the same resource pool
    # as recipe inputs, with no priority, so the calc just adds these into the
    # same demand total (see ARCHITECTURE calc rules).
    "resident_consumption": {
        "essen": 1,
        "wasser": 1,
    },
}
