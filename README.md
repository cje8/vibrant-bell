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

1. **Specified Hamiltonian, pulse, and initial ray.**
   Field-free evolution `|\Psi(t)\rangle = exp(-i Ĥ t / ℏ) |\Psi(0)\rangle`
   is unique for that Ĥ, but photodissociation is not field-free.  A VUV
   pulse is an additional interaction.  Neither object is found by
   minimizing an action over competing nuclear cartoons.
2. **Projective geometry of two rays.**
   `distance = acos(|⟨initial|final⟩|)`.
   This is a Fubini–Study geodesic.  It ignores Ĥ.  The Anandan–Aharonov
   length of a Hamiltonian orbit is `(2/ℏ) ∫ ΔE(t) dt` along that orbit.
   Two endpoint rays do not determine it, and a uniform time step does not
   specify the orbit.  The geodesic is only a lower bound.
3. **One Born–Oppenheimer surface.**
   A mass-weighted steepest-descent curve (MEP/IRC) is defined only after a
   single electronic state and a nuclear coordinate chart are chosen.  It
   cannot represent nonadiabatic branching.
4. **A specified action at a specified energy or temperature.**
   An instanton is a stationary path of that action.  It is not the MEP, and
   it is not Schrödinger evolution.  The Euclidean evaluator in this package
   returns nuclear `S = ∫ dτ [½ m(q) (dq/dτ)² + (V(q) − V₀)]` for a
   caller-supplied `V`, energy origin `V₀`, a mass vector at each image, and
   one imaginary-time width per interval, and a named nuclear coordinate
   chart.  A uniform `Δτ` is not a thermal instanton: this evaluator does
   not impose `q(0)=q(βℏ)`.  Jacobi angles are not Cartesian, so mass
   vectors are not interchangeable across unnamed charts.  Without `V₀`, a
   constant shift of `V` would change `S` by `V₀ × τ`.  The evaluator does
   not return `S/ℏ`, and it does not invent `V`.
5. **A specified pulse and asymptotic projectors.**
   Photodissociation yields a channel-resolved flux or S-matrix.  A “dominant
   tube” can be read off afterwards from the probability current.  It is an
   output, not an input.

The package implements (2), an evaluator for a user-supplied discretization
of (4), and the Anandan–Aharonov length of a supplied `ΔE(t)` series.  Two
endpoint rays do not determine that length.  The package cannot compute a
photodissociation branching ratio, an instanton without `V`, or a
Schrödinger orbit from a nuclear cartoon.

## What is known, kept on separate ledgers

**Directly detected (Lu et al., 2014).**  Neutral CO₂ irradiated between
101.5 and 107.2 nm yields `C(³P)`, observed by velocity-map imaging, with a
*reported* channel yield of **5 ± 2%**.  That is not a complete branching
ratio over all CO₂ photodissociation channels.  This repository does not
reanalyze that yield.  Those wavelengths are **12.22 eV** and **11.57 eV**.
The experiment measures a carbon-atom product, not a sequence of nuclear
isomers.

**Inferred, not imaged.**  Co-product `O₂(X ³Σg⁻)` is assigned from carbon
kinematics and energy conservation.  Molecular oxygen was not the imaged
species.

**Not measured.**  Total spin of the fragment pair was not reported.  Two
triplets *can* couple to `S = 0` by Clebsch–Gordan algebra; that
compatibility is not a measurement.

**Not derived here.**  The literature threshold quoted for
`CO₂ → C(³P) + O₂(X ³Σg⁻)` is **11.44 eV**.  This repository does not
recompute that thermochemistry, and it does not subtract `hc/λ` from
11.44 eV.  Those numbers do not share a derived energy zero here.

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

concatenates frames from different ledgers.  Linear OCO and collinear COO
are ground-state PES landmarks; cyclic CO₂ is conjecture; `C + O₂` is an
inferred photodissociation assignment.  None of those frames is an observed
trajectory, and the concatenation is not uniquely selected by a
representation-independent action principle.

## Reproduce the checks

The package has no runtime dependencies beyond Python 3.10+.

```bash
python -m pip install --no-deps .
python -m unittest discover -s tests -v
python -m co2_path
```

The CLI prints nested ledgers: experiment, thermochemistry, ground-state PES,
nuclear-tube conjecture, and problem contract.  They are separate objects so
a VUV carbon-atom detection cannot be read as a ground-state nuclear path.

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
  Singlet valence PESs and a 5×5 diabatic matrix for UV absorption.  That
  paper is not the 101.5–107.2 nm window and is not a `C + O₂` flux.
- J. C. San Vicente Veliz et al., *Phys. Chem. Chem. Phys.* **23**, 11251–11263
  (2021), [doi:10.1039/d1cp01101d](https://doi.org/10.1039/d1cp01101d).
  Ground `¹A′` OOC minimum and OCO/OOC saddle on the O + CO arrangement.
- J. Anandan and Y. Aharonov, *Phys. Rev. Lett.* **65**, 1697–1700
  (1990), [doi:10.1103/PhysRevLett.65.1697](https://doi.org/10.1103/PhysRevLett.65.1697).
  The Anandan–Aharonov length of a Hamiltonian orbit is the time integral
  of energy uncertainty.  That is not the Fubini–Study geodesic between
  two endpoint rays.
