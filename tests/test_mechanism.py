import math
import unittest

from co2_path import ChannelEvidence, Citation, neutral_atomic_carbon_channel, photon_energy_ev


class ChannelEvidenceTests(unittest.TestCase):
    def test_full_state_space_has_no_unique_min_action_path(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertFalse(evidence.unique_min_action_path_in_full_state_space)
        self.assertFalse(evidence.sequential_nuclear_tube_observed)
        self.assertIn("conjecture", evidence.sequential_nuclear_tube_status)
        self.assertTrue(
            any("unique" in question for question in evidence.ill_posed_questions)
        )

    def test_experiment_detected_carbon_and_inferred_oxygen(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertEqual(evidence.detected_fragment, "C(3P)")
        self.assertEqual(evidence.inferred_coproduct, "O2(X 3Sigma_g-)")
        self.assertFalse(evidence.coproduct_directly_detected)
        self.assertFalse(evidence.total_spin_measured)
        self.assertTrue(evidence.total_spin_compatible_with_singlet)
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

    def test_literature_threshold_is_not_derived_here(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertEqual(evidence.literature_threshold_ev, 11.44)
        self.assertFalse(evidence.literature_threshold_derived_here)

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

    def test_package_cannot_compute_a_branching_ratio_or_hamiltonian_orbit(self):
        evidence = neutral_atomic_carbon_channel()
        joined = " ".join(evidence.uncomputable_with_this_package).lower()
        self.assertIn("branching", joined)
        self.assertIn("potential", joined)
        self.assertIn("orbit", joined)

    def test_citations_are_bound_to_what_they_warrant(self):
        evidence = neutral_atomic_carbon_channel()
        by_doi = {citation.doi: citation.warrants for citation in evidence.references}
        self.assertIn("10.1126/science.1257156", by_doi)
        self.assertIn("inferred", by_doi["10.1126/science.1257156"].lower())
        self.assertIn("O+CO", by_doi["10.1039/d1cp01101d"])
        self.assertIn("not a C+O2 flux", by_doi["10.1063/1.4808369"])
        self.assertNotIn("10.1039/d1cp00369g", by_doi)
        self.assertTrue(all(isinstance(item, Citation) for item in evidence.references))

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
