#!/usr/bin/env python3

from __future__ import annotations

import sys

from runtime_bootstrap import import_repo_module

_doc_duplicate_module = import_repo_module(__file__, "scripts.check_doc_near_duplicates")


if __name__ == "__main__":
    sys.exit(_doc_duplicate_module.main())
