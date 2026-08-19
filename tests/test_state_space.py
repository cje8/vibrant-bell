import math
import unittest

from co2_path import fubini_study_distance, geodesic_state, normalize


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

    def test_fraction_is_validated(self):
        with self.assertRaises(ValueError):
            geodesic_state([1, 0], [0, 1], 1.1)


if __name__ == "__main__":
    unittest.main()
