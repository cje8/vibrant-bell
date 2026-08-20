"""Separated claims for the isolated-molecule C + O2 channel."""

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
class ChannelEvidence:
    """Facts, PES landmarks, and conjectures kept on separate fields.

    This is not a fitted potential-energy surface and not a unique trajectory.
    """

    product_channel: str
    literature_threshold_ev: float
    observed_vuv_short_nm: float
    observed_vuv_long_nm: float
    observed_photon_energy_high_ev: float
    observed_photon_energy_low_ev: float
    observed_yield_percent: float
    observed_yield_uncertainty_percent: float
    linear_ooc_minimum_ev_above_oco: float
    oco_ooc_barrier_ev_above_ooc: float
    ooc_electronic_state: str
    ooc_nuclear_arrangement: str
    unique_min_action_path_in_full_state_space: bool
    sequential_nuclear_tube_observed: bool
    sequential_nuclear_tube_status: str
    conjectured_nuclear_sequence: tuple[str, ...]
    well_posed_questions: tuple[str, ...]
    scope: str
    references: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def neutral_atomic_carbon_channel() -> ChannelEvidence:
    """Return the isolated-molecule C + O2 record with claims separated."""

    vuv_range_nm = (101.5, 107.2)
    return ChannelEvidence(
        product_channel="[C(3P) x O2(X 3Sigma_g-)] total S=0",
        literature_threshold_ev=11.44,
        observed_vuv_short_nm=vuv_range_nm[0],
        observed_vuv_long_nm=vuv_range_nm[1],
        observed_photon_energy_high_ev=photon_energy_ev(vuv_range_nm[0]),
        observed_photon_energy_low_ev=photon_energy_ev(vuv_range_nm[1]),
        observed_yield_percent=5.0,
        observed_yield_uncertainty_percent=2.0,
        # Ground 1A' O+CO arrangement (San Vicente Veliz / Koner 2021).
        linear_ooc_minimum_ev_above_oco=7.37,
        oco_ooc_barrier_ev_above_ooc=0.369,
        ooc_electronic_state="1A'",
        ooc_nuclear_arrangement="linear OOC on the O+CO Jacobi arrangement",
        unique_min_action_path_in_full_state_space=False,
        sequential_nuclear_tube_observed=False,
        sequential_nuclear_tube_status=(
            "conjecture concatenating ground-state nuclear isomers with a "
            "VUV photodissociation product channel"
        ),
        conjectured_nuclear_sequence=(
            "linear O-C-O (X 1Sigma_g+)",
            "strongly bent OCO",
            "cyclic c-CO2 (1A1)",
            "collinear C-O-O (1Sigma+)",
            "separated C + O2",
        ),
        well_posed_questions=(
            "projective-Hilbert-space geodesic between specified rays",
            "MEP/IRC on one specified Born-Oppenheimer surface",
            "stationary path of a specified action at specified energy or temperature",
            "channel-resolved photodissociation flux for a specified pulse and initial state",
        ),
        scope="isolated neutral gas-phase molecule; atomic carbon product",
        references=(
            "10.1126/science.1257156",
            "10.1063/1.4808369",
            "10.1039/d1cp01101d",
            "10.1103/PhysRevLett.65.1697",
        ),
    )
