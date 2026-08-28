from pathlib import Path
from glob import glob

python_files = glob("pkg/*.py")
other_python_files = list(Path(".").rglob("*.py"))
