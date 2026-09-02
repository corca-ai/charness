#!/usr/bin/env python3
"""Declare the optional CLI inventory unavailable in this tree."""

import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()
print("inventory_cli_ergonomics.py unavailable; skipping optional advisory inventory.")
