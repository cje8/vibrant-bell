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
        distance = fubini_study_distance([1, 0], [0, 1])
        self.assertAlmostEqual(distance, math.pi / 2)

    def test_global_phase_has_zero_distance(self):
        self.assertAlmostEqual(fubini_study_distance([1, 0], [1j, 0]), 0.0)

    def test_geodesic_midpoint_is_normalized(self):
        midpoint = geodesic_state([1, 0], [0, 1], 0.5)
        norm = sum(abs(value) ** 2 for value in midpoint)
        self.assertAlmostEqual(norm, 1.0)
        self.assertAlmostEqual(abs(midpoint[0]), math.sqrt(0.5))
        self.assertAlmostEqual(abs(midpoint[1]), math.sqrt(0.5))

    def test_geodesic_parameter_is_arc_length_fraction(self):
        initial = [1 + 2j, 3 - 1j, 0.5]
        final = [0.2 - 0.7j, 1j, 2]
        total = fubini_study_distance(initial, final)
        for fraction in (0.0, 0.3, 0.7, 1.0):
            point = geodesic_state(initial, final, fraction)
            self.assertAlmostEqual(
                fubini_study_distance(initial, point),
                fraction * total,
            )

    def test_fraction_is_validated(self):
        with self.assertRaises(ValueError):
            geodesic_state([1, 0], [0, 1], 1.1)
        with self.assertRaises(ValueError):
            geodesic_state([1, 0], [0, 1], float("nan"))

    def test_anandan_aharonov_length_is_not_the_endpoint_geodesic(self):
        geodesic = fubini_study_distance([1, 0], [0, 1])
        orbit = anandan_aharonov_length((0.5, 0.5, 0.5), 1.0)
        self.assertAlmostEqual(orbit, 2.0)
        self.assertGreater(orbit, geodesic)

    def test_anandan_aharonov_length_rejects_a_single_sample(self):
        with self.assertRaises(ValueError):
            anandan_aharonov_length((0.5,), 1.0)
        with self.assertRaises(ValueError):
            anandan_aharonov_length((0.5, -0.1), 1.0)


if __name__ == "__main__":
    unittest.main()
