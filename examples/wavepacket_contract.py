"""Print a synthetic contract, NOT a CO2 PES or a runnable dynamics model.

The reference hashes identify synthetic metadata strings, not numerical data.
Run after installing the package: python examples/wavepacket_contract.py
"""

import hashlib
import math

from co2_path import (
    Bounds, DiabaticModelContract, ElectronicState, Evidence,
    InitialRovibronicState, Isotopologue, JacobiChart,
    ProductProjectorContract, PropertyProvider, ProviderReference,
    RadiationPreparation, RovibrationalState, WavepacketProblem,
)


def synthetic_reference(name):
    return ProviderReference(
        provider_id=f"synthetic:{name}",
        source="synthetic metadata only; no numerical provider exists",
        version="1",
        sha256=hashlib.sha256(f"synthetic metadata only:{name}".encode()).hexdigest(),
    )


def synthetic_problem():
    chart = JacobiChart(
        chart_id="synthetic:C+O2",
        arrangement="C+O2",
        atom_indices=(0, 1, 2),
        coordinates=("R", "r", "theta"),
        definitions=(
            "distance from O2 center of mass to carbon",
            "distance between the two oxygen atoms",
            "angle between O1-to-O2 and O2-center-of-mass-to-C vectors",
        ),
        length_unit="bohr",
        angle_unit="radian",
        domain=(Bounds(0.5, 20.0), Bounds(0.5, 5.0), Bounds(0.0, math.pi)),
    )

    def provider(name, units):
        return PropertyProvider(
            reference=synthetic_reference(name), chart_id=chart.chart_id,
            state_order=("S0", "S1"), basis_id="synthetic-basis-v1",
            gauge_id="synthetic-gauge-v1", units=units, domain=chart.domain,
        )

    return WavepacketProblem(
        isotopologue=Isotopologue("12C16O2", ("C", "O", "O"), (12.0, 15.9949, 15.9949)),
        coordinate_chart=chart,
        initial_state=InitialRovibronicState(
            electronic_state="S0", J=0, parity="+",
            rovibrational=RovibrationalState(vibration=(0, 0, 0), rotation=0),
        ),
        preparation=RadiationPreparation(
            photon_energy=0.45, energy_unit="hartree", polarization=(0.0, 0.0, 1.0),
            time_origin=0.0, duration=10.0, time_unit="fs",
            transition_dipole=provider("tdm", ("e*bohr",)),
        ),
        electronic_model=DiabaticModelContract(
            states=(ElectronicState("S0", 1, "A'"), ElectronicState("S1", 1, "A'")),
            matrix_shape=(2, 2), basis_id="synthetic-basis-v1", gauge_id="synthetic-gauge-v1",
            energy_unit="hartree", energy_zero="synthetic-model-zero",
            potential=provider("potential", ("hartree",)),
        ),
        product_channels=(ProductProjectorContract(
            channel_id="synthetic:C+O2:v0:j1:S0", chart=chart,
            provider=provider("projector", ("dimensionless",)),
            carbon_term="C(3P)", oxygen_state="X 3Sigma_g-", v=0, j=1,
            flux_R=15.0, outward="increasing_R", correlated_states=("S1",),
            assignment_evidence=Evidence("assumed", "synthetic fixture, not an experimental assignment"),
            total_spin=0, spin_evidence=Evidence("assumed", "synthetic singlet sector"),
        ),),
    )


if __name__ == "__main__":
    print(synthetic_problem().to_json())
