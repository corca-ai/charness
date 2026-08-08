"""A repo that is bundle-READY by construction, so the ready path is owned in every state.

`#560`: after `#537` the ready payload and render shape were owned only by tests that require
the LIVE worktree to be clean — `test_this_repo_is_currently_bundle_ready` and
`test_this_repo_is_currently_closeout_bundle_ready`. So while any blocker is live (an unowned
artifact path, a drifted plugin mirror, a manifest under edit) ZERO tests exercise the ready
path. That is the state in which a ready-path regression is most likely to be introduced and
least likely to be noticed, and the preflight contract
(`charness-artifacts/spec/2026-08-06-final-bundle-preflight-contract.md`) had declared this
fixture as an acceptance check with nothing implementing it.

Reproduced before building: `printf '{"probe":1}' > charness-artifacts/spec/probe.json` then
running the two suites gives `2 failed, 37 passed`, and both failures ARE the readiness tests.

The live readiness tests stay. "Is THIS repo bundle-ready right now" is a real question worth
one failing test per surface. What this adds is that the ready path is proven even when the
answer is no.

## Ready by construction, and what that costs

The manifest's identities are COMPUTED over the fixture tree with the validator's own helpers
(`_root_identity_digest`, `_sha256_file`) rather than transcribed. That is deliberate for
FIXTURE CONSTRUCTION and would be wrong for an assertion: a test that recomputed the expected
value with the subject's own code would pass with the subject deleted. Nothing here is
asserted — the assertions live in the tests and read the preflight's ready PAYLOAD.

Be precise about what that recomputation buys, because the careful wording above invited a
stronger reading than it earns: `build_plan` validates with `verify_current=False`, and every
`identity_mode` in the template is `captured`, so the digest branches are SKIPPED and these
fields are only 64-hex format-checked. The fixture would be equally `ready` with the template's
live digests left in place. They are recomputed so the artifact is internally honest, not
because anything here exercises identity freshness — `tests/quality_gates/test_slice_manifest.py`
owns that. For the same reason, do not credit this fixture with manifest-identity coverage:
collapsing every commit SHA to one value makes `validate_manifest`'s cross-field equalities
(`carrier.sha == target.sha`, the premise and readback SHAs, the ancestry check) vacuous INSIDE
the fixture.

The critique binding is COPIED from the live repo rather than forged, then RE-STAMPED against
the fixture. A durable critique artifact binds a prepare packet by path, packet SHA-256, and
reviewed-input identity, and the packet's Markdown must be the deterministic rendering of its
JSON. Hand-writing that triple would be a second implementation of the binding rule, so the
fixture copies the real one and re-derives it with the real producers.

## What this fixture is NOT independent of

Honest scope, because the docstring previously implied more. The fixture is a copy of the live
tree minus `charness-artifacts`, so it is independent of the ARTIFACT-PATH blocker class (the
`#560` repro), of manifest git-state, and of the changed-path set. It is NOT independent of the
plugin mirror, `.agents/surfaces.json`, or the source tree: those are copied, so a live mirror
drift travels into the fixture and blocks it too. For those classes the fan-out is worse, not
better. `_restamp_reviewed_binding` closes the one coupling that was both silent and imminent.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MANIFEST_TEMPLATE = "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"
FIXTURE_MANIFEST = "charness-artifacts/goals/2026-08-09-bundle-ready-fixture.slice-manifest.json"
FIXTURE_CRITIQUE = "charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md"
BEHAVIOR_CHANNEL = "behavior=python3 -m pytest -q tests/quality_gates/test_final_bundle_preflight.py"

# The bound critique triple plus what the manifest and the binding point AT. `charness-artifacts`
# is excluded from the repo copy (`REPO_COPY_EXCLUDE_NAMES`), so every artifact the plan reads has
# to be placed here explicitly — which is also what keeps the fixture's inputs legible.
REVIEWED_SPEC = "charness-artifacts/spec/2026-08-06-final-bundle-preflight-contract.md"

SEEDED_ARTIFACTS = (
    FIXTURE_CRITIQUE,
    "charness-artifacts/critique/2026-08-06-041231-packet.json",
    "charness-artifacts/critique/2026-08-06-041231-packet.md",
    REVIEWED_SPEC,
    "charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md",
)

_SHA1 = re.compile(r"^[0-9a-f]{40}$")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.email=fixture@charness.test", "-c", "user.name=fixture", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _rewrite_shas(node: object, sha: str) -> None:
    """Repoint every captured git SHA at the fixture's own history.

    Every 40-hex string in the template is a commit identity from the real repo, and none of
    them exist in the fixture's git. `premise.local_head_sha` in particular becomes the plan's
    base, and the preflight requires it to be an ancestor of HEAD.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and _SHA1.match(value):
                node[key] = sha
            else:
                _rewrite_shas(value, sha)
    elif isinstance(node, list):
        # Rewrite list ELEMENTS too. The dict branch only reaches a string through a key, so a
        # bare 40-hex string inside a list hit neither branch and survived un-rewritten — latent
        # today (the template has no such field) but the docstring's premise, "every 40-hex
        # string is a commit identity", was unenforced against a template that is a live artifact.
        for index, item in enumerate(node):
            if isinstance(item, str) and _SHA1.match(item):
                node[index] = sha
            else:
                _rewrite_shas(item, sha)


def build_bundle_ready_repo(repo: Path) -> dict[str, str]:
    """Seed an already-cloned repo copy into a bundle-ready state and return its plan inputs."""
    from scripts.slice_manifest_lib import _root_identity_digest, _sha256_file

    missing = [relative for relative in (*SEEDED_ARTIFACTS, MANIFEST_TEMPLATE) if not (ROOT / relative).is_file()]
    if missing:
        # Named loudly, because the alternative is a session fixture erroring all three tests
        # with a `shutil.copy2` traceback that says nothing about the fixture's premise.
        raise AssertionError(f"the bundle-ready fixture's seed inputs are missing: {missing}")
    for relative in SEEDED_ARTIFACTS:
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    _restamp_reviewed_binding(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "seed the artifacts the bundle plan reads")

    # The base is captured BEFORE the manifest commit, so it is a strict ancestor of HEAD and the
    # `candidate_base_not_ancestor` blocker cannot fire for a reason the fixture created itself.
    base_sha = _git(repo, "rev-parse", "HEAD")

    manifest = json.loads((ROOT / MANIFEST_TEMPLATE).read_text(encoding="utf-8"))
    _rewrite_shas(manifest, base_sha)
    for root in manifest["reader_roots"]:
        root["identity_sha256"] = _root_identity_digest(repo, [str(p) for p in root["identity_paths"]])
    for pair in manifest["parity_pairs"]:
        pair["source_sha256"] = _sha256_file(repo / pair["source"])
        pair["derived_sha256"] = _sha256_file(repo / pair["derived"])
    critique_text = (repo / FIXTURE_CRITIQUE).read_text(encoding="utf-8")
    manifest["critique"] = {
        "status": "captured",
        "artifact_path": FIXTURE_CRITIQUE,
        "packet_path": FIXTURE_CRITIQUE,
        "packet_sha256": _sha256_file(repo / FIXTURE_CRITIQUE),
        # The two identities the durable artifact declares about its BOUND prepare packet. Read
        # out of the artifact rather than pasted, so a re-copied critique cannot silently
        # disagree with the manifest that points at it.
        "reviewed_packet_sha256": _declared(critique_text, "packet sha256"),
        "reviewed_identity_sha256": _declared(critique_text, "identity sha256"),
    }
    (repo / FIXTURE_MANIFEST).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "bind the fixture manifest")
    return {"repo": str(repo), "manifest": FIXTURE_MANIFEST, "critique": FIXTURE_CRITIQUE, "base": base_sha}


def _declared(text: str, field: str) -> str:
    from scripts.critique_reviewed_input_binding import _binding_fields
    from scripts.final_bundle_preflight_evidence import _strip_markup

    fields = _binding_fields(text)
    if field not in fields:
        raise AssertionError(
            f"{FIXTURE_CRITIQUE} declares no `{field}` under its reviewed-input binding; "
            f"present fields are {sorted(fields)}"
        )
    # The SUBJECT's stripper, not a second one. A local `.strip('`')` agreed with it only for
    # plain backticks; a critique written with bold emphasis would leave a `*` in the value and
    # push it into the manifest.
    return _strip_markup(fields[field])


def _restamp_reviewed_binding(repo: Path) -> None:
    """Rebind the copied critique to the FIXTURE's bytes, with the real producer.

    Without this the fixture is not independent of live state, in a way no test would show.
    `critique_inventory` verifies the binding with `check_current=True`, which resolves the repo
    root by walking up to the nearest `.git` — the FIXTURE — and RECOMPUTES the identity over the
    packet's `reviewed_paths`. Under `sha256-v2` working-tree mode that digest reduces to the
    bytes and exec bit of one file: the preflight contract spec, copied out of the live tree.

    So the next edit to that spec would have staled the fixture's binding and reddened all three
    fixture tests ALONGSIDE the two live readiness tests — a five-test fan-out for one cause,
    which is the shape `#537` exists to have removed, and zero ready-path coverage in exactly the
    window this fixture was built to cover. The spec is not a remote hazard either: it is the
    contract whose acceptance check this fixture implements.

    Re-stamping uses `build_reviewed_input_identity` and `render_markdown` — the producers — so
    the fixture never hand-writes a binding rule.
    """
    from scripts.critique_packet_lib import render_markdown
    from scripts.reviewed_input_identity import build_reviewed_input_identity

    critique = repo / FIXTURE_CRITIQUE
    text = critique.read_text(encoding="utf-8")
    packet_rel = _declared(text, "packet path")
    packet_json = repo / packet_rel
    packet_md = packet_json.with_suffix(".md")
    packet = json.loads(packet_json.read_text(encoding="utf-8"))
    declared = packet["reviewed_input_identity"]

    packet["reviewed_input_identity"] = build_reviewed_input_identity(
        repo_root=repo,
        reviewed_paths=list(declared["reviewed_paths"]),
        changed_ref=declared.get("changed_ref"),
        algorithm=declared.get("algorithm", "sha256-v1"),
    )
    packet_json.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    packet_md.write_text(render_markdown(packet), encoding="utf-8")

    from scripts.slice_manifest_lib import _sha256_file

    replacements = {
        "Packet SHA256": _sha256_file(packet_json),
        "Packet Markdown SHA256": _sha256_file(packet_md),
        "Identity SHA256": packet["reviewed_input_identity"]["identity_sha256"],
    }
    lines = text.split("\n")
    for index, line in enumerate(lines):
        for label, value in replacements.items():
            if line.startswith(f"- {label}: "):
                lines[index] = f"- {label}: `{value}`"
    critique.write_text("\n".join(lines), encoding="utf-8")


@pytest.fixture(scope="session")
def bundle_ready_repo(seeded_charness_git_repo: Path, tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    """A bundle-ready repo, built once per session and never mutated by a test.

    Session-scoped because the clone dominates its cost, and read-only by contract: a test that
    mutated it would silently change what every later test measures.
    """
    from tests.repo_copy import clone_seeded_charness_repo

    target = tmp_path_factory.mktemp("bundle-ready")
    repo = clone_seeded_charness_repo(target, seeded_charness_git_repo)
    return build_bundle_ready_repo(repo)
