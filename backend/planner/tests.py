from django.urls import reverse
from rest_framework.test import APITestCase

from . import calc, graph
from .data import STATIC

# sewing_hut L3 (2 workers), split 50/30/20 across the linen chain.
# Hand-computed expected balance, matching the spike's documented case.
SETTLEMENT = {
    "population": 10,
    "buildings": [
        {
            "type": "sewing_hut",
            "level": 3,
            "workers": 2,
            "allocation": {"leinengarn": 50, "leinengewebe": 30, "einfaches_leinenhemd": 20},
        }
    ],
}


class ComputeBalanceTests(APITestCase):
    def test_balance_matches_hand_computed(self):
        _, _, bal = calc.compute_balance(SETTLEMENT, STATIC)
        # leinengarn: produced 20, consumed 18 (gewebe) + 4 (hemd) -> -2
        self.assertAlmostEqual(bal["leinengarn"], -2)
        self.assertAlmostEqual(bal["leinengewebe"], 16)
        self.assertAlmostEqual(bal["einfaches_leinenhemd"], 2)
        # flachs has no producer in V1: leaf deficit equal to the chain's draw
        self.assertAlmostEqual(bal["flachs"], -100)
        # 10 residents, 1/day each, nothing produces these -> -10
        self.assertAlmostEqual(bal["essen"], -10)
        self.assertAlmostEqual(bal["wasser"], -10)

    def test_resident_demand_scales_with_population(self):
        small = {**SETTLEMENT, "population": 3}
        _, dem, _ = calc.compute_balance(small, STATIC)
        self.assertAlmostEqual(dem["essen"], 3)
        self.assertAlmostEqual(dem["wasser"], 3)

    def test_validate_flags_too_many_workers(self):
        bad = {"population": 0, "buildings": [
            {"type": "sewing_hut", "level": 3, "workers": 3, "allocation": {"leinengarn": 100}}
        ]}
        errors = calc.validate(bad, STATIC)
        self.assertEqual(len(errors), 1)
        self.assertIn("workers", errors[0])


class RecipeGraphTests(APITestCase):
    def test_shipped_static_data_is_acyclic(self):
        # curation guard: a recipe must never depend on itself
        g = graph.build_recipe_graph(STATIC)
        self.assertEqual(graph.find_cycles(g), [])

    def test_topo_order_respects_chain(self):
        g = graph.build_recipe_graph(STATIC)
        order = graph.topo_order(g)
        self.assertLess(order.index("flachs"), order.index("leinengarn"))
        self.assertLess(order.index("leinengarn"), order.index("leinengewebe"))
        self.assertLess(order.index("leinengewebe"), order.index("einfaches_leinenhemd"))

    def test_cycle_detection_flags_bad_data(self):
        bad = {"buildings": {"x": {"levels": {1: {"max_workers": 1, "can_produce": [
            {"output": "a", "rate_at_100": 1, "inputs": {"b": 1}},
            {"output": "b", "rate_at_100": 1, "inputs": {"a": 1}},
        ]}}}}}
        g = graph.build_recipe_graph(bad)
        self.assertTrue(graph.find_cycles(g))


class ChainEndpointTests(APITestCase):
    def test_get_returns_acyclic_chain(self):
        response = self.client.get(reverse("chain"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["cycles"], [])
        self.assertIn({"source": "flachs", "target": "leinengarn"}, body["edges"])
        self.assertEqual(body["topo_order"][0], "flachs")


class BalanceEndpointTests(APITestCase):
    def test_post_returns_balance(self):
        response = self.client.post(reverse("balance"), SETTLEMENT, format="json")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["errors"], [])
        self.assertAlmostEqual(body["balance"]["flachs"], -100)

    def test_unknown_building_is_rejected(self):
        bad = {"population": 0, "buildings": [
            {"type": "no_such_hut", "level": 1, "workers": 1, "allocation": {}}
        ]}
        response = self.client.post(reverse("balance"), bad, format="json")
        self.assertEqual(response.status_code, 400)
