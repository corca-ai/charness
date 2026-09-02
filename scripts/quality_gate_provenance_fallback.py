#!/usr/bin/env python3
"""Emit the consumer-tree fallback for the optional provenance gate."""

from __future__ import annotations

import argparse
import os


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    print("status: unestablished")
    print("proof_level: unavailable")
    print("non_claims: [provenance contract checker is not packaged in this consumer tree]")
    if os.environ.get("CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY") == "1":
        print("REFUSAL: release provenance proof is unavailable")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
