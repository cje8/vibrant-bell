"""Run a compiled, unmodified upstream PES through native_probe.f90.

The executable and its isolated data directory are supplied by the caller.
Each point runs in a fresh process; raw output is retained, including NaNs.
No upstream files are changed by this script. With missing kernels, the
upstream evaluator itself rebuilds them in the supplied data directory.
"""

import argparse
import json
import math
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("executable")
    parser.add_argument("data_directory")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--finite-difference", action="store_true")
    parser.add_argument(
        "--require-finite", action="store_true",
        help="Exit 1 if any main case lacks a finite, successful native result.",
    )
    args = parser.parse_args()

    def probe(name, r):
        input_text = " ".join(format(x, ".17g") for x in r) + "\n"
        record = {"name": name, "r_bohr": list(r), "stdin": input_text}
        try:
            p = subprocess.run(
                [args.executable], input=input_text, text=True,
                cwd=args.data_directory, capture_output=True, timeout=args.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            record.update(timeout=True, stdout=str(exc.stdout), stderr=str(exc.stderr))
            return record
        record.update(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
        lines = [line for line in p.stdout.splitlines() if line.startswith("RESULT ")]
        if len(lines) == 1:
            try:
                values = [float(x.replace("D", "E")) for x in lines[0].split()[1:]]
                if len(values) == 4:
                    record["finite"] = [math.isfinite(x) for x in values]
                    record["energy_hartree"] = values[0] if math.isfinite(values[0]) else None
                    record["gradient_hartree_per_bohr"] = [
                        x if math.isfinite(x) else None for x in values[1:]
                    ]
            except ValueError:
                record["parse_error"] = "non-numeric RESULT"
        record["valid_result"] = (
            p.returncode == 0 and all(record.get("finite", [False]))
            and "ERROR" not in (p.stdout + p.stderr).upper()
        )
        return record

    cases = [
        ("upstream_example", (2.4, 2.3, 4.5)),
        ("upstream_example_O_swap", (2.4, 4.5, 2.3)),
        ("bent_control", (3.0, 2.2, 2.2)),
        ("bent_asymmetric", (3.0, 2.1, 2.3)),
        ("bent_asymmetric_O_swap", (3.0, 2.3, 2.1)),
        ("linear_OCO", (4.4, 2.2, 2.2)),
        ("linear_OCO_paper_rounded", (4.412, 2.206, 2.206)),
        ("linear_OCO_asymmetric", (4.4, 2.1, 2.3)),
        # Exactly representable binary distances remove decimal-rounding doubt.
        ("linear_OCO_binary_exact", (4.0, 2.0, 2.0)),
        ("linear_OCO_binary_exact_225", (4.5, 2.25, 2.25)),
        ("linear_OCO_asymmetric_binary_exact", (4.5, 2.0, 2.5)),
        ("linear_OOC", (2.6, 2.2, 4.8)),
    ]
    for delta in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
        cases.append((f"OCO_bend_delta_{delta:g}_rad", (4.4 * math.cos(delta / 2), 2.2, 2.2)))
    for big_r in (10.0, 20.0, 40.0):
        oc = math.hypot(big_r, 2.29 / 2)
        cases.append((f"C_plus_O2_R{big_r:g}", (2.29, oc, oc)))
    # Perpendicular O + CO Jacobi geometries; masses match the evaluator.
    for big_r in (10.0, 20.0, 40.0):
        co = 2.13
        carbon_fraction = 12.0 / (12.0 + 15.99491462)
        oo = math.hypot(big_r, carbon_fraction * co)
        other_oc = math.hypot(big_r, (1 - carbon_fraction) * co)
        cases.append((f"O_plus_CO_R{big_r:g}", (oo, co, other_oc)))
    results = [probe(name, r) for name, r in cases]

    differences = []
    if args.finite_difference:
        # Strictly interior geometry, so all these distance stencils are valid.
        center = (3.0, 2.1, 2.3)
        reference = probe("fd_center", center)
        for h in (1e-3, 1e-4, 1e-5):
            entry = {"h_bohr": h, "center": reference, "axes": []}
            for axis in range(3):
                minus, plus = list(center), list(center)
                minus[axis] -= h
                plus[axis] += h
                lo = probe(f"fd_axis{axis}_minus", minus)
                hi = probe(f"fd_axis{axis}_plus", plus)
                rec = {"axis": axis, "minus": lo, "plus": hi}
                if all(x.get("valid_result") for x in (reference, lo, hi)):
                    fd = (hi["energy_hartree"] - lo["energy_hartree"]) / (2 * h)
                    analytic = reference["gradient_hartree_per_bohr"][axis]
                    rec.update(finite_difference=fd, absolute_error=abs(fd - analytic))
                entry["axes"].append(rec)
            differences.append(entry)

    print(json.dumps({
        "executable": args.executable,
        "data_directory": args.data_directory,
        "case_count": len(results),
        "finite_case_count": sum(x.get("valid_result", False) for x in results),
        "cases": results,
        "interior_gradient_checks": differences,
    }, indent=2, allow_nan=False))
    if args.require_finite and not all(x.get("valid_result", False) for x in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
