"""Versioned evidence record for the neutral atomic-carbon channel."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MechanismEvidence:
    """Literature constraints, not a fitted potential-energy surface."""

    steps: tuple[str, ...]
    product_channel: str
    thermochemical_threshold_ev: float
    observed_vuv_range_nm: tuple[float, float]
    observed_yield_percent: float
    observed_yield_uncertainty_percent: float
    linear_ooc_minimum_ev_above_oco: float
    oco_ooc_barrier_ev_above_ooc: float
    exact_unique_path_known: bool
    scope: str
    references: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def neutral_atomic_carbon_channel() -> MechanismEvidence:
    """Return a concise record of the supported neutral gas-phase topology."""

    return MechanismEvidence(
        steps=(
            "linear O-C-O (X 1Sigma_g+)",
            "strongly bent OCO",
            "cyclic c-CO2 (1A1)",
            "collinear C-O-O (1Sigma+)",
            "separated C + O2",
        ),
        product_channel="[C(3P) x O2(X 3Sigma_g-)] total S=0",
        thermochemical_threshold_ev=11.44,
        observed_vuv_range_nm=(101.5, 107.2),
        observed_yield_percent=5.0,
        observed_yield_uncertainty_percent=2.0,
        # OOC is 7.37 eV above OCO; the connecting saddle is 0.369 eV above OOC.
        linear_ooc_minimum_ev_above_oco=7.37,
        oco_ooc_barrier_ev_above_ooc=0.369,
        exact_unique_path_known=False,
        scope="isolated neutral gas-phase molecule; atomic carbon product",
        references=(
            "10.1126/science.1257156",
            "10.1063/1.4808369",
            "10.1039/d1cp01101d",
            "10.1103/PhysRevLett.65.1697",
        ),
    )
