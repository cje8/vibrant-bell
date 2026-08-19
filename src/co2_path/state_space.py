"""Geometry of normalized pure-state rays.

These functions construct a projective-Hilbert-space geodesic.  They do not
claim that the physical CO2 Hamiltonian generates that geodesic.
"""

from __future__ import annotations

import cmath
import math
from collections.abc import Iterable

State = tuple[complex, ...]


def _as_state(values: Iterable[complex]) -> State:
    state = tuple(complex(value) for value in values)
    if not state:
        raise ValueError("a state vector must not be empty")
    return state


def _inner(left: State, right: State) -> complex:
    if len(left) != len(right):
        raise ValueError("state vectors must have equal dimensions")
    return sum(a.conjugate() * b for a, b in zip(left, right, strict=True))


def normalize(values: Iterable[complex]) -> State:
    """Return a normalized copy of a nonzero complex vector."""

    state = _as_state(values)
    norm_squared = _inner(state, state).real
    if norm_squared <= 0.0:
        raise ValueError("a state vector must have nonzero norm")
    norm = math.sqrt(norm_squared)
    return tuple(value / norm for value in state)


def fubini_study_distance(initial: Iterable[complex], final: Iterable[complex]) -> float:
    """Return ``acos(abs(<initial|final>))`` for normalized endpoint rays."""

    start = normalize(initial)
    end = normalize(final)
    overlap = abs(_inner(start, end))
    return math.acos(min(1.0, max(0.0, overlap)))


def geodesic_state(
    initial: Iterable[complex], final: Iterable[complex], fraction: float
) -> State:
    """Return one shortest-geodesic representative between two pure-state rays.

    ``fraction`` must lie in ``[0, 1]``.  The returned final vector can differ
    from the supplied final vector by a global phase, which represents the same
    physical ray.  Orthogonal endpoints admit phase-related alternatives; this
    routine chooses the phase already present in ``final``.
    """

    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must lie in [0, 1]")

    start = normalize(initial)
    end = normalize(final)
    if len(start) != len(end):
        raise ValueError("state vectors must have equal dimensions")

    overlap = _inner(start, end)
    magnitude = min(1.0, max(0.0, abs(overlap)))
    if magnitude > 1.0 - 1e-14:
        return start

    if magnitude > 1e-14:
        end = tuple(cmath.exp(-1j * cmath.phase(overlap)) * value for value in end)

    angle = math.acos(magnitude)
    sine = math.sin(angle)
    perpendicular = tuple(
        (end_value - magnitude * start_value) / sine
        for start_value, end_value in zip(start, end, strict=True)
    )
    point = tuple(
        math.cos(fraction * angle) * start_value
        + math.sin(fraction * angle) * perpendicular_value
        for start_value, perpendicular_value in zip(start, perpendicular, strict=True)
    )
    return normalize(point)
