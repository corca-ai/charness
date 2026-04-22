#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {Path(sys.argv[0]).name} <notion_url_or_page_id> <output_file>", file=sys.stderr)
        return 1

    notion_target = sys.argv[1]
    output_file = Path(sys.argv[2]).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    vendor_script = Path(__file__).resolve().parents[1] / "vendor" / "notion-to-md.py"
    result = subprocess.run(
        [sys.executable, str(vendor_script), notion_target, str(output_file)],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
