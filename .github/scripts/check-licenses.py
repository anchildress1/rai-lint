#!/usr/bin/env python3
"""
License checker script for GitHub Actions.

Usage: python3 check-licenses.py <json_file>

Where:
- json_file: Path to JSON file with license data

Supports three formats:
- Node (license-checker): {"pkg": {"licenses": "MIT", ...}}
- Python (pip-licenses): [{"Name": "pkg", "License": "MIT", ...}]
- CycloneDX SBOM: {"components": [{"name": "pkg", "licenses": [...]}]}
"""

import json
import sys
import re
from pathlib import Path

def load_data(json_file):
    path = Path(json_file).resolve()
    if not path.is_relative_to(Path.cwd().resolve()):
        print(f"Refusing to read outside the working directory: {json_file}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {json_file}: {e}", file=sys.stderr)
        sys.exit(1)

def _component_license(component):
    licenses = []
    for entry in component.get('licenses', []):
        if not isinstance(entry, dict):
            continue
        license_info = entry.get('license') or {}
        value = entry.get('expression') or license_info.get('id') or license_info.get('name')
        if value:
            licenses.append(value)
    if len(licenses) == 1:
        return licenses[0]
    return licenses or None


def _license_entries(data):
    if isinstance(data, list):
        for item in data:
            yield item.get('Name'), item.get('License')
    elif isinstance(data, dict) and 'components' in data:
        for component in data['components']:
            yield component.get('name'), _component_license(component)
    elif isinstance(data, dict):
        for package, info in data.items():
            yield package, info.get('licenses')
    else:
        print("Unknown JSON format", file=sys.stderr)
        sys.exit(1)


def check_licenses(data, allowed):
    return [(name, lic) for name, lic in _license_entries(data) if not license_allowed(lic, allowed)]


class LicenseExpression:
    def __init__(self, expression, allowed):
        self.tokens = re.findall(r"\(|\)|[A-Za-z0-9.-]+", expression)
        self.valid_tokens = bool(self.tokens) and "".join(self.tokens).lower() == re.sub(
            r"\s+", "", expression
        ).lower()
        self.allowed_ids = {item.lower() for item in allowed if item}
        self.position = 0

    def is_allowed(self):
        if not self.valid_tokens:
            return False
        try:
            result = self._or()
        except ValueError:
            return False
        return result and self.position == len(self.tokens)

    def _or(self):
        result = self._and()
        while self._current() == 'OR':
            self.position += 1
            next_result = self._and()
            result = result or next_result
        return result

    def _and(self):
        result = self._atom()
        while self._current() == 'AND':
            self.position += 1
            next_result = self._atom()
            result = result and next_result
        return result

    def _atom(self):
        token = self._current()
        if token is None or token in {'AND', 'OR', ')'}:
            raise ValueError('expected license')
        self.position += 1
        if token == '(':
            result = self._or()
            if self._current() != ')':
                raise ValueError('unclosed license group')
            self.position += 1
            return result
        return token.lower() in self.allowed_ids

    def _current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position].upper()
        return None


def license_allowed(lic, allowed):
    """Accept a license value only when a permitted choice satisfies every required license."""
    if lic is None:
        return False
    if isinstance(lic, (list, tuple)):
        return any(license_allowed(item, allowed) for item in lic)
    return LicenseExpression(str(lic).strip(), allowed).is_allowed()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 check-licenses.py <json_file>", file=sys.stderr)
        sys.exit(1)

    json_file = sys.argv[1]

    allowed = {
        'MIT',
        'Apache-2.0', 'Apache',
        'BSD-3-Clause', 'BSD-2-Clause', 'BSD',
        'ISC',
        'Python-2.0', 'Python',
        'LicenseRef-PolyForm-Shield-1.0.0',
    }

    data = load_data(json_file)
    bad = check_licenses(data, allowed)

    if bad:
        print('❌ Disallowed licenses found:')
        for name, lic in bad:
            print(f'  {name}: {lic}')
        sys.exit(1)
    else:
        print('✅ All licenses are allowed.')


if __name__ == '__main__':
    main()
