import unittest

from co2_path import neutral_atomic_carbon_channel


class MechanismTests(unittest.TestCase):
    def test_evidence_record_does_not_claim_an_exact_path(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertFalse(evidence.exact_unique_path_known)
        self.assertEqual(evidence.thermochemical_threshold_ev, 11.44)
        self.assertIn("cyclic c-CO2 (1A1)", evidence.steps)

    def test_oco_ooc_barrier_is_relative_to_the_ooc_minimum(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertEqual(evidence.linear_ooc_minimum_ev_above_oco, 7.37)
        self.assertEqual(evidence.oco_ooc_barrier_ev_above_ooc, 0.369)
        self.assertLess(
            evidence.oco_ooc_barrier_ev_above_ooc,
            evidence.linear_ooc_minimum_ev_above_oco,
        )

    def test_primary_dois_match_cited_literature(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertIn("10.1126/science.1257156", evidence.references)
        self.assertIn("10.1039/d1cp01101d", evidence.references)
        self.assertNotIn("10.1039/d1cp00369g", evidence.references)


if __name__ == "__main__":
    unittest.main()
