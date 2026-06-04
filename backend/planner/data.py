"""Static game data: PLACEHOLDER RECIPES on a real building set.

Two kinds of static data live here, both the same for every player (see
notes/OVERVIEW.md principle 6): production per building, and consumption per
resident. Shape matches notes/ARCHITECTURE.md (building -> levels -> level ->
can_produce).

The building names and their level counts come from the wiki's Buildings page
(Workshop I-III, Smithy I-III, Sewing I-III, Kitchen I-II, Tavern, Barn I-III,
Woodshed I-II, Well). NOTE: the wiki's "Materials" column is the building's
CONSTRUCTION cost, not its production recipe, so the recipes, inputs, rates and
max_workers below are still PLACEHOLDERS chosen to exercise the model
(multi-stage chains, multi-input recipes, level-dependent recipe sets, a
cross-building dependency workshop->smithy). They are NOT the curated shipping
data; real recipe rates will be read off the in-game assignment screen at skill 3.

Only day-steady producers are modelled. Fields and orchards (seasonal bulk
harvest) are excluded per the decisions log; hunting/animal-husbandry/extraction
are a possible later category. Raw materials with no producer here (baumstamm,
eisenerz, getreide, flachs) surface as leaf deficits equal to their chain's daily
draw. A well IS a steady daily producer (a worker draws water continuously), so
unlike a field it is modelled as a producer.
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

_BARN_RECIPES = [
    {"output": "mehl", "rate_at_100": 18, "inputs": {"getreide": 2}},
]

# extraction/production recipe sets that grow with building level.
_WOODSHED_RECIPES_L1 = [
    {"output": "brennholz", "rate_at_100": 25, "inputs": {"baumstamm": 1}},
]
_WOODSHED_RECIPES_L2 = [
    {"output": "brennholz", "rate_at_100": 25, "inputs": {"baumstamm": 1}},
    {"output": "bretter",   "rate_at_100": 16, "inputs": {"baumstamm": 1}},
]
_WORKSHOP_RECIPES_L1 = [
    {"output": "griff", "rate_at_100": 15, "inputs": {"bretter": 1}},
]
_WORKSHOP_RECIPES_L2 = [
    {"output": "griff", "rate_at_100": 15, "inputs": {"bretter": 1}},
    {"output": "stiel", "rate_at_100": 18, "inputs": {"baumstamm": 1}},
]
_WORKSHOP_RECIPES_L3 = [
    {"output": "griff",  "rate_at_100": 15, "inputs": {"bretter": 1}},
    {"output": "stiel",  "rate_at_100": 18, "inputs": {"baumstamm": 1}},
    {"output": "moebel", "rate_at_100": 4,  "inputs": {"bretter": 2}},
]
_SMITHY_RECIPES_L1 = [
    {"output": "eisenbarren", "rate_at_100": 8, "inputs": {"eisenerz": 2}},
]
_SMITHY_RECIPES_L2 = [
    {"output": "eisenbarren", "rate_at_100": 8, "inputs": {"eisenerz": 2}},
    {"output": "werkzeug",    "rate_at_100": 5, "inputs": {"eisenbarren": 1, "griff": 1}},
]
_SMITHY_RECIPES_L3 = [
    {"output": "eisenbarren", "rate_at_100": 8, "inputs": {"eisenerz": 2}},
    {"output": "werkzeug",    "rate_at_100": 5, "inputs": {"eisenbarren": 1, "griff": 1}},
    {"output": "nagel",       "rate_at_100": 30, "inputs": {"eisenbarren": 1}},
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
        "woodshed": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _WOODSHED_RECIPES_L1},
                2: {"max_workers": 2, "can_produce": _WOODSHED_RECIPES_L2},
            },
        },
        "barn": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _BARN_RECIPES},
                2: {"max_workers": 2, "can_produce": _BARN_RECIPES},
                3: {"max_workers": 3, "can_produce": _BARN_RECIPES},
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
                1: {"max_workers": 2, "can_produce": _TAVERN_RECIPES},
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
                3: {"max_workers": 3, "can_produce": _WORKSHOP_RECIPES_L3},
            },
        },
        "smithy": {
            "levels": {
                1: {"max_workers": 1, "can_produce": _SMITHY_RECIPES_L1},
                2: {"max_workers": 2, "can_produce": _SMITHY_RECIPES_L2},
                3: {"max_workers": 3, "can_produce": _SMITHY_RECIPES_L3},
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
