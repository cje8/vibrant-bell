"""Serializable *declarations* for a finite diabatic wavepacket problem.

Validation checks structure and declared compatibility, not provider values,
global PES accuracy, Hermiticity, smoothness, or gauge continuity. No providers
are imported, executed, or downloaded by this module.
"""

from __future__ import annotations

import json
import math
import re
import types
from dataclasses import MISSING, asdict, dataclass, fields, is_dataclass
from typing import Literal, get_args, get_origin, get_type_hints


@dataclass(frozen=True)
class Bounds:
    """Closed bounds in the units of the corresponding chart axis."""

    lower: float
    upper: float


Domain = tuple[Bounds, Bounds, Bounds]
EnergyUnit = Literal["hartree", "eV"]


@dataclass(frozen=True)
class Isotopologue:
    label: str
    atoms: tuple[str, str, str]
    masses: tuple[float, float, float]
    mass_unit: Literal["u"] = "u"


@dataclass(frozen=True)
class JacobiChart:
    """atom_indices = (spectator, diatom atom 1, diatom atom 2)."""

    chart_id: str
    arrangement: Literal["O+CO", "C+O2"]
    atom_indices: tuple[int, int, int]
    coordinates: tuple[str, str, str]
    definitions: tuple[str, str, str]
    length_unit: Literal["bohr", "angstrom"]
    angle_unit: Literal["radian", "degree"]
    domain: Domain


@dataclass(frozen=True)
class ProviderReference:
    """An inert, versioned identifier; sha256 identifies the declared artifact."""

    provider_id: str
    source: str
    version: str
    sha256: str


@dataclass(frozen=True)
class PropertyProvider:
    reference: ProviderReference
    chart_id: str
    state_order: tuple[str, ...]
    basis_id: str
    gauge_id: str
    units: tuple[str, ...]
    domain: Domain
    representation: Literal["diabatic"] = "diabatic"


@dataclass(frozen=True)
class ElectronicState:
    label: str
    multiplicity: int
    symmetry: str


@dataclass(frozen=True)
class DiabaticModelContract:
    states: tuple[ElectronicState, ...]
    matrix_shape: tuple[int, int]
    basis_id: str
    gauge_id: str
    energy_unit: EnergyUnit
    energy_zero: str
    potential: PropertyProvider
    soc: PropertyProvider | None = None
    derivative_coupling: PropertyProvider | None = None
    required_spin_connections: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class RovibrationalState:
    vibration: tuple[int, ...]
    rotation: int


@dataclass(frozen=True)
class InitialRovibronicState:
    electronic_state: str
    J: int
    parity: Literal["+", "-"]
    rovibrational: RovibrationalState | None = None
    wavefunction: PropertyProvider | None = None


@dataclass(frozen=True)
class RadiationPreparation:
    """A linearly polarized preparation; envelope IDs are inert references."""

    energy_unit: EnergyUnit
    polarization: tuple[float, float, float]
    time_origin: float
    duration: float
    time_unit: Literal["fs", "atomic_time"]
    transition_dipole: PropertyProvider
    photon_energy: float | None = None
    envelope: ProviderReference | None = None
    kind: Literal["radiation"] = "radiation"


@dataclass(frozen=True)
class MicrocanonicalPreparation:
    total_energy: float
    energy_unit: EnergyUnit
    energy_zero: str
    kind: Literal["microcanonical"] = "microcanonical"


@dataclass(frozen=True)
class Evidence:
    status: Literal["measured", "inferred", "assumed"]
    source: str


@dataclass(frozen=True)
class JacobiTransform:
    """Declared source-to-target coverage, not an evaluated coordinate map."""

    reference: ProviderReference
    source_chart_id: str
    target_chart_id: str
    source_domain: Domain
    target_domain: Domain


@dataclass(frozen=True)
class ProductProjectorContract:
    channel_id: str
    chart: JacobiChart
    provider: PropertyProvider
    carbon_term: Literal["C(3P)"]
    oxygen_state: Literal["X 3Sigma_g-"]
    v: int
    j: int
    flux_R: float
    outward: Literal["increasing_R"]
    correlated_states: tuple[str, ...]
    assignment_evidence: Evidence
    total_spin: int | None = None
    spin_evidence: Evidence | None = None
    transform: JacobiTransform | None = None


@dataclass(frozen=True)
class WavepacketProblem:
    isotopologue: Isotopologue
    coordinate_chart: JacobiChart
    initial_state: InitialRovibronicState
    preparation: RadiationPreparation | MicrocanonicalPreparation
    electronic_model: DiabaticModelContract
    product_channels: tuple[ProductProjectorContract, ...]
    schema_version: Literal["1"] = "1"

    def to_json(self) -> str:
        """Validate and emit deterministic JSON (no NaN/Infinity extensions)."""

        problem = _typed(self, WavepacketProblem, "problem")
        validate_wavepacket_problem(problem)
        return json.dumps(
            asdict(problem), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )

    @classmethod
    def from_json(cls, text: str) -> WavepacketProblem:
        """Reject unknown fields, duplicate keys, unsupported versions and types."""

        _require(type(text) is str, "json", "expected a string")
        try:
            data = json.loads(
                text, object_pairs_hook=_unique_object,
                parse_constant=lambda value: _fail("json", f"non-finite {value}"),
            )
        except (json.JSONDecodeError, RecursionError) as exc:
            raise ValueError(f"json: malformed document ({exc})") from exc
        # Version and mode must be explicit in persisted input, even though the
        # Python constructors provide convenient defaults.
        _require(type(data) is dict, "problem", "expected an object")
        _require("schema_version" in data, "problem.schema_version", "required")
        preparation = data.get("preparation")
        _require(type(preparation) is dict and "kind" in preparation,
                 "problem.preparation.kind", "explicit preparation mode required")
        problem = _typed(data, cls, "problem", from_json=True)
        validate_wavepacket_problem(problem)
        return problem


def _fail(path: str, message: str):
    raise ValueError(f"{path}: {message}")


def _require(condition: bool, path: str, message: str) -> None:
    if not condition:
        _fail(path, message)


def _typed(value, expected, path: str, *, from_json: bool = False):
    """Small closed-schema reader shared by Python validation and JSON input.

    Only the annotations used above are supported. Mutable lists/dicts are not
    accepted inside Python contracts; JSON arrays become immutable tuples.
    """

    origin, args = get_origin(expected), get_args(expected)
    if origin is types.UnionType:
        errors = []
        for choice in args:
            try:
                return _typed(value, choice, path, from_json=from_json)
            except ValueError as exc:
                errors.append(str(exc))
        _fail(path, "no matching alternative (" + "; ".join(errors) + ")")
    if origin is Literal:
        _require(any(type(value) is type(option) and value == option for option in args),
                 path, f"expected one of {args!r}")
        return value
    if origin is tuple:
        _require(type(value) is (list if from_json else tuple), path,
                 "expected an array" if from_json else "expected an immutable tuple")
        repeated = len(args) == 2 and args[1] is Ellipsis
        _require(repeated or len(value) == len(args), path,
                 f"expected {len(args)} entries")
        return tuple(_typed(item, args[0] if repeated else args[i],
                            f"{path}[{i}]", from_json=from_json)
                     for i, item in enumerate(value))
    if is_dataclass(expected):
        _require(type(value) is (dict if from_json else expected), path,
                 f"expected {expected.__name__}")
        schema = fields(expected)
        hints = get_type_hints(expected)
        if from_json:
            unknown = set(value) - {field.name for field in schema}
            _require(not unknown, path, f"unknown fields: {sorted(unknown)!r}")
        result = {}
        for field in schema:
            key = f"{path}.{field.name}"
            if from_json and field.name not in value:
                _require(field.default is not MISSING, key, "required")
                result[field.name] = field.default
            else:
                item = value[field.name] if from_json else getattr(value, field.name)
                result[field.name] = _typed(item, hints[field.name], key, from_json=from_json)
        return expected(**result)
    if expected is float:
        _require(type(value) in (int, float), path, "expected a finite number, not bool")
        try:
            result = float(value)
        except OverflowError:
            _fail(path, "number is out of range")
        _require(math.isfinite(result), path, "expected a finite number")
        return 0.0 if result == 0 else result  # canonicalize negative zero
    _require(type(value) is expected, path, f"expected {expected.__name__}")
    if expected is str:
        _require(bool(value.strip()), path, "must not be blank")
    return value


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "json", f"duplicate key {key!r}")
        result[key] = value
    return result


def _domain(domain: Domain, path: str) -> None:
    for i, bound in enumerate(domain):
        _require(bound.lower < bound.upper, f"{path}[{i}]", "empty or reversed bounds")


def _covers(outer: Domain, inner: Domain, path: str) -> None:
    _domain(outer, path)
    _require(all(a.lower <= b.lower and a.upper >= b.upper for a, b in zip(outer, inner)),
             path, "does not cover the declared chart domain")


def _chart(chart: JacobiChart, molecule: Isotopologue, path: str) -> None:
    _require(chart.coordinates == ("R", "r", "theta"), path + ".coordinates",
             "must be exactly (R, r, theta)")
    _require(sorted(chart.atom_indices) == [0, 1, 2], path + ".atom_indices",
             "must be a permutation of atom indices 0, 1, 2")
    spectator, a, b = (molecule.atoms[i] for i in chart.atom_indices)
    composition = (spectator, sorted((a, b)))
    expected = ("C", ["O", "O"]) if chart.arrangement == "C+O2" else ("O", ["C", "O"])
    _require(composition == expected, path + ".atom_indices", "does not match arrangement")
    _domain(chart.domain, path + ".domain")
    _require(all(bound.lower > 0 for bound in chart.domain[:2]), path + ".domain",
             "R and r must be strictly positive")
    theta = chart.domain[2]
    limit = math.pi if chart.angle_unit == "radian" else 180.0
    _require(0 <= theta.lower < theta.upper <= limit, path + ".domain[2]",
             "theta must lie in [0, pi] radians or [0, 180] degrees")


def validate_wavepacket_problem(problem: WavepacketProblem) -> None:
    """Validate declared inputs, raising a field-addressed ValueError on failure.

    Passing is not a certificate of physical correctness or solver readiness.
    In particular, finite-domain coverage here is a claim, not a global proof.
    """

    p = _typed(problem, WavepacketProblem, "problem")
    molecule, chart, model = p.isotopologue, p.coordinate_chart, p.electronic_model
    _require(sorted(molecule.atoms) == ["C", "O", "O"], "problem.isotopologue.atoms",
             "expected one C and two O atoms")
    _require(all(m > 0 for m in molecule.masses), "problem.isotopologue.masses",
             "masses must be positive")
    _chart(chart, molecule, "problem.coordinate_chart")
    states = {state.label: state for state in model.states}
    order = tuple(state.label for state in model.states)
    _require(bool(states) and len(states) == len(model.states), "problem.electronic_model.states",
             "state labels must be nonempty and unique")
    _require(model.matrix_shape == (len(states), len(states)),
             "problem.electronic_model.matrix_shape", "must be square and match state count")
    for i, state in enumerate(model.states):
        _require(state.multiplicity > 0 and state.multiplicity % 2 == 1,
                 f"problem.electronic_model.states[{i}].multiplicity",
                 "neutral CO2 requires a positive odd spin multiplicity")

    # The same identifier cannot silently refer to different artifact versions
    # or property bindings within a single reproducible contract.
    references: dict[str, ProviderReference] = {}
    bindings: dict[str, PropertyProvider] = {}

    def reference(ref: ProviderReference, path: str) -> None:
        _require(re.fullmatch(r"[0-9a-f]{64}", ref.sha256) is not None,
                 path + ".sha256", "expected 64 lowercase hexadecimal characters")
        _require(ref.provider_id not in references or references[ref.provider_id] == ref,
                 path, "conflicting provider ID/provenance")
        references[ref.provider_id] = ref

    def provider(prop: PropertyProvider, target: JacobiChart, path: str,
                 allowed_units: tuple[tuple[str, ...], ...]) -> None:
        reference(prop.reference, path + ".reference")
        _require(prop.chart_id == target.chart_id, path + ".chart_id", "chart mismatch")
        _require(prop.state_order == order, path + ".state_order", "state order mismatch")
        _require(prop.basis_id == model.basis_id, path + ".basis_id", "basis mismatch")
        _require(prop.gauge_id == model.gauge_id, path + ".gauge_id", "gauge mismatch")
        _require(prop.units in allowed_units, path + ".units", f"expected {allowed_units!r}")
        _covers(prop.domain, target.domain, path + ".domain")
        key = prop.reference.provider_id
        _require(key not in bindings or bindings[key] == prop, path,
                 "conflicting property bindings for provider ID")
        bindings[key] = prop

    energy_units = ((model.energy_unit,),)
    provider(model.potential, chart, "problem.electronic_model.potential", energy_units)
    if model.soc is not None:
        provider(model.soc, chart, "problem.electronic_model.soc", energy_units)
    if model.derivative_coupling is not None:
        units = ((f"1/{chart.length_unit}", f"1/{chart.length_unit}", f"1/{chart.angle_unit}"),)
        provider(model.derivative_coupling, chart,
                 "problem.electronic_model.derivative_coupling", units)
    for i, (a, b) in enumerate(model.required_spin_connections):
        path = f"problem.electronic_model.required_spin_connections[{i}]"
        _require(a in states and b in states and a != b, path, "expected two distinct known states")
        if states[a].multiplicity != states[b].multiplicity:
            _require(model.soc is not None, path, "multiplicity-changing connection requires SOC")

    initial = p.initial_state
    _require(initial.electronic_state in states, "problem.initial_state.electronic_state",
             "must occur in the declared model basis")
    _require(initial.J >= 0, "problem.initial_state.J", "must be nonnegative")
    _require((initial.rovibrational is None) != (initial.wavefunction is None),
             "problem.initial_state", "supply exactly one rovibrational state or wavefunction")
    if initial.rovibrational is not None:
        rv = initial.rovibrational
        _require(bool(rv.vibration) and all(v >= 0 for v in rv.vibration),
                 "problem.initial_state.rovibrational.vibration", "nonnegative quantum numbers required")
        _require(rv.rotation >= 0, "problem.initial_state.rovibrational.rotation", "must be nonnegative")
    if initial.wavefunction is not None:
        provider(initial.wavefunction, chart, "problem.initial_state.wavefunction", (("chart-amplitude",),))

    preparation = p.preparation
    if isinstance(preparation, RadiationPreparation):
        _require(preparation.photon_energy is not None or preparation.envelope is not None,
                 "problem.preparation", "photon energy or envelope required")
        if preparation.photon_energy is not None:
            _require(preparation.photon_energy > 0, "problem.preparation.photon_energy", "must be positive")
        if preparation.envelope is not None:
            reference(preparation.envelope, "problem.preparation.envelope")
        _require(preparation.duration > 0, "problem.preparation.duration", "must be positive")
        _require(math.isclose(math.hypot(*preparation.polarization), 1.0, rel_tol=1e-9, abs_tol=1e-12),
                 "problem.preparation.polarization", "expected a real unit vector (linear polarization)")
        provider(preparation.transition_dipole, chart, "problem.preparation.transition_dipole",
                 (("e*bohr",), ("debye",)))
    else:
        _require(preparation.energy_unit == model.energy_unit, "problem.preparation.energy_unit",
                 "must match model energy unit; no implicit conversion")
        _require(preparation.energy_zero == model.energy_zero, "problem.preparation.energy_zero",
                 "must match model energy zero")

    _require(bool(p.product_channels), "problem.product_channels", "at least one channel required")
    channel_ids: set[str] = set()
    charts = {chart.chart_id: chart}
    for i, channel in enumerate(p.product_channels):
        path = f"problem.product_channels[{i}]"
        _require(channel.channel_id not in channel_ids, path + ".channel_id", "duplicate channel ID")
        channel_ids.add(channel.channel_id)
        target = channel.chart
        _chart(target, molecule, path + ".chart")
        _require(target.arrangement == "C+O2", path + ".chart.arrangement", "C+O2 projector required")
        _require(target.chart_id not in charts or charts[target.chart_id] == target,
                 path + ".chart.chart_id", "chart ID reused with different definitions")
        charts[target.chart_id] = target
        if target != chart:
            _require(channel.transform is not None, path + ".transform", "explicit coordinate transform required")
        if channel.transform is not None:
            transform = channel.transform
            reference(transform.reference, path + ".transform.reference")
            _require(transform.source_chart_id == chart.chart_id and transform.target_chart_id == target.chart_id,
                     path + ".transform", "transform source/target chart mismatch")
            _covers(transform.source_domain, chart.domain, path + ".transform.source_domain")
            _covers(transform.target_domain, target.domain, path + ".transform.target_domain")
        provider(channel.provider, target, path + ".provider", (("dimensionless",),))
        _require(channel.v >= 0 and channel.j >= 0, path, "O2 (v, j) must be nonnegative integers")
        _require(target.domain[0].lower <= channel.flux_R <= target.domain[0].upper,
                 path + ".flux_R", "surface lies outside projector chart domain")
        correlations = channel.correlated_states
        _require(bool(correlations) and len(set(correlations)) == len(correlations)
                 and set(correlations) <= states.keys(), path + ".correlated_states",
                 "unique, known asymptotically correlated states required")
        # A monitored channel may have exactly zero yield. Only explicitly
        # required spin connections demand SOC; projectors do not assert
        # nonzero dynamical reachability from the initial state.
        _require((channel.total_spin is None) == (channel.spin_evidence is None),
                 path + ".spin_evidence", "total spin and its evidence must be supplied together")
        if channel.total_spin is not None:
            _require(channel.total_spin in (0, 1, 2), path + ".total_spin",
                     "two triplet fragments allow total S = 0, 1, 2")
            _require(all(states[label].multiplicity == 2 * channel.total_spin + 1 for label in correlations),
                     path + ".correlated_states", "declared spin sector disagrees with correlated basis states")
            evidence = channel.spin_evidence
            source = evidence.source.lower()
            _require(not (evidence.status == "measured" and
                          ("10.1126/science.1257156" in source or
                           "lu2014" in source or "lu et al" in source)),
                     path + ".spin_evidence", "Lu et al. did not measure total fragment-pair spin")
