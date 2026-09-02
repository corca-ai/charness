#!/usr/bin/env python3
"""Declare the optional clone inventory as unproven in this tree."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print("ADVISORY: inventory_nose_clones.py unavailable; clone-family inventory is unproven.")
    raise SystemExit(3)


if __name__ == "__main__":
    main()
