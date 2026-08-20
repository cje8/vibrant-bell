"""Evaluators for candidate paths on a supplied nuclear potential."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def _is_finite_number(value: float) -> bool:
    return math.isfinite(float(value))


def _validate_path(path: Sequence[Sequence[float]], masses: Sequence[float]) -> None:
    if len(path) < 2:
        raise ValueError("a path requires at least two images")
    if not masses or any(not _is_finite_number(mass) or mass <= 0.0 for mass in masses):
        raise ValueError("all coordinate masses must be positive")
    if any(len(image) != len(masses) for image in path):
        raise ValueError("every path image must match the mass-vector dimension")
    if any(not _is_finite_number(coordinate) for image in path for coordinate in image):
        raise ValueError("path coordinates must be finite")


def discrete_euclidean_action(
    path: Sequence[Sequence[float]],
    potentials: Sequence[float],
    masses: Sequence[float],
    delta_tau: float,
    potential_origin: float,
) -> float:
    """Evaluate a trapezoidal, fixed-time discretization of Euclidean action.

    Returns the nuclear action

        S = ∫ dτ [½ m (dq/dτ)² + (V(q) − V₀)]

    not ``S/ℏ`` and not a Hilbert-space geometric length.  ``potential_origin``
    is the energy zero ``V₀``; without it a constant shift in ``V`` would change
    ``S`` by ``V₀ × τ`` and could not be compared to an instanton.  The caller
    must supply ``V``.  This does not locate an instanton or include electronic
    transitions.
    """

    _validate_path(path, masses)
    if len(potentials) != len(path):
        raise ValueError("one potential value is required per path image")
    if any(not _is_finite_number(value) for value in potentials):
        raise ValueError("potential values must be finite")
    if not math.isfinite(delta_tau) or delta_tau <= 0.0:
        raise ValueError("delta_tau must be positive")
    if not _is_finite_number(potential_origin):
        raise ValueError("potential_origin must be finite")

    action = 0.0
    for index, (left, right) in enumerate(zip(path, path[1:])):
        velocity_squared = sum(
            mass * ((q_right - q_left) / delta_tau) ** 2
            for mass, q_left, q_right in zip(masses, left, right, strict=True)
        )
        kinetic = 0.5 * velocity_squared
        potential = 0.5 * (
            (potentials[index] - potential_origin)
            + (potentials[index + 1] - potential_origin)
        )
        action += (kinetic + potential) * delta_tau
    return action


def maximum_potential(potentials: Iterable[float]) -> float:
    """Return the maximum energy sampled by a candidate MEP image sequence."""

    values = tuple(float(value) for value in potentials)
    if not values:
        raise ValueError("at least one potential value is required")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("potential values must be finite")
    return max(values)
