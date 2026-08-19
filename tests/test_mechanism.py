import unittest

from co2_path import neutral_atomic_carbon_channel


class MechanismTests(unittest.TestCase):
    def test_evidence_record_does_not_claim_an_exact_path(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertFalse(evidence.exact_unique_path_known)
        self.assertEqual(evidence.thermochemical_threshold_ev, 11.44)
        self.assertIn("cyclic c-CO2 (1A1)", evidence.steps)


if __name__ == "__main__":
    unittest.main()
