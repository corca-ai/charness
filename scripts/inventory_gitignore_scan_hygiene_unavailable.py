#!/usr/bin/env python3
"""Declare the optional gitignore inventory unavailable in this tree."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print("inventory_gitignore_scan_hygiene.py unavailable; skipping optional advisory inventory.")


if __name__ == "__main__":
    main()
