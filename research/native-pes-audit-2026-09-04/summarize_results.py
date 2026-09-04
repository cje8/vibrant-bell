"""Summarize recorded native results without altering them."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(mode):
    return json.loads((ROOT / f"{mode}.json").read_text())


def compare(left, right):
    a, b = read(left), read(right)
    assert [p["name"] for p in a["cases"]] == [p["name"] for p in b["cases"]]
    energies, gradients = [], []
    for p, q in zip(a["cases"], b["cases"]):
        if p.get("energy_hartree") is not None and q.get("energy_hartree") is not None:
            energies.append({"case": p["name"], "difference": abs(p["energy_hartree"] - q["energy_hartree"])})
        if p["valid_result"] and q["valid_result"]:
            gradients.append({"case": p["name"], "difference": max(
                abs(x - y) for x, y in zip(p["gradient_hartree_per_bohr"], q["gradient_hartree_per_bohr"])
            )})
    return {
        "left": left, "right": right,
        "max_finite_energy_difference_hartree": max(energies, key=lambda p: p["difference"]),
        "max_finite_gradient_component_difference_hartree_per_bohr": max(gradients, key=lambda p: p["difference"]),
    }


def main():
    modes = ["o0_kernel", "o2_kernel", "o0_csv", "o2_csv", "trap_kernel"]
    result = {"comparisons": [compare("o0_kernel", "o0_csv"), compare("o0_kernel", "o2_kernel")], "modes": {}}
    for mode in modes:
        data = read(mode)
        by_name = {x["name"]: x for x in data["cases"]}
        swaps = []
        for name in ("upstream_example", "bent_asymmetric"):
            a, b = by_name[name], by_name[name + "_O_swap"]
            swaps.append({
                "case": name,
                "energy_difference_hartree": abs(a["energy_hartree"] - b["energy_hartree"]),
                "max_permuted_gradient_difference_hartree_per_bohr": max(
                    abs(a["gradient_hartree_per_bohr"][i] - b["gradient_hartree_per_bohr"][j])
                    for i, j in enumerate((0, 2, 1))
                ),
            })
        result["modes"][mode] = {
            "case_count": data["case_count"], "finite_case_count": data["finite_case_count"],
            "failures": [{"case": x["name"], "returncode": x["returncode"], "raw_output": x["stdout"]}
                         for x in data["cases"] if not x["valid_result"]],
            "oxygen_swaps": swaps,
            "gradient_checks": [{"h_bohr": x["h_bohr"], "absolute_errors": [y.get("absolute_error") for y in x["axes"]]}
                                for x in data["interior_gradient_checks"]],
        }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
