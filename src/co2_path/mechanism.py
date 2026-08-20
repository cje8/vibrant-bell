"""Separated ledgers for the isolated-molecule C + O2 channel."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

# Exact from the CODATA 2018 defining constants h, c, and e.
PLANCK_HC_EV_NM = (6.62607015e-34 * 299792458.0 / 1.602176634e-19) * 1e9


def photon_energy_ev(wavelength_nm: float) -> float:
    """Return ``E = hc / λ`` in electronvolts for a vacuum wavelength in nm."""

    if not math.isfinite(wavelength_nm) or wavelength_nm <= 0.0:
        raise ValueError("wavelength must be a positive finite length")
    return PLANCK_HC_EV_NM / wavelength_nm


@dataclass(frozen=True)
class Citation:
    """A DOI attached to the statement it can actually support."""

    doi: str
    warrants: str


@dataclass(frozen=True)
class ExperimentLedger:
    """What Lu et al. imaged, inferred, and did not measure."""

    detected_fragment: str
    inferred_coproduct: str
    coproduct_directly_detected: bool
    total_spin_measured: bool
    total_spin_compatible_with_singlet: bool
    total_spin_compatibility_source: str
    reported_channel_yield_percent: float
    reported_channel_yield_uncertainty_percent: float
    yield_reanalyzed_here: bool
    reported_yield_is_branching_ratio: bool
    reported_yield_denominator: str
    observed_vuv_short_nm: float
    observed_vuv_long_nm: float
    observed_photon_energy_high_ev: float
    observed_photon_energy_low_ev: float
    photon_energy_zero: str
    photon_energy_compared_to_literature_threshold: str


@dataclass(frozen=True)
class ThermochemistryLedger:
    """A literature threshold this repository does not recompute."""

    literature_threshold_ev: float
    derived_here: bool
    energy_zero: str


@dataclass(frozen=True)
class GroundStatePESLedger:
    """Landmarks on the ground 1A' O+CO arrangement, not a VUV path."""

    linear_ooc_minimum_ev_above_oco: float
    oco_ooc_barrier_ev_above_ooc: float
    ooc_electronic_state: str
    ooc_nuclear_arrangement: str
    jacobi_arrangement: str
    is_c_plus_o2_asymptote: bool


@dataclass(frozen=True)
class NuclearTubeStep:
    """One cartoon frame, tagged with the ledger it was taken from."""

    description: str
    source_ledger: str
    observed: bool
    jacobi_arrangement: str


@dataclass(frozen=True)
class NuclearTubeConjecture:
    """A cartoon that concatenates different physical objects."""

    observed: bool
    status: str
    sequence: tuple[NuclearTubeStep, ...]


@dataclass(frozen=True)
class ProblemContract:
    """Which questions are well-posed, and which this package cannot answer."""

    unique_min_action_path_in_full_state_space: bool
    lu_experiment_answers: tuple[str, ...]
    well_posed_but_not_this_experiment: tuple[str, ...]
    ill_posed_questions: tuple[str, ...]
    uncomputable_with_this_package: tuple[str, ...]


@dataclass(frozen=True)
class ChannelEvidence:
    """Facts, inferences, PES landmarks, and conjectures on separate ledgers.

    This is not a fitted potential-energy surface and not a unique trajectory.
    """

    experiment: ExperimentLedger
    thermochemistry: ThermochemistryLedger
    ground_state_pes: GroundStatePESLedger
    nuclear_tube: NuclearTubeConjecture
    problem: ProblemContract
    scope: str
    references: tuple[Citation, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def neutral_atomic_carbon_channel() -> ChannelEvidence:
    """Return the isolated-molecule C + O2 record with claims on separate ledgers."""

    short_nm = 101.5
    long_nm = 107.2
    return ChannelEvidence(
        experiment=ExperimentLedger(
            detected_fragment="C(3P)",
            inferred_coproduct="O2(X 3Sigma_g-)",
            coproduct_directly_detected=False,
            total_spin_measured=False,
            total_spin_compatible_with_singlet=True,
            total_spin_compatibility_source=(
                "Clebsch-Gordan coupling of two triplet fragments; not a measurement"
            ),
            reported_channel_yield_percent=5.0,
            reported_channel_yield_uncertainty_percent=2.0,
            yield_reanalyzed_here=False,
            reported_yield_is_branching_ratio=False,
            reported_yield_denominator=(
                "Lu et al. reported channel yield near threshold; not a "
                "complete branching ratio over all CO2 photodissociation channels"
            ),
            observed_vuv_short_nm=short_nm,
            observed_vuv_long_nm=long_nm,
            observed_photon_energy_high_ev=photon_energy_ev(short_nm),
            observed_photon_energy_low_ev=photon_energy_ev(long_nm),
            photon_energy_zero="vacuum photon energy hc/λ, not a molecular energy zero",
            photon_energy_compared_to_literature_threshold=(
                "not subtracted here: hc/λ and the 11.44 eV literature "
                "threshold do not share a derived energy zero in this package"
            ),
        ),
        thermochemistry=ThermochemistryLedger(
            literature_threshold_ev=11.44,
            derived_here=False,
            energy_zero="not specified in this repository",
        ),
        ground_state_pes=GroundStatePESLedger(
            linear_ooc_minimum_ev_above_oco=7.37,
            oco_ooc_barrier_ev_above_ooc=0.369,
            ooc_electronic_state="1A'",
            ooc_nuclear_arrangement="linear OOC on the O+CO Jacobi arrangement",
            jacobi_arrangement="O+CO",
            is_c_plus_o2_asymptote=False,
        ),
        nuclear_tube=NuclearTubeConjecture(
            observed=False,
            status=(
                "conjecture concatenating ground-state nuclear isomers with a "
                "VUV photodissociation product assignment"
            ),
            sequence=(
                NuclearTubeStep(
                    description="linear O-C-O (X 1Sigma_g+)",
                    source_ledger="ground_state_pes",
                    observed=False,
                    jacobi_arrangement="O+CO",
                ),
                NuclearTubeStep(
                    description="strongly bent OCO",
                    source_ledger="conjecture",
                    observed=False,
                    jacobi_arrangement="unspecified",
                ),
                NuclearTubeStep(
                    description="cyclic c-CO2 (1A1)",
                    source_ledger="conjecture",
                    observed=False,
                    jacobi_arrangement="unspecified",
                ),
                NuclearTubeStep(
                    description="collinear C-O-O (1Sigma+)",
                    source_ledger="ground_state_pes",
                    observed=False,
                    jacobi_arrangement="O+CO",
                ),
                NuclearTubeStep(
                    description="separated C + O2",
                    source_ledger="experiment_inferred_coproduct",
                    observed=False,
                    jacobi_arrangement="C+O2",
                ),
            ),
        ),
        problem=ProblemContract(
            unique_min_action_path_in_full_state_space=False,
            lu_experiment_answers=(
                "VMI of C(3P) from a specified VUV pulse on CO2; O2 is inferred",
            ),
            well_posed_but_not_this_experiment=(
                "projective-Hilbert-space geodesic between specified rays in a named C^n",
                "MEP/IRC on one specified Born-Oppenheimer surface",
                "stationary path of a specified action at specified energy or temperature",
                "channel-resolved photodissociation flux for a specified pulse and initial state",
            ),
            ill_posed_questions=(
                "unique representation-independent minimum-action path in the full state space",
                "the nuclear cartoon followed by every reactive wavepacket",
                "photodissociation as field-free Schrodinger evolution of an isolated molecule",
                "O+CO ground-state OOC as the C+O2 photodissociation asymptote",
                "Fubini-Study geodesic in caller-supplied C^n as a CO2 molecular path",
            ),
            uncomputable_with_this_package=(
                "photodissociation branching ratio",
                "instanton: this evaluator does not impose q(0)=q(beta hbar)",
                "instanton without a supplied potential and energy origin",
                "Euclidean action without a named nuclear coordinate chart",
                "Schrodinger orbit from a nuclear cartoon",
                "Anandan-Aharonov Hamiltonian orbit length from two endpoint rays",
            ),
        ),
        scope="isolated neutral gas-phase molecule; atomic carbon product",
        references=(
            Citation(
                doi="10.1126/science.1257156",
                warrants=(
                    "VMI detection of C(3P) from CO2 at 101.5-107.2 nm with "
                    "a reported 5±2% channel yield; O2 inferred from kinematics, "
                    "not imaged"
                ),
            ),
            Citation(
                doi="10.1063/1.4808369",
                warrants=(
                    "singlet valence PESs and a 5x5 diabatic matrix for UV "
                    "absorption, not the 101.5-107.2 nm window and not a C+O2 flux"
                ),
            ),
            Citation(
                doi="10.1039/d1cp01101d",
                warrants=(
                    "ground 1A' linear OOC minimum 7.37 eV above OCO and "
                    "OCO/OOC saddle 0.369 eV above OOC on the O+CO arrangement"
                ),
            ),
            Citation(
                doi="10.1103/PhysRevLett.65.1697",
                warrants=(
                    "the Anandan-Aharonov length of a Hamiltonian orbit is "
                    "the time integral of energy uncertainty; that is not "
                    "the Fubini-Study geodesic between two endpoint rays"
                ),
            ),
        ),
    )
