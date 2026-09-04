# Wavepacket contract, schema version 1

This is a dependency-free declaration format, not a wavepacket solver.
The [complete synthetic example](../examples/wavepacket_contract.py) constructs
a two-singlet problem and prints deterministic JSON. Its provider hashes refer
only to synthetic metadata strings; it contains no CO₂ electronic-structure data.

## API and failure behavior

All records are frozen dataclasses exported from `co2_path`. Construct nested
sequences as tuples. Dataclass constructors allow incomplete inputs so callers
can assemble specifications, but `validate_wavepacket_problem(problem)` checks
the complete object graph and raises `ValueError` with a field path, such as
`problem.electronic_model.potential.gauge_id`. `to_json()` also validates before
serializing. Successful validation returns `None`.

`WavepacketProblem.from_json(text)` reconstructs immutable nested records and
performs the same validation. It requires explicit `schema_version: "1"` and
preparation `kind`. Unknown fields, missing required fields, duplicate object
keys, wrong types, NaN, infinities, and unsupported versions are errors. JSON
booleans are not accepted as numbers; quantum numbers require actual integers.
Provider references never trigger filesystem access, network calls, or imports.

Serialization sorts object keys and uses compact UTF-8-compatible JSON without
NaN/Infinity extensions. Integral real-valued fields are emitted as floats;
negative zero becomes `0.0`. Tuple/array order is preserved, especially the
electronic-state order: it is physically significant, not a sorting target.
This is deterministic serialization for this schema, not a claim to implement
an external canonical-JSON standard. Optional fields have explicit null/default
representations on output. No calculated observable belongs to the schema.

## Molecule and coordinate chart

`Isotopologue` declares a nonempty label, an ordered `(C, O, O)` composition (any
permutation), positive finite masses, and mass unit `u`. The label does not cause
an isotope-database lookup; the caller owns isotope/mass accuracy.

`JacobiChart.atom_indices` is `(spectator, diatom atom 1, diatom atom 2)` in the
molecule's atom order. For `C+O2`, carbon must be the spectator; for `O+CO`, oxygen
must be the spectator. Definitions must explain the vectors as well as the
scalar distances and angle. The axis order is exactly `(R, r, theta)`. Both
length axes use `length_unit`, and theta uses `angle_unit`.

All domains are triples of closed `Bounds(lower, upper)`. Finite, nonempty
bounds, strictly positive radial lower bounds, and theta in `[0, pi]` radians
or `[0, 180]` degrees are required. Version 1 deliberately describes a **finite
computational domain**, not the infinite scattering domain or a grid. Reusing
a chart ID with different definitions, atom order, units, or bounds is rejected.

## Electronic basis and property providers

The ordered states include every referenced initial and asymptotically
correlated state. Each state supplies a unique label, symmetry, and positive odd
spin multiplicity (neutral CO₂, with electronic spin distinguished from nuclear
spin). `matrix_shape` must equal `(number_of_states, number_of_states)`.
`basis_id`, `gauge_id`, energy unit, and energy-zero label are mandatory.

Each `PropertyProvider` declares its chart ID, state order, diabatic
representation, basis ID, gauge ID, units, and domain coverage. A
`ProviderReference` carries a provider ID, source, version, and lowercase
64-hex-character SHA-256 checksum. Reusing a provider ID with conflicting
provenance or bindings is rejected. These are consistency checks on metadata,
not checksum verification or proof that any provider exists.

| Property | Permitted units in its `units` tuple |
| --- | --- |
| Potential and SOC | `(model.energy_unit,)`: `hartree` or `eV` |
| Transition dipole | `("e*bohr",)` or `("debye",)` |
| Derivative coupling | `(1/length_unit, 1/length_unit, 1/angle_unit)` |
| Initial wavefunction | `("chart-amplitude",)` |
| Product projector | `("dimensionless",)` |

Derivative couplings are declared as coordinate covector components in axis
order, e.g. `("1/bohr", "1/bohr", "1/radian")`; their numerical incorporation
into a kinetic operator is deferred. `chart-amplitude` names a chart-specific
wavefunction representation, not a verified normalization convention or
integration measure. All properties use the full ordered model basis.

Units are checked, not converted. Property domains must cover their chart
domain. This means a caller **declares** coverage; the validator does not prove
the PES is global or evaluate a point outside/inside its numerical support.

`required_spin_connections` explicitly names state pairs. If a required edge
changes multiplicity, SOC is mandatory. Monitored product channels do not
require nonzero reachability: a different-spin projector is valid without SOC
and may have exactly zero yield. A supplied SOC descriptor does not prove the
coupling is nonzero or dynamically relevant. Two triplet fragments can be assigned a singlet
total-spin sector: their fragment multiplicities alone do not require SOC.

## Initial state and preparation

`InitialRovibronicState` specifies an electronic state in the model basis,
nonnegative integer rovibronic `J` (excluding nuclear spin), and parity `+` or
`-`. Supply exactly one of:

- `RovibrationalState`: a nonempty tuple of nonnegative vibrational quantum
  numbers and a nonnegative rotational quantum number, with mode order defined
  by the caller's model; or
- an initial-wavefunction `PropertyProvider` in the same chart, basis and gauge.

The schema does not certify eigenstates, isotope-dependent selection rules,
nuclear-exchange symmetry, state normalization, or completeness of quantum
labels. Those need a numerical/symmetry-aware model.

Preparation is a tagged union:

- `RadiationPreparation(kind="radiation")`: a positive photon-energy center,
  an envelope reference, or both; a real unit polarization vector (linear
  polarization only); finite time origin; positive duration; `fs` or
  `atomic_time`; and a compatible transition-dipole descriptor. Photon energy
  is an energy difference and does not use the molecular energy-zero label.
- `MicrocanonicalPreparation(kind="microcanonical")`: finite total energy,
  unit and energy zero matching the model exactly. Negative energies are valid
  relative to an explicitly specified zero.

Pulse and microcanonical fields cannot be mixed. Version 1 does not evaluate
pulse envelopes, infer their carrier frequencies, or check support/timing.

## Asymptotic projectors

At least one uniquely named `ProductProjectorContract` is required. Version 1
targets `C(3P) + O2(X 3Sigma_g-)` in a `C+O2` chart. Each channel declares O₂
integer `(v, j)`, a compatible dimensionless projector descriptor, a flux
surface at `flux_R` inside that chart, and outward `increasing_R` orientation.

`correlated_states` explicitly maps this channel to one or more unique model
state labels. It is **not** a numerical asymptotic transformation matrix. An
optional total-spin sector is restricted to 0, 1, or 2 and must agree with the
correlated states' multiplicities. State labels alone never determine this
correlation; the caller must supply it.

If source and product charts differ, a `JacobiTransform` is mandatory, even
when only units, atom order, or definitions differ. Its reference, source/target
IDs and declared coverage of both domains are checked. Numerical transforms,
their Jacobians, and whether the flux surface truly maps into PES support are
not evaluated. The transform is for coordinates; electronic bases/gauges must
still match exactly.

Channel assignment and optional total-spin evidence distinguish `measured`,
`inferred`, and `assumed` claims, each with a nonempty source. Both total spin
and its evidence must be supplied together or omitted together. A known claim
that [Lu et al.](https://doi.org/10.1126/science.1257156) measured total
fragment-pair spin is rejected. Arbitrary references and claims are not
fact-checked by string validation; a source label is not proof of measurement.

## Boundary and next layer

Passing means **internally consistent metadata only**, not an
accurate physical model or an executable simulation. A future numerical
adapter/probe layer must load the identified artifacts and validate actual
matrix shapes, units, finite values, Hermiticity (with explicit tolerances),
normalization, projectors, transformations and sample-point coverage. Even
sample-point probes do not prove global smoothness or gauge continuity.

This work does not create a real PES, extend the 120–160 nm five-state valence
model to the 101.5–107.2 nm experiment, build a grid/kinetic operator, propagate a
packet, implement CAPs, integrate flux, or compute an S-matrix or branching
ratio. The existing experiment and conjecture ledgers remain separate.

### Known version-1 modeling limits

Version 1 is an inventory of declarations, not a complete physical input
contract. In particular:

- Radiation metadata does not specify a unique electric field: field amplitude,
  envelope normalization and duration convention are absent. Nor does it
  distinguish finite-field propagation from a linear-response source packet.
  A ground-state source outside the propagated electronic basis is unsupported.
- Electronic gauge IDs do not specify the spatial frame or Cartesian/spherical
  component convention of the transition dipole and polarization.
- State count is the declared matrix dimension. The schema does not distinguish
  full spin-component bases from symmetry-reduced/effective models, so SOC
  metadata alone is not enough to construct a physical spin Hamiltonian.
- Product `j` does not distinguish spin-free rotation from fine-structure total
  angular momentum. Carbon `J_C`, O2 `N` versus `J`, and isotope-dependent
  exchange restrictions require additional conventions. `C(3P)` must not be
  read as the resolved `C(3P2)` observable of the Lu experiment.
- A microcanonical energy does not uniquely specify a pure packet or ensemble;
  an adapter must supply the preparation and normalization convention.

These omissions require a future physical-model schema before propagation;
passing the current validator does not resolve them.
