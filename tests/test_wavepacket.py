import json
import unittest
from dataclasses import FrozenInstanceError, replace

from co2_path import (
    Bounds, Evidence, JacobiTransform, MicrocanonicalPreparation,
    WavepacketProblem, validate_wavepacket_problem,
)
from examples.wavepacket_contract import synthetic_problem, synthetic_reference


class WavepacketContractTests(unittest.TestCase):
    def setUp(self):
        self.problem = synthetic_problem()

    def invalid(self, problem, path):
        with self.assertRaises(ValueError) as context:
            validate_wavepacket_problem(problem)
        self.assertIn(path, str(context.exception))
        # Serializers must not provide a route around validation.
        with self.assertRaises(ValueError):
            problem.to_json()

    def model(self, **changes):
        return replace(self.problem, electronic_model=replace(self.problem.electronic_model, **changes))

    def initial(self, **changes):
        return replace(self.problem, initial_state=replace(self.problem.initial_state, **changes))

    def radiation(self, **changes):
        return replace(self.problem, preparation=replace(self.problem.preparation, **changes))

    def channel(self, **changes):
        return replace(self.problem, product_channels=(replace(self.problem.product_channels[0], **changes),))

    def test_synthetic_two_state_contract(self):
        self.assertIsNone(validate_wavepacket_problem(self.problem))

    def test_json_round_trip_is_canonical_and_immutable(self):
        text = self.problem.to_json()
        restored = WavepacketProblem.from_json(text)
        self.assertEqual(restored, self.problem)
        self.assertEqual(restored.to_json(), text)
        self.assertIsInstance(restored.product_channels, tuple)
        self.assertIsInstance(restored.coordinate_chart.domain, tuple)
        with self.assertRaises(FrozenInstanceError):
            restored.initial_state.J = 1
        with self.assertRaises(FrozenInstanceError):
            restored.coordinate_chart.domain[0].lower = 2
        # Object-key order is irrelevant, but electronic-state order is not.
        self.assertEqual(WavepacketProblem.from_json(json.dumps(json.loads(text))).to_json(), text)

    def test_json_normalizes_integer_float_and_negative_zero(self):
        p = self.radiation(duration=10, time_origin=-0.0)
        self.assertEqual(p.to_json(), self.problem.to_json())

    def test_consistent_electronic_state_reordering_is_preserved(self):
        p = self.problem
        order = ("S1", "S0")
        p = replace(
            p,
            electronic_model=replace(p.electronic_model, states=p.electronic_model.states[::-1],
                                     potential=replace(p.electronic_model.potential, state_order=order)),
            preparation=replace(p.preparation, transition_dipole=replace(p.preparation.transition_dipole,
                                                                         state_order=order)),
            product_channels=(replace(p.product_channels[0],
                                      provider=replace(p.product_channels[0].provider, state_order=order)),),
        )
        restored = WavepacketProblem.from_json(p.to_json())
        self.assertEqual(tuple(state.label for state in restored.electronic_model.states), order)
        self.assertEqual(restored, p)

    def test_degree_angstrom_chart_and_ev_model(self):
        p = self.problem
        chart = replace(p.coordinate_chart, length_unit="angstrom", angle_unit="degree",
                        domain=p.coordinate_chart.domain[:2] + (Bounds(0, 180),))
        potential = replace(p.electronic_model.potential, domain=chart.domain, units=("eV",))
        tdm = replace(p.preparation.transition_dipole, domain=chart.domain, units=("debye",))
        channel = replace(p.product_channels[0], chart=chart,
                          provider=replace(p.product_channels[0].provider, domain=chart.domain))
        p = replace(p, coordinate_chart=chart,
                    electronic_model=replace(p.electronic_model, energy_unit="eV", potential=potential),
                    preparation=replace(p.preparation, energy_unit="eV", transition_dipole=tdm),
                    product_channels=(channel,))
        self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)

    def test_flux_surface_endpoints_and_provider_superset_domain(self):
        for flux in (0.5, 20.0):
            validate_wavepacket_problem(self.channel(flux_R=flux))
        prop = self.problem.electronic_model.potential
        p = self.model(potential=replace(prop, domain=(Bounds(0.1, 30),) + prop.domain[1:]))
        validate_wavepacket_problem(p)

    def test_invalid_top_level_type_is_value_error(self):
        for value in (None, {}, (), "problem"):
            with self.assertRaises(ValueError):
                validate_wavepacket_problem(value)

    def test_microcanonical_supports_signed_energy_with_explicit_zero(self):
        prep = MicrocanonicalPreparation(-1.0, "hartree", "synthetic-model-zero")
        p = replace(self.problem, preparation=prep)
        self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)
        for changes in ({"energy_unit": "eV"}, {"energy_zero": "other-zero"}):
            self.invalid(replace(p, preparation=replace(prep, **changes)), "problem.preparation")

    def test_envelope_only_and_envelope_plus_carrier(self):
        envelope = synthetic_reference("envelope")
        for energy in (None, 0.45):
            p = self.radiation(photon_energy=energy, envelope=envelope)
            self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)

    def test_initial_wavefunction_provider(self):
        wavefunction = replace(self.problem.electronic_model.potential,
                               reference=synthetic_reference("packet"), units=("chart-amplitude",))
        p = self.initial(rovibrational=None, wavefunction=wavefunction)
        self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)
        self.invalid(self.initial(wavefunction=wavefunction), "problem.initial_state")
        self.invalid(self.initial(rovibrational=None), "problem.initial_state")

    def test_derivative_coupling_covector_units(self):
        coupling = replace(self.problem.electronic_model.potential,
                           reference=synthetic_reference("nac"),
                           units=("1/bohr", "1/bohr", "1/radian"))
        validate_wavepacket_problem(self.model(derivative_coupling=coupling))
        self.invalid(self.model(derivative_coupling=replace(coupling, units=("1/bohr",))),
                     "derivative_coupling.units")

    def test_wrong_or_missing_molecular_inputs(self):
        for changes in ({"label": ""}, {"atoms": ("O", "O", "O")},
                        {"masses": (12.0, 0.0, 16.0)}, {"masses": (12.0, 16.0)},
                        {"mass_unit": "kg"}):
            with self.subTest(changes=changes):
                self.invalid(replace(self.problem, isotopologue=replace(self.problem.isotopologue, **changes)),
                             "problem.isotopologue")

    def test_invalid_chart_inputs(self):
        chart = self.problem.coordinate_chart
        mutations = (
            {"chart_id": " "}, {"arrangement": "unnamed"},
            {"coordinates": ("r", "R", "theta")}, {"coordinates": ("R", "R", "theta")},
            {"coordinates": ("R", "r")}, {"definitions": ("", "r", "theta")},
            {"angle_unit": ""}, {"length_unit": "meter"},
            {"atom_indices": (0, 0, 1)}, {"atom_indices": (1, 0, 2)},
            {"domain": (Bounds(0, 20),) + chart.domain[1:]},
            {"domain": (Bounds(20, 20),) + chart.domain[1:]},
            {"domain": chart.domain[:2] + (Bounds(0, 4),)},
            {"domain": chart.domain[:2] + (Bounds(-1, 2),)},
        )
        for changes in mutations:
            with self.subTest(changes=changes):
                self.invalid(replace(self.problem, coordinate_chart=replace(chart, **changes)),
                             "problem.coordinate_chart")

    def test_bad_matrix_and_states(self):
        model = self.problem.electronic_model
        for shape in ((2, 3), (3, 3), (0, 0), (-2, -2), (2,), (2.0, 2), (True, 2)):
            with self.subTest(shape=shape):
                self.invalid(self.model(matrix_shape=shape), "matrix_shape")
        self.invalid(self.model(states=()), "states")
        self.invalid(self.model(states=(model.states[0], model.states[0])), "states")
        for multiplicity in (0, -1, 2, True):
            self.invalid(self.model(states=(replace(model.states[0], multiplicity=multiplicity), model.states[1])),
                         "multiplicity")
        for changes in ({"energy_zero": ""}, {"energy_unit": "joule"},
                        {"basis_id": " "}, {"gauge_id": ""}):
            self.invalid(self.model(**changes), "electronic_model")

    def test_all_property_bindings_are_checked(self):
        p = self.problem
        extra = replace(p.electronic_model.potential, reference=synthetic_reference("soc"))
        nac = replace(extra, reference=synthetic_reference("nac"), units=("1/bohr", "1/bohr", "1/radian"))
        packet = replace(extra, reference=synthetic_reference("packet"), units=("chart-amplitude",))
        routes = (
            (p.electronic_model.potential, lambda v: self.model(potential=v)),
            (extra, lambda v: self.model(soc=v)),
            (nac, lambda v: self.model(derivative_coupling=v)),
            (p.preparation.transition_dipole, lambda v: self.radiation(transition_dipole=v)),
            (p.product_channels[0].provider, lambda v: self.channel(provider=v)),
            (packet, lambda v: self.initial(rovibrational=None, wavefunction=v)),
        )
        for prop, assemble in routes:
            for changes in ({"chart_id": "other-chart"}, {"state_order": ("S1", "S0")},
                            {"basis_id": "other-basis"}, {"gauge_id": "other-gauge"},
                            {"representation": "adiabatic"}, {"units": ("invalid",)},
                            {"domain": (Bounds(1, 10),) + prop.domain[1:]}):
                with self.subTest(provider=prop.reference.provider_id, changes=changes):
                    self.invalid(assemble(replace(prop, **changes)), next(iter(changes)))

    def test_provider_reference_must_be_complete_and_unambiguous(self):
        prop = self.problem.electronic_model.potential
        for field in ("provider_id", "source", "version", "sha256"):
            self.invalid(self.model(potential=replace(prop, reference=replace(prop.reference, **{field: ""}))), field)
        self.invalid(self.model(potential=replace(prop, reference=replace(prop.reference, sha256="wrong"))), "sha256")
        tdm = self.problem.preparation.transition_dipole
        conflicting = replace(tdm, reference=replace(prop.reference, version="2"))
        self.invalid(self.radiation(transition_dipole=conflicting), "conflicting provider")
        self.invalid(self.radiation(transition_dipole=replace(tdm, reference=prop.reference)),
                     "conflicting property")

    def test_initial_quantum_numbers_and_parity(self):
        for changes in ({"J": -1}, {"J": True}, {"J": 0.5}, {"parity": "even"},
                        {"electronic_state": "unknown"}):
            self.invalid(self.initial(**changes), "initial_state")
        rv = self.problem.initial_state.rovibrational
        for changes in ({"vibration": ()}, {"vibration": (-1, 0, 0)}, {"rotation": -1}):
            self.invalid(self.initial(rovibrational=replace(rv, **changes)), "rovibrational")

    def test_bad_radiation(self):
        for changes in ({"duration": 0.0}, {"photon_energy": 0.0}, {"photon_energy": None},
                        {"polarization": (0, 0, 0)}, {"polarization": (1, 1, 0)},
                        {"transition_dipole": None}, {"time_unit": "seconds"}):
            self.invalid(self.radiation(**changes), "preparation")

    def test_invalid_product_fields(self):
        for changes in ({"v": -1}, {"j": -1}, {"v": None}, {"j": 1.2},
                        {"carbon_term": "C(1D)"}, {"oxygen_state": "unknown"},
                        {"flux_R": 21}, {"outward": "decreasing_R"},
                        {"correlated_states": ()}, {"correlated_states": ("X",)},
                        {"correlated_states": ("S1", "S1")},
                        {"total_spin": 3}, {"total_spin": 1},
                        {"spin_evidence": None}, {"total_spin": None}):
            with self.subTest(changes=changes):
                self.invalid(self.channel(**changes), "product_channels")
        self.invalid(replace(self.problem, product_channels=()), "product_channels")
        self.invalid(replace(self.problem, product_channels=self.problem.product_channels * 2), "channel_id")

    def test_optional_total_spin_and_multiple_channels(self):
        p = self.channel(total_spin=None, spin_evidence=None)
        second = replace(p.product_channels[0], channel_id="synthetic:v1:j1", v=1)
        p = replace(p, product_channels=p.product_channels + (second,))
        self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)

    def test_lu_spin_claim_is_not_a_measurement(self):
        for source in ("10.1126/science.1257156", "https://doi.org/10.1126/science.1257156", "Lu2014", "Lu et al. (2014)"):
            self.invalid(self.channel(spin_evidence=Evidence("measured", source)), "did not measure")
        self.invalid(self.channel(spin_evidence=Evidence("assumed", "")), "source")
        self.invalid(self.channel(assignment_evidence=Evidence("certain", "synthetic")), "status")

    def test_singlet_coupled_triplet_products_do_not_require_soc(self):
        self.assertEqual(self.problem.product_channels[0].total_spin, 0)
        self.assertIsNone(self.problem.electronic_model.soc)
        validate_wavepacket_problem(self.problem)

    def test_multiplicity_changing_connections_require_soc(self):
        p = self.channel(total_spin=1)
        model = replace(p.electronic_model,
                        states=(p.electronic_model.states[0], replace(p.electronic_model.states[1], multiplicity=3)),
                        required_spin_connections=(("S0", "S1"),))
        p = replace(p, electronic_model=model)
        self.invalid(p, "requires SOC")
        # Omitting an edge cannot hide an initial-to-product spin mismatch.
        self.invalid(replace(p, electronic_model=replace(model, required_spin_connections=())), "requires SOC")
        soc = replace(model.potential, reference=synthetic_reference("soc"))
        p = replace(p, electronic_model=replace(model, soc=soc))
        self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)
        for pair in (("S0", "X"), ("S0", "S0")):
            self.invalid(self.model(required_spin_connections=(pair,)), "required_spin_connections")

    def transformed_problem(self):
        p = self.problem
        source = replace(
            p.coordinate_chart, chart_id="synthetic:O+CO", arrangement="O+CO", atom_indices=(1, 0, 2),
            definitions=("CO center of mass to spectator O distance", "C-to-O distance",
                         "angle between C-to-O and CO-center-of-mass-to-spectator vectors"),
        )
        model = replace(p.electronic_model, potential=replace(p.electronic_model.potential, chart_id=source.chart_id))
        prep = replace(p.preparation, transition_dipole=replace(p.preparation.transition_dipole, chart_id=source.chart_id))
        transform = JacobiTransform(synthetic_reference("transform"), source.chart_id,
                                    p.coordinate_chart.chart_id, source.domain, p.coordinate_chart.domain)
        channel = replace(p.product_channels[0], transform=transform)
        return replace(p, coordinate_chart=source, electronic_model=model, preparation=prep, product_channels=(channel,))

    def test_explicit_arrangement_transform(self):
        p = self.transformed_problem()
        self.assertEqual(WavepacketProblem.from_json(p.to_json()), p)
        channel = p.product_channels[0]
        self.invalid(replace(p, product_channels=(replace(channel, transform=None),)), "transform required")
        for changes in ({"source_chart_id": "wrong"}, {"target_chart_id": "wrong"},
                        {"target_domain": (Bounds(1, 2),) + channel.chart.domain[1:]},
                        {"source_domain": (Bounds(1, 2),) + p.coordinate_chart.domain[1:]}):
            self.invalid(replace(p, product_channels=(replace(channel, transform=replace(channel.transform, **changes)),)),
                         "transform")

    def test_conflicting_chart_id_and_non_product_arrangement(self):
        target = replace(self.problem.coordinate_chart, length_unit="angstrom")
        self.invalid(self.channel(chart=target), "chart ID reused")
        target = replace(target, arrangement="O+CO", atom_indices=(1, 0, 2))
        self.invalid(self.channel(chart=target), "C+O2 projector required")

    def test_nonfinite_and_bool_numeric_values(self):
        for number in (float("nan"), float("inf"), -float("inf"), True, "1", 10**400):
            for p in (self.radiation(duration=number), self.radiation(time_origin=number),
                      self.channel(flux_R=number),
                      replace(self.problem, isotopologue=replace(self.problem.isotopologue, masses=(number, 16, 16))),
                      replace(self.problem, coordinate_chart=replace(self.problem.coordinate_chart,
                              domain=(Bounds(0.5, number),) + self.problem.coordinate_chart.domain[1:]))):
                with self.subTest(number=repr(number)):
                    self.invalid(p, "problem")

    def test_mutable_python_containers_are_rejected(self):
        self.invalid(replace(self.problem, product_channels=list(self.problem.product_channels)), "immutable tuple")
        self.invalid(self.radiation(polarization=[0, 0, 1]), "immutable tuple")
        self.invalid(replace(self.problem, isotopologue={}), "Isotopologue")

    def test_json_rejects_bad_documents(self):
        for document in ("{", "[]", "null", "42", '{"schema_version":"1","schema_version":"1"}'):
            with self.subTest(document=document), self.assertRaises(ValueError):
                WavepacketProblem.from_json(document)
        for value in (None, {}, b"{}"):
            with self.assertRaises(ValueError):
                WavepacketProblem.from_json(value)
        text = self.problem.to_json()
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            WavepacketProblem.from_json(text.replace('"duration":10.0', '"duration":10.0,"duration":20.0'))

    def test_json_rejects_unknown_fields_types_and_versions(self):
        def bad(mutator):
            data = json.loads(self.problem.to_json())
            mutator(data)
            with self.assertRaises(ValueError):
                WavepacketProblem.from_json(json.dumps(data))

        bad(lambda d: d.update(schema_version="2"))
        bad(lambda d: d.pop("schema_version"))
        bad(lambda d: d.update(branching_ratio=0.05))
        bad(lambda d: d["initial_state"].update(J=True))
        bad(lambda d: d["initial_state"].update(J=0.0))
        bad(lambda d: d["preparation"].update(total_energy=1))
        bad(lambda d: d["preparation"].update(kind="microcanonical"))
        bad(lambda d: d["preparation"].pop("kind"))
        bad(lambda d: d["preparation"].pop("transition_dipole"))
        bad(lambda d: d["preparation"].update(duration="10"))
        bad(lambda d: d["electronic_model"]["potential"].update(units=["joule"]))
        bad(lambda d: d["product_channels"][0].pop("v"))
        bad(lambda d: d["product_channels"][0].pop("correlated_states"))

    def test_json_rejects_nonfinite_extensions_and_overflow(self):
        text = self.problem.to_json()
        for token in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                WavepacketProblem.from_json(text.replace('"duration":10.0', '"duration":' + token))


if __name__ == "__main__":
    unittest.main()
