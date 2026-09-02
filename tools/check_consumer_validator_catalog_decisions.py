#!/usr/bin/env python3
"""Run the Charness-owned consumer-validator adoption decision check."""

from __future__ import annotations

from scripts import check_consumer_validator_catalog


def main(argv: list[str] | None = None) -> int:
    return check_consumer_validator_catalog.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
