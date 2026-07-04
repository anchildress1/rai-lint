#!/usr/bin/env python3
"""Regression tests for check-licenses.py. Run: python3 test_check_licenses.py"""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "check_licenses", Path(__file__).parent / "check-licenses.py"
)
check_licenses = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_licenses)

ALLOWED = {"MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "LicenseRef-PolyForm-Shield-1.0.0"}

CASES = [
    ("MIT", True),
    ("BSD-3-Clause", True),
    ("(MIT OR Apache-2.0)", True),
    ("LicenseRef-PolyForm-Shield-1.0.0", True),
    (["GPL-3.0", "MIT"], True),
    # substring matches must not pass: 'mit' in 'limited'
    ("Limited Proprietary License", False),
    ("mitigated-license", False),
    ("GPL-3.0", False),
    # unknown/missing licenses fail closed
    ("UNKNOWN", False),
    (None, False),
]


def main():
    for lic, want in CASES:
        got = check_licenses.license_allowed(lic, ALLOWED)
        assert got == want, f"license_allowed({lic!r}) = {got}, expected {want}"
    print(f"ok - {len(CASES)} license checker cases pass")


if __name__ == "__main__":
    main()
