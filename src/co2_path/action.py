"""Evaluators for candidate paths on a supplied nuclear potential."""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def _validate_path(path: Sequence[Sequence[float]], masses: Sequence[float]) -> None:
    if len(path) < 2:
        raise ValueError("a path requires at least two images")
    if not masses or any(mass <= 0.0 for mass in masses):
        raise ValueError("all coordinate masses must be positive")
    if any(len(image) != len(masses) for image in path):
        raise ValueError("every path image must match the mass-vector dimension")


def discrete_euclidean_action(
    path: Sequence[Sequence[float]],
    potentials: Sequence[float],
    masses: Sequence[float],
    delta_tau: float,
) -> float:
    """Evaluate a trapezoidal, fixed-time discretization of Euclidean action.

    The caller supplies coordinate images, potential values at those images,
    diagonal coordinate masses, and a positive imaginary-time step.  Units must
    be mutually consistent.  This function evaluates a path; it does not claim
    to locate an instanton or account for electronic-state transitions.
    """

    _validate_path(path, masses)
    if len(potentials) != len(path):
        raise ValueError("one potential value is required per path image")
    if delta_tau <= 0.0:
        raise ValueError("delta_tau must be positive")

    action = 0.0
    for index, (left, right) in enumerate(zip(path, path[1:])):
        velocity_squared = sum(
            mass * ((q_right - q_left) / delta_tau) ** 2
            for mass, q_left, q_right in zip(masses, left, right, strict=True)
        )
        kinetic = 0.5 * velocity_squared
        potential = 0.5 * (potentials[index] + potentials[index + 1])
        action += (kinetic + potential) * delta_tau
    return action


def maximum_potential(potentials: Iterable[float]) -> float:
    """Return the maximum energy sampled by a candidate MEP image sequence."""

    values = tuple(float(value) for value in potentials)
    if not values:
        raise ValueError("at least one potential value is required")
    return max(values)
