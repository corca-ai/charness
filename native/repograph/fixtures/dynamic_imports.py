import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pkg import mod

dynamic = import_repo_module(__file__, "pkg.mod")
