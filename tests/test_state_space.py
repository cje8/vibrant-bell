import math
import unittest

from co2_path import (
    anandan_aharonov_length,
    fubini_study_distance,
    geodesic_state,
    normalize,
)


class StateSpaceTests(unittest.TestCase):
    def test_normalize_rejects_zero_vector(self):
        with self.assertRaises(ValueError):
            normalize([0, 0])

    def test_orthogonal_distance_is_pi_over_two(self):
        distance = fubini_study_distance([1, 0], [0, 1], "C^2-test")
        self.assertAlmostEqual(distance, math.pi / 2)

    def test_global_phase_has_zero_distance(self):
        self.assertAlmostEqual(
            fubini_study_distance([1, 0], [1j, 0], "C^2-test"), 0.0
        )

    def test_geodesic_midpoint_is_normalized(self):
        midpoint = geodesic_state([1, 0], [0, 1], 0.5, "C^2-test")
        norm = sum(abs(value) ** 2 for value in midpoint)
        self.assertAlmostEqual(norm, 1.0)
        self.assertAlmostEqual(abs(midpoint[0]), math.sqrt(0.5))
        self.assertAlmostEqual(abs(midpoint[1]), math.sqrt(0.5))

    def test_geodesic_parameter_is_arc_length_fraction(self):
        initial = [1 + 2j, 3 - 1j, 0.5]
        final = [0.2 - 0.7j, 1j, 2]
        total = fubini_study_distance(initial, final, "C^3-test")
        for fraction in (0.0, 0.3, 0.7, 1.0):
            point = geodesic_state(initial, final, fraction, "C^3-test")
            self.assertAlmostEqual(
                fubini_study_distance(initial, point, "C^3-test"),
                fraction * total,
            )

    def test_fraction_is_validated(self):
        with self.assertRaises(ValueError):
            geodesic_state([1, 0], [0, 1], 1.1, "C^2-test")
        with self.assertRaises(ValueError):
            geodesic_state([1, 0], [0, 1], float("nan"), "C^2-test")

    def test_unnamed_hilbert_space_is_rejected(self):
        with self.assertRaises(ValueError):
            fubini_study_distance([1, 0], [0, 1], "")
        with self.assertRaises(ValueError):
            geodesic_state([1, 0], [0, 1], 0.5, "")

    def test_labeling_the_space_co2_is_rejected(self):
        with self.assertRaises(ValueError):
            fubini_study_distance([1, 0], [0, 1], "CO2")

    def test_anandan_aharonov_length_is_not_the_endpoint_geodesic(self):
        geodesic = fubini_study_distance([1, 0], [0, 1], "C^2-test")
        orbit = anandan_aharonov_length((0.5, 0.5, 0.5), (1.0, 1.0), "C^2-test")
        self.assertAlmostEqual(orbit, 2.0)
        self.assertGreater(orbit, geodesic)

    def test_anandan_aharonov_length_rejects_a_single_sample(self):
        with self.assertRaises(ValueError):
            anandan_aharonov_length((0.5,), (1.0,), "C^2-test")
        with self.assertRaises(ValueError):
            anandan_aharonov_length((0.5, -0.1), (1.0,), "C^2-test")

    def test_anandan_aharonov_length_rejects_a_scalar_time_step(self):
        with self.assertRaises(ValueError):
            anandan_aharonov_length((0.5, 0.5), 1.0, "C^2-test")


if __name__ == "__main__":
    unittest.main()
