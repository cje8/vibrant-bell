import math
import unittest

from co2_path import (
    ChannelEvidence,
    Citation,
    ExperimentLedger,
    GroundStatePESLedger,
    NuclearTubeConjecture,
    ProblemContract,
    ThermochemistryLedger,
    neutral_atomic_carbon_channel,
    photon_energy_ev,
)


class ChannelEvidenceTests(unittest.TestCase):
    def test_ledgers_are_separate_objects(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertIsInstance(evidence, ChannelEvidence)
        self.assertIsInstance(evidence.experiment, ExperimentLedger)
        self.assertIsInstance(evidence.thermochemistry, ThermochemistryLedger)
        self.assertIsInstance(evidence.ground_state_pes, GroundStatePESLedger)
        self.assertIsInstance(evidence.nuclear_tube, NuclearTubeConjecture)
        self.assertIsInstance(evidence.problem, ProblemContract)

    def test_full_state_space_has_no_unique_min_action_path(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertFalse(evidence.problem.unique_min_action_path_in_full_state_space)
        self.assertFalse(evidence.nuclear_tube.observed)
        self.assertIn("conjecture", evidence.nuclear_tube.status)
        self.assertTrue(
            any("unique" in question for question in evidence.problem.ill_posed_questions)
        )
        self.assertTrue(
            any(
                "field-free" in question
                for question in evidence.problem.ill_posed_questions
            )
        )

    def test_experiment_detected_carbon_and_inferred_oxygen(self):
        experiment = neutral_atomic_carbon_channel().experiment
        self.assertEqual(experiment.detected_fragment, "C(3P)")
        self.assertEqual(experiment.inferred_coproduct, "O2(X 3Sigma_g-)")
        self.assertFalse(experiment.coproduct_directly_detected)
        self.assertFalse(experiment.total_spin_measured)
        self.assertTrue(experiment.total_spin_compatible_with_singlet)
        self.assertIn("not a measurement", experiment.total_spin_compatibility_source)
        self.assertEqual(experiment.reported_channel_yield_percent, 5.0)
        self.assertFalse(experiment.yield_reanalyzed_here)
        self.assertEqual(experiment.observed_vuv_short_nm, 101.5)
        self.assertEqual(experiment.observed_vuv_long_nm, 107.2)

    def test_observed_photon_energies_are_hc_over_lambda(self):
        experiment = neutral_atomic_carbon_channel().experiment
        threshold = neutral_atomic_carbon_channel().thermochemistry.literature_threshold_ev
        self.assertAlmostEqual(
            experiment.observed_photon_energy_high_ev,
            photon_energy_ev(experiment.observed_vuv_short_nm),
        )
        self.assertAlmostEqual(
            experiment.observed_photon_energy_low_ev,
            photon_energy_ev(experiment.observed_vuv_long_nm),
        )
        self.assertGreater(experiment.observed_photon_energy_low_ev, threshold)
        self.assertGreater(
            experiment.observed_photon_energy_high_ev,
            experiment.observed_photon_energy_low_ev,
        )
        self.assertAlmostEqual(experiment.observed_photon_energy_low_ev, 11.566, places=3)
        self.assertAlmostEqual(experiment.observed_photon_energy_high_ev, 12.215, places=3)

    def test_literature_threshold_is_not_derived_here(self):
        thermochemistry = neutral_atomic_carbon_channel().thermochemistry
        self.assertEqual(thermochemistry.literature_threshold_ev, 11.44)
        self.assertFalse(thermochemistry.derived_here)

    def test_oco_ooc_landmarks_are_ground_state_o_plus_co_points(self):
        pes = neutral_atomic_carbon_channel().ground_state_pes
        self.assertEqual(pes.linear_ooc_minimum_ev_above_oco, 7.37)
        self.assertEqual(pes.oco_ooc_barrier_ev_above_ooc, 0.369)
        self.assertLess(
            pes.oco_ooc_barrier_ev_above_ooc,
            pes.linear_ooc_minimum_ev_above_oco,
        )
        self.assertIn("O+CO", pes.ooc_nuclear_arrangement)
        self.assertEqual(pes.ooc_electronic_state, "1A'")

    def test_nuclear_tube_is_not_on_the_experiment_ledger(self):
        evidence = neutral_atomic_carbon_channel()
        self.assertNotEqual(evidence.nuclear_tube.sequence, ())
        self.assertNotIn("cyclic", evidence.experiment.detected_fragment)
        self.assertNotIn("OOC", evidence.experiment.inferred_coproduct)

    def test_package_cannot_compute_a_branching_ratio_or_hamiltonian_orbit(self):
        joined = " ".join(
            neutral_atomic_carbon_channel().problem.uncomputable_with_this_package
        ).lower()
        self.assertIn("branching", joined)
        self.assertIn("origin", joined)
        self.assertIn("orbit", joined)
        self.assertIn("anandan", joined)

    def test_citations_are_bound_to_what_they_warrant(self):
        evidence = neutral_atomic_carbon_channel()
        by_doi = {citation.doi: citation.warrants for citation in evidence.references}
        self.assertIn("10.1126/science.1257156", by_doi)
        self.assertIn("inferred", by_doi["10.1126/science.1257156"].lower())
        self.assertIn("O+CO", by_doi["10.1039/d1cp01101d"])
        self.assertIn("not a C+O2 flux", by_doi["10.1063/1.4808369"])
        self.assertIn("101.5-107.2 nm", by_doi["10.1063/1.4808369"])
        self.assertIn("energy uncertainty", by_doi["10.1103/PhysRevLett.65.1697"])
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
