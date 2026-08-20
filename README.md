# CO₂ → C + O₂: what is actually well-posed

This repository records one negative result and the facts that survive after
the usual reaction-path language is stripped off.

> For a specified molecular Hamiltonian and initial state, Schrödinger
> evolution already *is* the path.  There is no extra variational problem
> whose solution is “the” CO₂ trajectory in the full quantum-state space.

Everything else answers a different question.  Mixing those questions is how
a unique “minimum-action path” appears to exist when it does not.

## First-principles inventory

The isolated three-atom problem is a Hamiltonian on a Hilbert space, not a
curve drawn on a picture of nuclei.

1. **Specified Hamiltonian and initial ray.**
   `|\Psi(t)\rangle = exp(-i Ĥ t / ℏ) |\Psi(0)\rangle`.
   This is unique.  It is not found by minimizing an action over competing
   nuclear cartoons.
2. **Projective geometry of two rays.**
   `distance = acos(|⟨initial|final⟩|)`.
   This is a Fubini–Study geodesic.  It ignores Ĥ.
3. **One Born–Oppenheimer surface.**
   A mass-weighted steepest-descent curve (MEP/IRC) is defined only after a
   single electronic state and a nuclear coordinate chart are chosen.  It
   cannot represent nonadiabatic branching.
4. **A specified action at a specified energy or temperature.**
   An instanton is a stationary path of that action.  It is not the MEP, and
   it is not Schrödinger evolution.  The Euclidean evaluator in this package
   returns nuclear `S = ∫ dτ [½ m (dq/dτ)² + V(q)]` for a caller-supplied
   `V`.  It does not return `S/ℏ`, and it does not invent `V`.
5. **A specified pulse and asymptotic projectors.**
   Photodissociation yields a channel-resolved flux or S-matrix.  A “dominant
   tube” can be read off afterwards from the probability current.  It is an
   output, not an input.

The package implements (2) and an evaluator for a user-supplied discretization
of (4).  It cannot compute a photodissociation branching ratio, an instanton
without `V`, or a Schrödinger orbit from a nuclear cartoon.

## What is known, kept on separate ledgers

**Directly detected (Lu et al., 2014).**  Neutral CO₂ irradiated between
101.5 and 107.2 nm yields `C(³P)`, observed by velocity-map imaging, with a
reported channel yield of **5 ± 2%**.  Those wavelengths are **12.22 eV** and
**11.57 eV**.  The experiment measures a carbon-atom product, not a sequence
of nuclear isomers.

**Inferred, not imaged.**  Co-product `O₂(X ³Σg⁻)` is assigned from carbon
kinematics and energy conservation.  Molecular oxygen was not the imaged
species.

**Not measured.**  Total spin of the fragment pair was not reported.  Two
triplets *can* couple to `S = 0`; that compatibility is not a measurement.

**Not derived here.**  The literature threshold quoted for
`CO₂ → C(³P) + O₂(X ³Σg⁻)` is **11.44 eV**.  This repository does not
recompute that thermochemistry.

**Ground-state PES landmarks (San Vicente Veliz / Koner et al., 2021).**  On
the ground `¹A′` surface, a linear OOC minimum lies about **7.37 eV** above
linear OCO.  The OCO/OOC saddle is about **0.369 eV** above that OOC minimum.
Those points live on the **O + CO** Jacobi arrangement of the ground surface.
They are not a measured VUV photodissociation path to `C + O₂`.

**Scope.**  `C` means an isolated carbon atom.  Graphite or any other solid
carbon phase is outside the three-atom Hilbert space.

**Conjecture, not a fact.**  The nuclear sequence

```text
linear O–C–O (X ¹Σg⁺)
  → strongly bent OCO
  → cyclic c-CO₂ (¹A₁)
  → collinear C–O–O (¹Σ⁺)
  → [C(³P) ⊗ O₂(X ³Σg⁻)]S=0
```

concatenates ground-state isomers with a VUV product *assignment*.  It is a
candidate tube one might later test with a global diabatic wavepacket.  It is
not an observed trajectory, and it is not uniquely selected by a
representation-independent action principle.

## Reproduce the checks

The package has no runtime dependencies beyond Python 3.10+.

```bash
python -m pip install --no-deps .
python -m unittest discover -s tests -v
python -m co2_path
```

The CLI prints the separated evidence record.  The fields
`sequential_nuclear_tube_observed`, `coproduct_directly_detected`,
`total_spin_measured`, and `literature_threshold_derived_here` are `false`.

## What a defensible calculation still has to specify

- isotopologue, initial rovibronic state, total angular momentum and parity;
- photon energy and pulse, or a microcanonical energy / temperature;
- a global diabatic electronic-state matrix over Jacobi coordinates
  `(R, r, theta)`;
- derivative couplings and, where relevant, spin–orbit couplings;
- asymptotic product projectors resolving O₂ vibration and rotation.

The well-posed result is then a channel-resolved scattering matrix or product
flux.  A “dominant path” may be extracted afterward as a ridge of the
conditional quantum probability current.

## Primary references

Each DOI is stored with the statement it can actually support.

- Z. Lu et al., *Science* **346**, 61–64 (2014),
  [doi:10.1126/science.1257156](https://doi.org/10.1126/science.1257156).
  VMI of `C(³P)` from CO₂ at 101.5–107.2 nm; `O₂` inferred from kinematics.
- S. Y. Grebenshchikov, *J. Chem. Phys.* **138**, 224106 (2013),
  [doi:10.1063/1.4808369](https://doi.org/10.1063/1.4808369).
  Singlet valence PESs and a 5×5 diabatic matrix for UV absorption, not a
  `C + O₂` flux.
- J. C. San Vicente Veliz et al., *Phys. Chem. Chem. Phys.* **23**, 11251–11263
  (2021), [doi:10.1039/d1cp01101d](https://doi.org/10.1039/d1cp01101d).
  Ground `¹A′` OOC minimum and OCO/OOC saddle on the O + CO arrangement.
- J. Anandan and Y. Aharonov, *Phys. Rev. Lett.* **65**, 1697–1700
  (1990), [doi:10.1103/PhysRevLett.65.1697](https://doi.org/10.1103/PhysRevLett.65.1697).
  Geometry of quantum evolution; a geodesic between rays is not the
  Hamiltonian orbit.
