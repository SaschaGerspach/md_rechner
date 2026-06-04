"""Static game data: PLACEHOLDER VALUES, not curated.

One building only for the first slice. Shape matches notes/ARCHITECTURE.md
(building -> levels -> level -> can_produce). Real rates will be read off the
in-game assignment screen at skill 3 when curation starts; these numbers only
exercise the model. `flachs` has no producer here on purpose: V1 does not model
fields, so it surfaces as a leaf deficit equal to the chain's daily draw.
"""

_SEWING_RECIPES = [
    {"output": "leinengarn",           "rate_at_100": 20, "inputs": {"flachs": 5}},
    {"output": "leinengewebe",         "rate_at_100": 30, "inputs": {"leinengarn": 1}},
    {"output": "einfaches_leinenhemd", "rate_at_100": 5,  "inputs": {"leinengewebe": 1, "leinengarn": 2}},
]

STATIC = {
    "sewing_hut": {
        "levels": {
            1: {"max_workers": 1, "can_produce": _SEWING_RECIPES},
            2: {"max_workers": 1, "can_produce": _SEWING_RECIPES},
            3: {"max_workers": 2, "can_produce": _SEWING_RECIPES},
        },
    },
}
