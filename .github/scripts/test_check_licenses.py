#!/usr/bin/env python3
"""Regression tests for check-licenses.py. Run: python3 test_check_licenses.py"""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "check_licenses", Path(__file__).parent / "check-licenses.py"
)
check_licenses = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_licenses)

ALLOWED = {"MIT", "Apache-2.0", "Apache", "BSD-3-Clause", "BSD", "ISC", "LicenseRef-PolyForm-Shield-1.0.0"}

CASES = [
    ("MIT", True),
    ("BSD-3-Clause", True),
    ("(MIT OR Apache-2.0)", True),
    ("GPL-3.0 OR MIT", True),
    ("MIT AND BSD-3-Clause", True),
    ("GPL-3.0 AND MIT", False),
    ("GPL-3.0 OR MIT AND GPL-3.0", False),
    ("MIT AND (GPL-3.0 OR BSD-3-Clause)", True),
    ("(MIT OR GPL-3.0) AND GPL-3.0", False),
    ("MIT OR", False),
    ("MIT WITH Classpath-exception-2.0", False),
    ("LicenseRef-PolyForm-Shield-1.0.0", True),
    (["GPL-3.0", "MIT"], True),
    # substring matches must not pass: 'mit' in 'limited'
    ("Limited Proprietary License", False),
    ("License :: OSI Approved :: Apache Software License", True),
    ("License :: OSI Approved :: BSD License", True),
    ("License :: OSI Approved :: GNU General Public License v3 (GPLv3)", False),
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
    formats = [
        ({"pkg": {"licenses": "GPL-3.0 AND MIT"}}, True),
        ({"pkg": {"licenses": "MIT OR GPL-3.0"}}, False),
        ([{"Name": "pkg", "License": "GPL-3.0 AND MIT"}], True),
        ({"components": [{"name": "pkg", "licenses": [{"license": {"id": "MIT"}}]}]}, False),
        ({"components": [{"name": "pkg", "licenses": [{"expression": "MIT OR GPL-3.0"}]}]}, False),
        ({"components": [{"name": "pkg", "licenses": [{"expression": "MIT AND GPL-3.0"}]}]}, True),
    ]
    for data, want_bad in formats:
        got_bad = bool(check_licenses.check_licenses(data, ALLOWED))
        assert got_bad == want_bad, f"check_licenses({data!r}) bad={got_bad}, expected {want_bad}"
    print(f"ok - {len(CASES) + len(formats)} license checker cases pass")


if __name__ == "__main__":
    main()
