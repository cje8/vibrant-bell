import math
import unittest

from co2_path import ChannelEvidence, neutral_atomic_carbon_channel, photon_energy_ev


class ChannelEvidenceTests(unittest.TestCase):
    def test_full_state_space_has_no_unique_min_action_path(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertFalse(evidence.unique_min_action_path_in_full_state_space)
        self.assertFalse(evidence.sequential_nuclear_tube_observed)
        self.assertIn("conjecture", evidence.sequential_nuclear_tube_status)

    def test_experiment_is_a_product_channel_not_a_nuclear_sequence(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertEqual(evidence.observed_yield_percent, 5.0)
        self.assertEqual(evidence.observed_vuv_short_nm, 101.5)
        self.assertEqual(evidence.observed_vuv_long_nm, 107.2)
        self.assertNotEqual(evidence.conjectured_nuclear_sequence, ())
        self.assertIsInstance(evidence, ChannelEvidence)

    def test_observed_photon_energies_are_hc_over_lambda(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertAlmostEqual(
            evidence.observed_photon_energy_high_ev,
            photon_energy_ev(evidence.observed_vuv_short_nm),
        )
        self.assertAlmostEqual(
            evidence.observed_photon_energy_low_ev,
            photon_energy_ev(evidence.observed_vuv_long_nm),
        )
        self.assertGreater(
            evidence.observed_photon_energy_low_ev,
            evidence.literature_threshold_ev,
        )
        self.assertGreater(
            evidence.observed_photon_energy_high_ev,
            evidence.observed_photon_energy_low_ev,
        )
        self.assertAlmostEqual(evidence.observed_photon_energy_low_ev, 11.566, places=3)
        self.assertAlmostEqual(evidence.observed_photon_energy_high_ev, 12.215, places=3)

    def test_oco_ooc_landmarks_are_ground_state_o_plus_co_points(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertEqual(evidence.linear_ooc_minimum_ev_above_oco, 7.37)
        self.assertEqual(evidence.oco_ooc_barrier_ev_above_ooc, 0.369)
        self.assertLess(
            evidence.oco_ooc_barrier_ev_above_ooc,
            evidence.linear_ooc_minimum_ev_above_oco,
        )
        self.assertIn("O+CO", evidence.ooc_nuclear_arrangement)
        self.assertEqual(evidence.ooc_electronic_state, "1A'")

    def test_well_posed_questions_do_not_include_a_unique_full_space_path(self):
        evidence = neutral_atomic_carbon_channel()
        joined = " ".join(evidence.well_posed_questions).lower()
        self.assertNotIn("unique", joined)
        self.assertIn("geodesic", joined)
        self.assertIn("flux", joined)

    def test_primary_dois_match_cited_literature(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertIn("10.1126/science.1257156", evidence.references)
        self.assertIn("10.1039/d1cp01101d", evidence.references)
        self.assertNotIn("10.1039/d1cp00369g", evidence.references)

    def test_photon_energy_rejects_non_physical_wavelengths(self):
        with self.assertRaises(ValueError):
            photon_energy_ev(0.0)
        with self.assertRaises(ValueError):
            photon_energy_ev(float("nan"))

    def test_photon_energy_matches_codata_2018_hc(self):
        self.assertTrue(math.isfinite(photon_energy_ev(107.2)))
        self.assertAlmostEqual(photon_energy_ev(1239.8419843320025), 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
