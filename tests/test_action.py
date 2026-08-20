import unittest

from co2_path import discrete_euclidean_action, maximum_potential


class ActionTests(unittest.TestCase):
    def test_constant_velocity_free_path(self):
        action = discrete_euclidean_action(
            path=((0.0,), (1.0,), (2.0,)),
            potentials=(0.0, 0.0, 0.0),
            masses=((2.0,), (2.0,), (2.0,)),
            delta_tau=(1.0, 1.0),
            potential_origin=0.0,
        )
        self.assertAlmostEqual(action, 2.0)

    def test_potential_uses_trapezoidal_rule(self):
        action = discrete_euclidean_action(
            path=((0.0,), (0.0,)),
            potentials=(1.0, 3.0),
            masses=((1.0,), (1.0,)),
            delta_tau=(0.5,),
            potential_origin=0.0,
        )
        self.assertAlmostEqual(action, 1.0)

    def test_action_is_invariant_under_a_shift_of_potential_and_origin(self):
        kwargs = dict(
            path=((0.0,), (1.0,), (2.0,)),
            masses=((2.0,), (2.0,), (2.0,)),
            delta_tau=(1.0, 1.0),
        )
        unshifted = discrete_euclidean_action(
            potentials=(1.0, 1.0, 1.0),
            potential_origin=1.0,
            **kwargs,
        )
        shifted = discrete_euclidean_action(
            potentials=(4.0, 4.0, 4.0),
            potential_origin=4.0,
            **kwargs,
        )
        self.assertAlmostEqual(unshifted, shifted)
        self.assertAlmostEqual(unshifted, 2.0)

    def test_omitting_the_origin_would_make_a_constant_potential_change_the_action(self):
        kwargs = dict(
            path=((0.0,), (1.0,)),
            masses=((2.0,), (2.0,)),
            delta_tau=(1.0,),
            potential_origin=0.0,
        )
        low = discrete_euclidean_action(potentials=(0.0, 0.0), **kwargs)
        high = discrete_euclidean_action(potentials=(3.0, 3.0), **kwargs)
        self.assertAlmostEqual(high - low, 3.0)

    def test_position_dependent_mass_is_averaged_on_each_interval(self):
        action = discrete_euclidean_action(
            path=((0.0,), (1.0,)),
            potentials=(0.0, 0.0),
            masses=((1.0,), (3.0,)),
            delta_tau=(1.0,),
            potential_origin=0.0,
        )
        self.assertAlmostEqual(action, 1.0)

    def test_constant_mass_vector_is_rejected_as_one_image(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,)),
                (0.0, 0.0),
                (1.0, 1.0),
                (1.0,),
                0.0,
            )

    def test_dimension_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,)),
                (0.0, 0.0),
                ((1.0, 1.0), (1.0, 1.0)),
                (1.0,),
                0.0,
            )

    def test_scalar_time_step_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,)),
                (0.0, 0.0),
                ((1.0,), (1.0,)),
                1.0,
                0.0,
            )

    def test_wrong_number_of_time_steps_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,), (2.0,)),
                (0.0, 0.0, 0.0),
                ((1.0,), (1.0,), (1.0,)),
                (1.0,),
                0.0,
            )

    def test_uneven_time_steps_are_accepted(self):
        action = discrete_euclidean_action(
            path=((0.0,), (0.0,), (0.0,)),
            potentials=(0.0, 2.0, 2.0),
            masses=((1.0,), (1.0,), (1.0,)),
            delta_tau=(1.0, 3.0),
            potential_origin=0.0,
        )
        self.assertAlmostEqual(action, 1.0 + 6.0)

    def test_non_finite_step_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,)),
                (0.0, 0.0),
                ((1.0,), (1.0,)),
                (float("nan"),),
                0.0,
            )

    def test_non_finite_origin_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,)),
                (0.0, 0.0),
                ((1.0,), (1.0,)),
                (1.0,),
                float("nan"),
            )

    def test_non_finite_coordinates_are_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((float("nan"),), (1.0,)),
                (0.0, 0.0),
                ((1.0,), (1.0,)),
                (1.0,),
                0.0,
            )

    def test_non_finite_path_potential_is_rejected(self):
        with self.assertRaises(ValueError):
            discrete_euclidean_action(
                ((0.0,), (1.0,)),
                (0.0, float("inf")),
                ((1.0,), (1.0,)),
                (1.0,),
                0.0,
            )

    def test_maximum_potential(self):
        self.assertEqual(maximum_potential([-1.0, 2.0, 0.5]), 2.0)

    def test_non_finite_potential_is_rejected(self):
        with self.assertRaises(ValueError):
            maximum_potential([1.0, float("inf")])


if __name__ == "__main__":
    unittest.main()
