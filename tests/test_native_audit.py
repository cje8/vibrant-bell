"""Offline audit-record and fail-closed parser tests, not a native PES CI job."""

import contextlib
import io
import json
import math
from pathlib import Path
import runpy
import subprocess
import unittest
from unittest.mock import patch


AUDIT = Path(__file__).resolve().parents[1] / "research/native-pes-audit-2026-09-04"


def strict_json(text):
    def reject(value):
        raise ValueError(value)
    return json.loads(text, parse_constant=reject)


class NativeAuditTests(unittest.TestCase):
    def run_guard(self, stdout, stderr="", returncode=0, timeout=False):
        buffer = io.StringIO()
        result = subprocess.CompletedProcess([], returncode, stdout, stderr)
        args = [str(AUDIT / "run_native_cases.py"), "/mock/pes", "/mock/data", "--require-finite"]
        effect = subprocess.TimeoutExpired("mock", 30) if timeout else None
        with patch("sys.argv", args), patch("subprocess.run", return_value=result, side_effect=effect), contextlib.redirect_stdout(buffer):
            try:
                runpy.run_path(str(AUDIT / "run_native_cases.py"), run_name="__main__")
            except SystemExit as exc:
                code = exc.code
            else:
                code = 0
        return code, strict_json(buffer.getvalue())

    def test_finite_output_passes(self):
        code, data = self.run_guard("RESULT -0.5 1 2 3\nFINITE T T T T\n")
        self.assertEqual(code, 0)
        self.assertEqual(data["finite_case_count"], 24)

    def test_nan_and_infinity_fail_even_when_child_exits_zero(self):
        for value in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(value=value):
                code, data = self.run_guard(f"RESULT -0.5 {value} 0 0\n")
                self.assertEqual(code, 1)
                self.assertEqual(data["finite_case_count"], 0)
                self.assertIsNone(data["cases"][0]["gradient_hartree_per_bohr"][0])

    def test_nonfinite_energy_fails(self):
        code, _ = self.run_guard("RESULT NaN 0 0 0\n")
        self.assertEqual(code, 1)

    def test_bad_or_missing_result_fails(self):
        for output in ("", "RESULT 1 2 3\n", "RESULT 1 2 3 4 5\n", "RESULT bad 2 3 4\n", "RESULT 1 2 3 4\nRESULT 1 2 3 4\n"):
            with self.subTest(output=output):
                code, _ = self.run_guard(output)
                self.assertEqual(code, 1)

    def test_error_in_either_stream_fails(self):
        for stdout, stderr in (("RESULT 1 2 3 4\nERROR failed", ""), ("RESULT 1 2 3 4\n", "ERROR failed")):
            code, _ = self.run_guard(stdout, stderr)
            self.assertEqual(code, 1)

    def test_child_failure_and_timeout_fail(self):
        for kwargs in ({"returncode": 2}, {"timeout": True}):
            code, _ = self.run_guard("RESULT 1 2 3 4\n", **kwargs)
            self.assertEqual(code, 1)

    def test_preserved_matrices_are_internally_consistent(self):
        names = None
        for mode, count in (("o0_kernel", 21), ("o2_kernel", 19), ("o0_csv", 21), ("o2_csv", 19), ("trap_kernel", 21)):
            data = strict_json((AUDIT / f"{mode}.json").read_text())
            self.assertEqual(data["case_count"], len(data["cases"]))
            self.assertEqual(data["case_count"], 24)
            self.assertEqual(data["finite_case_count"], count)
            self.assertEqual(sum(p["valid_result"] for p in data["cases"]), count)
            current = [p["name"] for p in data["cases"]]
            self.assertEqual(len(set(current)), 24)
            if names is not None:
                self.assertEqual(current, names)
            names = current
            for point in data["cases"]:
                if point["valid_result"]:
                    self.assertEqual(point["returncode"], 0)
                    self.assertTrue(all(math.isfinite(v) for v in [point["energy_hartree"], *point["gradient_hartree_per_bohr"]]))
                elif mode != "trap_kernel":
                    self.assertEqual(point["returncode"], 0)
                    self.assertFalse(all(point["finite"]))

    def test_preserved_summary_is_reproducible(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(AUDIT / "summarize_results.py"), run_name="__main__")
        self.assertEqual(strict_json(output.getvalue()), strict_json((AUDIT / "summary.json").read_text()))

    def test_all_record_json_is_strict(self):
        for path in AUDIT.glob("*.json"):
            with self.subTest(path=path.name):
                strict_json(path.read_text())


if __name__ == "__main__":
    unittest.main()
