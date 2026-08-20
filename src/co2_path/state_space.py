"""Geometry of normalized pure-state rays.

These functions construct a projective-Hilbert-space geodesic.  They do not
claim that the physical CO2 Hamiltonian generates that geodesic.  The
Anandan–Aharonov length of a Hamiltonian orbit is a different number: the
time integral of energy uncertainty along that orbit.
"""

from __future__ import annotations

import cmath
import math
from collections.abc import Iterable, Sequence

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
    return math.acos(min(1.0, overlap))


def geodesic_state(
    initial: Iterable[complex], final: Iterable[complex], fraction: float
) -> State:
    """Return one shortest-geodesic representative between two pure-state rays.

    ``fraction`` must lie in ``[0, 1]``.  The returned final vector can differ
    from the supplied final vector by a global phase, which represents the same
    physical ray.  Orthogonal endpoints admit phase-related alternatives; this
    routine chooses the phase already present in ``final``.
    """

    if not math.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must lie in [0, 1]")

    start = normalize(initial)
    end = normalize(final)
    if len(start) != len(end):
        raise ValueError("state vectors must have equal dimensions")

    overlap = _inner(start, end)
    magnitude = min(1.0, abs(overlap))
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


def anandan_aharonov_length(
    energy_uncertainties: Sequence[float],
    delta_t: Sequence[float],
) -> float:
    """Return ``(2/ħ) ∫ ΔE(t) dt`` for a supplied energy-uncertainty series.

    Units are ``ħ = 1``.  ``energy_uncertainties`` are ``ΔE(t)`` samples along
    a Hamiltonian orbit, not Fubini–Study distances between endpoint rays.
    ``delta_t`` is one positive real-time width per interval; a uniform step
    does not specify the orbit.  Two rays alone do not determine this length.
    The Fubini–Study geodesic distance is a lower bound on every such orbit
    length.
    """

    values = tuple(float(value) for value in energy_uncertainties)
    if len(values) < 2:
        raise ValueError("an orbit requires at least two energy-uncertainty samples")
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("energy uncertainties must be finite and non-negative")
    n_intervals = len(values) - 1
    if isinstance(delta_t, (str, bytes)) or not isinstance(delta_t, Sequence):
        raise ValueError("one positive delta_t is required per orbit interval")
    if len(delta_t) != n_intervals:
        raise ValueError("one positive delta_t is required per orbit interval")
    steps = tuple(float(step) for step in delta_t)
    if any(not math.isfinite(step) or step <= 0.0 for step in steps):
        raise ValueError("delta_t must be positive")

    integral = 0.0
    for (left, right), step in zip(zip(values, values[1:]), steps, strict=True):
        integral += 0.5 * (left + right) * step
    return 2.0 * integral
