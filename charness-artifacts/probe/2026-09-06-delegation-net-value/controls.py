"""Run correct and axis-varying broken controls outside producer roots."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    correct = (HERE / "control_catalog.py").read_text()
    mutations = {
        "no_forward_chains": (
            "while target not in self.mapping:",
            "if target not in self.mapping: raise ValueError(name)\n            while target not in self.mapping:",
        ),
        "wrong_canonical_key": ("return self.keys[name]", "return name"),
        "wrong_error_subject": ("raise ValueError(name)", "raise ValueError(target)"),
        "missing_structural_precedence": (
            "targets[name] = target",
            "targets[name] = target\n            if target not in self.mapping: raise ValueError(name)",
        ),
        "mutate_caller": (
            "pairs = list(aliases or [])",
            "pairs = list(aliases or [])\n        if aliases: aliases.clear()",
        ),
        "swallow_unknown": (
            "return self.mapping[self.canonical_key(name)]",
            "return self.mapping.get(self.keys.get(name))",
        ),
        "unknown_with_aliases": (
            "return self.keys[name]",
            "return self.keys.get(name) if len(self.keys) > len(self.mapping) else self.keys[name]",
        ),
        "mutate_values_on_error": (
            "raise ValueError(name)",
            "[value.clear() for value in mapping.values() if isinstance(value, list)]; raise ValueError(name)",
        ),
    }
    candidates = {"correct": correct}
    for name, (before, after) in mutations.items():
        if before not in correct:
            raise RuntimeError(f"mutation did not apply: {name}")
        candidates[name] = correct.replace(before, after)
    candidates["correct_modular"] = "from .helper import Catalog\n"
    observations = []
    with tempfile.TemporaryDirectory(prefix="goal805-oracle-controls-") as raw:
        root = Path(raw)
        (root / "src").mkdir()
        (root / "src/__init__.py").write_text("")
        (root / "src/helper.py").write_text(correct)
        for name, source in candidates.items():
            (root / "src/catalog.py").write_text(source)
            completed = subprocess.run(
                [sys.executable, "-B", str(HERE / "oracle.py"), str(root)],
                capture_output=True, text=True, timeout=20, check=False,
            )
            expected = 0 if name.startswith("correct") else 1
            observations.append({"name": name, "expected_exit": expected,
                                 "actual_exit": completed.returncode,
                                 "stdout": completed.stdout, "stderr": completed.stderr})
    payload = {"sources": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                           for name in ("oracle.py", "controls.py", "control_catalog.py")},
               "observations": observations}
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(rendered)
    print(rendered)
    return 0 if all(row["expected_exit"] == row["actual_exit"] for row in observations) else 1


if __name__ == "__main__":
    raise SystemExit(main())
