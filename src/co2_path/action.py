"""Evaluators for candidate paths on a supplied nuclear potential."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def _is_finite_number(value: float) -> bool:
    return math.isfinite(float(value))


def _as_mass_table(
    masses: Sequence[Sequence[float]], n_images: int
) -> tuple[tuple[float, ...], ...]:
    if isinstance(masses, (str, bytes)) or not isinstance(masses, Sequence):
        raise ValueError("one mass vector is required per path image")
    if len(masses) != n_images:
        raise ValueError("one mass vector is required per path image")
    table = []
    for entry in masses:
        if isinstance(entry, (str, bytes)) or not isinstance(entry, Sequence):
            raise ValueError("each mass entry must be a vector, one per path image")
        vector = tuple(float(mass) for mass in entry)
        if not vector:
            raise ValueError("each mass vector must be non-empty")
        table.append(vector)
    return tuple(table)


def _validate_path(
    path: Sequence[Sequence[float]],
    masses: Sequence[Sequence[float]],
) -> tuple[tuple[float, ...], ...]:
    if len(path) < 2:
        raise ValueError("a path requires at least two images")
    mass_table = _as_mass_table(masses, len(path))
    if any(len(mass_vector) != len(image) for mass_vector, image in zip(mass_table, path, strict=True)):
        raise ValueError("every mass vector must match its path-image dimension")
    if any(
        not _is_finite_number(mass) or mass <= 0.0
        for mass_vector in mass_table
        for mass in mass_vector
    ):
        raise ValueError("all coordinate masses must be positive")
    if any(not _is_finite_number(coordinate) for image in path for coordinate in image):
        raise ValueError("path coordinates must be finite")
    return mass_table


def discrete_euclidean_action(
    path: Sequence[Sequence[float]],
    potentials: Sequence[float],
    masses: Sequence[Sequence[float]],
    delta_tau: float,
    potential_origin: float,
) -> float:
    """Evaluate a trapezoidal, fixed-time discretization of Euclidean action.

    Returns the nuclear action

        S = ∫ dτ [½ m(q) (dq/dτ)² + (V(q) − V₀)]

    not ``S/ℏ`` and not a Hilbert-space geometric length.  ``masses`` is one
    positive mass vector per image, because a Jacobi angle does not have a
    constant Cartesian mass.  Interval kinetic energy uses the average of the
    two endpoint mass vectors.  ``potential_origin`` is the energy zero
    ``V₀``; without it a constant shift in ``V`` would change ``S`` by
    ``V₀ × τ`` and could not be compared to an instanton.  The caller must
    supply ``V``.  This does not locate an instanton or include electronic
    transitions.
    """

    mass_table = _validate_path(path, masses)
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
        mass_left = mass_table[index]
        mass_right = mass_table[index + 1]
        velocity_squared = sum(
            0.5 * (m_left + m_right) * ((q_right - q_left) / delta_tau) ** 2
            for m_left, m_right, q_left, q_right in zip(
                mass_left, mass_right, left, right, strict=True
            )
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
