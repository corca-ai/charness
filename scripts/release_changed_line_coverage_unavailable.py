#!/usr/bin/env python3
"""Report that the release changed-line proof has no base SHA."""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(
        "release changed-line coverage: no resolved origin/main base SHA; proof is unestablished",
        file=sys.stderr,
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
