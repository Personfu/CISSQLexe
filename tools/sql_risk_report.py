#!/usr/bin/env python3
"""Create an educational SQL risk report from local query examples.

This does not attack databases. It flags query-construction patterns that should
be remediated with parameterized queries and least-privilege access.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

RISK_PATTERNS = [
    ('string-concatenation-marker', re.compile(r"\+\s*(user|input|param|query|request)", re.I)),
    ('format-placeholder', re.compile(r"%s|\.format\(|\$\{", re.I)),
    ('stacked-query-risk', re.compile(r";\s*(drop|delete|update|insert|exec)\b", re.I)),
    ('wildcard-select', re.compile(r"select\s+\*", re.I)),
]


def analyze(item: dict[str, Any]) -> dict[str, Any]:
    query = str(item.get('query', ''))
    hits = [name for name, pattern in RISK_PATTERNS if pattern.search(query)]
    return {**item, 'risk_flags': hits, 'recommendation': 'Use parameterized queries and scoped database roles.' if hits else 'No simple pattern flags observed.'}


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a SQL risk education report from local JSON examples.')
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding='utf-8'))
    rows = raw if isinstance(raw, list) else raw.get('queries', [])
    results = [analyze(row) for row in rows]
    args.output.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'wrote {args.output}')


if __name__ == '__main__':
    main()
