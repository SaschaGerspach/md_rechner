from django.urls import reverse
from rest_framework.test import APITestCase

from . import calc
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

    def test_validate_flags_too_many_workers(self):
        bad = {"population": 0, "buildings": [
            {"type": "sewing_hut", "level": 3, "workers": 3, "allocation": {"leinengarn": 100}}
        ]}
        errors = calc.validate(bad, STATIC)
        self.assertEqual(len(errors), 1)
        self.assertIn("workers", errors[0])


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
