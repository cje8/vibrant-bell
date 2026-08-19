import unittest

from co2_path import discrete_euclidean_action, maximum_potential


class ActionTests(unittest.TestCase):
    def test_constant_velocity_free_path(self):
        action = discrete_euclidean_action(
            path=((0.0,), (1.0,), (2.0,)),
            potentials=(0.0, 0.0, 0.0),
            masses=(2.0,),
            delta_tau=1.0,
        )
        self.assertAlmostEqual(action, 2.0)

    def test_potential_uses_trapezoidal_rule(self):
        action = discrete_euclidean_action(
            path=((0.0,), (0.0,)),
            potentials=(1.0, 3.0),
            masses=(1.0,),
            delta_tau=0.5,
        )
        self.assertAlmostEqual(action, 1.0)

    def test_dimension_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(((0.0,), (1.0,)), (0.0, 0.0), (1.0, 1.0), 1.0)

    def test_maximum_potential(self):
        self.assertEqual(maximum_potential([-1.0, 2.0, 0.5]), 2.0)


if __name__ == "__main__":
    unittest.main()
