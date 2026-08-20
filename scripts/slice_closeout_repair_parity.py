#!/usr/bin/env python3
"""Repair-class and reviewer-parity advisory logic for slice closeout.

This module owns the parity boundary: compare changed Python source with the
reviewer snapshot, classify added refusal/detector inputs, and report when the
reviewed body was later repaired. The parent advisory module keeps the other
closeout nudges and delegates this cohesive source/proof concern here.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

_PARITY_HARNESS = "scripts/parity_harness.py"
_REPAIR_CLASS_LINE = re.compile(
    r"(?:\b(?:refus\w*|reject\w*|unhonored|uninterpreted|uncomparable|unread|"
    r"unsupported|malformed|not[-_ ](?:established|configured|found|read))\b|"
    r"report\s*\[\s*['\"](?:ok|status)['\"]\s*\]\s*=\s*False|"
    r"\b(?:findings|violations|problems|uncomparable)\s*\.\s*(?:append|add)\s*\()",
    re.IGNORECASE,
)


def _added_vs_base(repo_root: Path, paths: list[str], base: str) -> list[str]:
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base], cwd=repo_root, capture_output=True
    )
    if probe.returncode != 0:
        return []
    added: list[str] = []
    for path in paths:
        exists = subprocess.run(
            ["git", "cat-file", "-e", f"{base}:{path}"], cwd=repo_root, capture_output=True
        )
        if exists.returncode != 0:
            added.append(path)
    return added


def added_diff_lines(repo_root: Path, base: str, paths: list[str]) -> str:
    """Return added source lines, including untracked files absent from ``base``."""
    if not paths:
        return ""
    res = subprocess.run(
        ["git", "diff", "--unified=0", base, "--", *paths],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    diff_added = ""
    if res.returncode == 0:
        diff_added = "\n".join(
            line[1:] for line in res.stdout.splitlines() if line.startswith("+") and not line.startswith("+++")
        )
    new_texts = []
    for path in _added_vs_base(repo_root, paths, base):
        try:
            new_texts.append((repo_root / path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return "\n".join([diff_added, *new_texts])


def advise_repair_parity(
    repo_root: Path,
    changed_paths: list[str],
    *,
    base: str = "origin/main",
    harness_path: str = _PARITY_HARNESS,
) -> None:
    """Name repaired functions and expose newly added refusal classes."""
    source_paths = [p for p in changed_paths if p.startswith(("scripts/", "skills/")) and p.endswith(".py")]
    base_probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base], cwd=repo_root, capture_output=True
    )
    if base_probe.returncode != 0:
        if source_paths and (repo_root / ".git").exists():
            print(
                "ADVISORY: repair-parity base is unavailable; added refusal/detector classes "
                f"for {base!r} are UNPROVEN, not clean. Resolve the campaign base and rerun.",
                file=sys.stderr,
            )
        added = ""
    else:
        added = added_diff_lines(repo_root, base, sorted(set(source_paths)))
    classes = [
        line.strip()
        for line in added.splitlines()
        if line.strip()
        and not line.lstrip().startswith(("#", "'''", '\"\"\"'))
        and _REPAIR_CLASS_LINE.search(line)
    ]
    if classes:
        print(
            "ADVISORY: added refusal/detector input class candidates — exercise each exact source line against the real consumer and confirm the new code discriminates. Malformed, type-invalid, comment-only, or literal no-op generators are not evidence; repair the generator/consumer pair if it carries the class:\n"
            + "\n".join(f"  - {line}" for line in classes),
            file=sys.stderr,
        )
    harness = repo_root / harness_path
    if not harness.is_file():
        return
    proc = subprocess.run(
        [sys.executable, str(harness), "--repo-root", str(repo_root), "--against", "review-snapshot"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return
    try:
        report = yaml.safe_load(proc.stdout)
    except yaml.YAMLError:
        return
    if not isinstance(report, dict):
        return
    repaired = report.get("files") or {}
    uncomparable = report.get("uncomparable") or {}
    if not isinstance(repaired, dict) or not isinstance(uncomparable, dict):
        print(
            "ADVISORY: repair-parity returned a malformed report; reviewer parity is "
            "UNPROVEN, not clean. Expected mapping values for `files` and `uncomparable`.",
            file=sys.stderr,
        )
        return
    if not repaired and not uncomparable:
        return
    if not repaired:
        reason = "no reviewer snapshot for this HEAD (none taken, or invalidated by a mid-slice commit)"
        print(
            f"ADVISORY: {len(uncomparable)} changed Python path(s) could NOT be compared against what a "
            f"bounded reviewer read — {reason}. That is UNEXAMINED, not clean: any repair in them is "
            f"unverified. `python3 {harness_path} --against <base-ref>` is the fallback baseline for "
            "a function that already shipped.",
            file=sys.stderr,
        )
        return
    rendered = "; ".join(f"{path}: {', '.join(names)}" for path, names in sorted(repaired.items()))
    unexamined = (
        f" {len(uncomparable)} further path(s) could NOT be compared and are unexamined, not clean."
        if uncomparable
        else ""
    )
    print(
        f"ADVISORY: {report.get('repair_count', 0)} function(s) were REPAIRED after a bounded reviewer "
        f"read them (same signature, changed body) — {rendered}.{unexamined} State the INTENDED delta "
        "for each and prove the complement is unchanged; a repair verified only against the finding that "
        "prompted it is how a narrowing ships green. Baseline source is recoverable: "
        f"`python3 {harness_path} --against review-snapshot` lists them, and its "
        "`baseline_source`/`load_module_from_source`/`compare_callables` run the differential.",
        file=sys.stderr,
    )
