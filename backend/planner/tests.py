from pathlib import Path

from django.urls import reverse
from rest_framework.test import APITestCase

from . import calc, graph
from .data import _EXAMPLE_PATH, _build_static, _read_raw, STATIC

# Inline fixture with numeric rates: the math tests must not depend on the
# shipped data, whose rates are intentionally null until measured in-game.
SYNTH = {
    "buildings": {
        "synth_hut": {
            "levels": {
                3: {"max_workers": 2, "can_produce": [
                    {"output": "thread", "output_per_day_at_100": 20, "inputs": {"flax": 5}},
                    {"output": "fabric", "output_per_day_at_100": 30, "inputs": {"thread": 1}},
                    {"output": "shirt",  "output_per_day_at_100": 5,  "inputs": {"fabric": 1, "thread": 2}},
                    {"output": "norate", "output_per_day_at_100": None, "inputs": {"flax": 9}},
                ]},
                1: {"max_workers": None, "can_produce": [
                    {"output": "thread", "output_per_day_at_100": 20, "inputs": {"flax": 5}},
                ]},
            },
        },
    },
    "resident_consumption": {"food": 1, "water": 1},
}

SYNTH_SETTLEMENT = {
    "population": 10,
    "buildings": [
        {"type": "synth_hut", "level": 3, "workers": 2,
         "allocation": {"thread": 50, "fabric": 30, "shirt": 20}},
    ],
}


class ComputeBalanceTests(APITestCase):
    def test_balance_matches_hand_computed(self):
        _, _, bal = calc.compute_balance(SYNTH_SETTLEMENT, SYNTH)
        # thread: produced 20, consumed 18 (fabric) + 4 (shirt) -> -2
        self.assertAlmostEqual(bal["thread"], -2)
        self.assertAlmostEqual(bal["fabric"], 16)
        self.assertAlmostEqual(bal["shirt"], 2)
        # flax has no producer here: leaf deficit equal to the chain's draw
        self.assertAlmostEqual(bal["flax"], -100)
        # 10 residents, 1/day each, nothing produces these -> -10
        self.assertAlmostEqual(bal["food"], -10)
        self.assertAlmostEqual(bal["water"], -10)

    def test_resident_demand_scales_with_population(self):
        small = {**SYNTH_SETTLEMENT, "population": 3}
        _, dem, _ = calc.compute_balance(small, SYNTH)
        self.assertAlmostEqual(dem["food"], 3)
        self.assertAlmostEqual(dem["water"], 3)

    def test_null_rate_recipe_contributes_nothing(self):
        s = {"population": 0, "buildings": [
            {"type": "synth_hut", "level": 3, "workers": 1, "allocation": {"norate": 100}}
        ]}
        prod, dem, _ = calc.compute_balance(s, SYNTH)
        self.assertEqual(prod, {})
        # only the (zero) resident demand remains; the null-rate recipe adds nothing
        self.assertEqual(dem, {"food": 0, "water": 0})
        self.assertEqual(calc.missing_rates(s, SYNTH), [{"building": "synth_hut", "output": "norate"}])

    def test_validate_flags_too_many_workers(self):
        bad = {"population": 0, "buildings": [
            {"type": "synth_hut", "level": 3, "workers": 3, "allocation": {"thread": 100}}
        ]}
        errors = calc.validate(bad, SYNTH)
        self.assertEqual(len(errors), 1)
        self.assertIn("workers", errors[0])

    def test_null_max_workers_skips_cap(self):
        # level 1 has unknown (null) max_workers -> no cap enforced
        s = {"population": 0, "buildings": [
            {"type": "synth_hut", "level": 1, "workers": 9, "allocation": {"thread": 100}}
        ]}
        self.assertEqual(calc.validate(s, SYNTH), [])


class ExampleFallbackTests(APITestCase):
    def test_falls_back_to_example_when_game_data_missing(self):
        raw = _read_raw(Path("/no/such/game_data.json"), _EXAMPLE_PATH)
        static = _build_static(raw)
        # dummy schema data from the example file, not the real catalog
        self.assertIn("example_workshop", static["buildings"])
        self.assertNotIn("sewing_hut", static["buildings"])

    def test_uses_real_data_when_present(self):
        # with the real file present, _read_raw must not use the example
        raw = _read_raw()
        static = _build_static(raw)
        self.assertIn("sewing_hut", static["buildings"])


# Numeric fixture for the byproduct effect (the shipped data has null rates).
BYPRODUCT_STATIC = {
    "buildings": {
        "thresher": {
            "levels": {
                1: {"max_workers": 1, "can_produce": [
                    {"output": "grain", "output_per_day_at_100": 10,
                     "inputs": {"crop": 2}, "byproducts": {"straw": 3}},
                ]},
            },
        },
    },
    "resident_consumption": {},
}


class ByproductTests(APITestCase):
    def test_byproduct_adds_to_production_in_balance(self):
        s = {"population": 0, "buildings": [
            {"type": "thresher", "level": 1, "workers": 1, "allocation": {"grain": 100}}
        ]}
        prod, dem, bal = calc.compute_balance(s, BYPRODUCT_STATIC)
        # 10 grain/day made -> straw = ratio 3 * 10 = 30 on the production side
        self.assertAlmostEqual(prod["grain"], 10)
        self.assertAlmostEqual(prod["straw"], 30)
        self.assertAlmostEqual(dem["crop"], 20)
        self.assertAlmostEqual(bal["straw"], 30)

    def test_byproduct_is_a_graph_node_and_edge(self):
        g = graph.build_recipe_graph(BYPRODUCT_STATIC)
        self.assertIn("straw", g.nodes)
        self.assertIn(("crop", "straw"), g.edges)
        self.assertEqual(graph.find_cycles(g), [])


class RecipeGraphTests(APITestCase):
    def test_shipped_static_data_is_acyclic(self):
        # curation guard: a recipe must never depend on itself
        g = graph.build_recipe_graph(STATIC)
        self.assertEqual(graph.find_cycles(g), [])

    def test_topo_order_respects_chain(self):
        g = graph.build_recipe_graph(STATIC)
        order = graph.topo_order(g)
        self.assertLess(order.index("flax_stalk"), order.index("linen_thread"))
        self.assertLess(order.index("linen_thread"), order.index("linen_fabric"))
        self.assertLess(order.index("linen_fabric"), order.index("basic_shirt"))

    def test_cycle_detection_flags_bad_data(self):
        bad = {"buildings": {"x": {"levels": {1: {"max_workers": 1, "can_produce": [
            {"output": "a", "output_per_day_at_100": 1, "inputs": {"b": 1}},
            {"output": "b", "output_per_day_at_100": 1, "inputs": {"a": 1}},
        ]}}}}}
        g = graph.build_recipe_graph(bad)
        self.assertTrue(graph.find_cycles(g))


class ChainEndpointTests(APITestCase):
    def test_get_returns_acyclic_chain(self):
        response = self.client.get(reverse("chain"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["cycles"], [])
        self.assertIn({"source": "flax_stalk", "target": "linen_thread"}, body["edges"])
        order = body["topo_order"]
        self.assertLess(order.index("flax_stalk"), order.index("linen_thread"))


class BuildingsEndpointTests(APITestCase):
    def test_get_returns_catalog(self):
        response = self.client.get(reverse("buildings"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["verified"])
        self.assertTrue(body["source"])
        catalog = {b["id"]: b for b in body["buildings"]}
        self.assertIn("sewing_hut", catalog)
        levels = {lvl["level"]: lvl for lvl in catalog["sewing_hut"]["levels"]}
        self.assertEqual(levels[3]["max_workers"], 2)
        outputs = {r["output"] for r in levels[3]["can_produce"]}
        self.assertEqual(
            outputs, {"linen_thread", "linen_fabric", "basic_shirt", "basic_trousers"}
        )
        # rates are not yet measured
        self.assertIsNone(levels[3]["can_produce"][0]["output_per_day_at_100"])
        # max_workers unknown for buildings other than the sewing hut
        self.assertIsNone(catalog["well"]["levels"][0]["max_workers"])


class BalanceEndpointTests(APITestCase):
    def test_post_flags_missing_rates(self):
        settlement = {"population": 10, "buildings": [
            {"type": "sewing_hut", "level": 3, "workers": 2, "allocation": {"linen_thread": 100}}
        ]}
        response = self.client.post(reverse("balance"), settlement, format="json")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["errors"], [])
        self.assertIn({"building": "sewing_hut", "output": "linen_thread"}, body["rates_missing"])

    def test_unknown_building_is_rejected(self):
        bad = {"population": 0, "buildings": [
            {"type": "no_such_hut", "level": 1, "workers": 1, "allocation": {}}
        ]}
        response = self.client.post(reverse("balance"), bad, format="json")
        self.assertEqual(response.status_code, 400)
