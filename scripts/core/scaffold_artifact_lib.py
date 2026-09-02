from __future__ import annotations

import argparse
import os
import runpy
from collections.abc import Callable, Sequence
from pathlib import Path


def _load_repo_helper(module_filename: str) -> dict[str, object]:
    """Reach a repo-level `scripts/` helper without importing repo machinery.

    ``scaffold_ideation_artifact.py`` loads this module by file path with no
    package context, so the seams its siblings use (``runtime_bootstrap`` /
    ``skill_runtime_bootstrap``) are unavailable here and
    ``test_the_owner_stays_importable_with_no_package_context`` forbids them.
    ``runpy`` over an ancestor walk is the same stdlib-only spelling
    the artifact runners use for the identical constraint, and it finds
    ``scripts/<helper>.py`` at the repo root here and at the plugin root once
    exported. Both helpers this module needs ship in that same directory, so the
    walk is parameterized rather than copied per helper.
    """
    helper = next(
        (
            candidate
            for ancestor in Path(__file__).resolve().parents
            for candidate in (
                ancestor / "scripts" / module_filename,
                ancestor / "scripts" / "artifacts" / module_filename,
            )
            if candidate.is_file()
        ),
        None,
    )
    if helper is None:
        raise ImportError(f"scripts/{module_filename} not found")
    return runpy.run_path(str(helper))


emit_yaml = _load_repo_helper("yaml_output.py")["emit_yaml"]
_artifact_naming = _load_repo_helper("artifact_naming_lib.py")
slugify = _artifact_naming["slugify"]

# Re-exported, not re-implemented. The subject-identity concept lives in its own module (the
# length gate refused one file for both, and the seam was already in the docstrings), while the
# families keep ONE import surface: `ideation`'s scaffold has no package context and reaches
# this module by an ancestor walk, so making six scaffolds each walk to a second file would
# trade a cohesive split for six copies of the walk.
_subject_identity = _load_repo_helper("artifact_subject_identity.py")
SUBJECT_MATCH_MATCH = _subject_identity["SUBJECT_MATCH_MATCH"]
SUBJECT_MATCH_MISMATCH = _subject_identity["SUBJECT_MATCH_MISMATCH"]
SUBJECT_MATCH_UNKNOWN = _subject_identity["SUBJECT_MATCH_UNKNOWN"]
SUBJECT_MATCH_UNDECLARED = _subject_identity["SUBJECT_MATCH_UNDECLARED"]
SUBJECT_MATCH_ROUTED = _subject_identity["SUBJECT_MATCH_ROUTED"]
SUBJECT_IDENTITY_KEYS = _subject_identity["SUBJECT_IDENTITY_KEYS"]
SUBJECT_REFUSAL_KEYS = _subject_identity["SUBJECT_REFUSAL_KEYS"]
record_subject_channels = _subject_identity["record_subject_channels"]
record_subject_slug = _subject_identity["record_subject_slug"]
compose_subject_key = _subject_identity["compose_subject_key"]
subject_identity_facts = _subject_identity["subject_identity_facts"]
subject_refusal_facts = _subject_identity["subject_refusal_facts"]
writes_in_place = _subject_identity["writes_in_place"]
diverts_from_target = _subject_identity["diverts_from_target"]
final_subject_facts = _subject_identity["final_subject_facts"]


def validator_command(
    *,
    repo_root: Path,
    script_file: str | Path,
    script_names: Sequence[str],
    artifact_path: str | None = None,
    evidence_mode: bool = False,
) -> str:
    if not script_names:
        raise ValueError("script_names must not be empty")

    # Repo-local validators win so a consumer repo cites the same strict check
    # as its broad gate; installed-plugin validators are fallback-only.
    suffix = " --evidence-led" if evidence_mode else ""
    suffix += f" --paths {artifact_path}" if artifact_path else ""
    for script_name in script_names:
        repo_local = _repo_script(repo_root, script_name)
        if repo_local is not None:
            relative = repo_local.relative_to(repo_root).as_posix()
            return f"python3 {relative} --repo-root .{suffix}"
    for ancestor in Path(script_file).resolve().parents:
        for script_name in script_names:
            candidate = _repo_script(ancestor, script_name)
            if candidate is not None:
                return f"python3 {candidate} --repo-root .{suffix}"
    raise FileNotFoundError(f"{script_names[0]} not found in installed Charness layout")


def _repo_script(root: Path, script_name: str) -> Path | None:
    """`<root>/scripts/<name>` flat, or inside the concept package that owns it."""
    flat = root / "scripts" / script_name
    if flat.is_file():
        return flat
    scripts_root = root / "scripts"
    if not scripts_root.is_dir():
        return None
    packaged = sorted(p for p in scripts_root.glob(f"*/{script_name}") if p.is_file())
    return packaged[0] if packaged else None


def current_pointer_payload(
    *,
    repo_root: Path,
    output_dir: Path,
    date_text: str,
    title: str,
    template: str,
    validator_command: str,
    size_budget: dict[str, object] | None = None,
) -> dict[str, object]:
    artifact_path = output_dir / "latest.md"
    write_path, write_role, symlink_target = current_pointer_write_path(repo_root, artifact_path)
    payload: dict[str, object] = {
        "artifact_path": str(artifact_path),
        "artifact_role": "current_pointer",
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        **write_target_facts(repo_root, write_path),
        "current_pointer_symlink_target": symlink_target,
        "date": date_text,
        "title": title,
        "template": template,
        "validator_command": validator_command,
    }
    # Surface the artifact's size budget as part of the canonical scaffold
    # contract so a run writes-to-fit up front instead of writing long and then
    # burning a trim-to-fit edit/re-measure loop against a ceiling it could not
    # see until the validator rejected it. Optional: skills without a size ceiling
    # omit it entirely (no field), so existing scaffold consumers are unchanged.
    if size_budget is not None:
        payload["size_budget"] = size_budget
    return payload


def portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


CURRENT_POINTER_STATE_KEYS = (
    "current_pointer_is_symlink",
    "current_pointer_target_path",
    "current_pointer_target_exists",
)


def current_pointer_state(repo_root: Path, artifact_path: Path) -> dict[str, object]:
    """SINGLE OWNER of what a `latest.md` current pointer resolves to.

    #548: SIX implementations of this rule existed -- this one plus five private copies, in
    `resolve_artifact_path.py`, `resolve_quality_artifact.py`,
    `inventory_current_pointer_layouts.py`, `scaffold_debug_artifact.py`, and
    `plan_debug_run.py`. Three of them produced the same `write_artifact_path` /
    `write_artifact_role` pair from separate code, and nothing forced the copies to agree, so
    the key came to mean different things depending on which producer a skill happened to
    call; `#538` is the recorded instance of an agent nearly writing over a finished review
    because of it. Two copies were named by the issue, one was found by the duplicate-ratchet
    gate, and two by bounded review. All five now call this. Keep it dependency-free: skill
    scaffolds load this module by file path with no package context.
    """
    absolute_artifact_path = repo_root / artifact_path
    if not absolute_artifact_path.is_symlink():
        return {
            "current_pointer_is_symlink": False,
            "current_pointer_target_path": None,
            "current_pointer_target_exists": None,
            "current_pointer_symlink_target": None,
        }
    raw_target = os.readlink(absolute_artifact_path)
    target_path = Path(raw_target)
    if not target_path.is_absolute():
        target_path = absolute_artifact_path.parent / target_path
    return {
        "current_pointer_is_symlink": True,
        "current_pointer_target_path": portable_path(repo_root, target_path),
        "current_pointer_target_exists": target_path.exists(),
        "current_pointer_symlink_target": raw_target,
    }


def published_pointer_state(repo_root: Path, artifact_path: Path) -> dict[str, object]:
    """The three pointer keys artifact payloads publish, from the single owner.

    Exists so each payload producer is a one-line delegation rather than its own copy of
    "call the owner, then filter". The duplicate-ratchet gate caught that second-order
    duplication immediately after the first consolidation removed the first-order kind --
    consolidating a rule can create a new shared shape that then drifts, which is the trade
    this repo's boundary rule names.
    """
    state = current_pointer_state(repo_root, artifact_path)
    return {key: state[key] for key in CURRENT_POINTER_STATE_KEYS}


def write_target_facts(repo_root: Path, write_path: str) -> dict[str, object]:
    """What writing to `write_path` actually DOES to what is already there.

    #548: every scaffold payload said WHERE to write and none said whether anything was
    already there. `write_artifact_role: current_pointer_target` is true and reads as
    neutral, while the path it names may be a completed dated review whose content a write
    destroys -- and because the filename is dated, nothing afterwards looks wrong. These
    two keys state the consequence instead of leaving it to be inferred from the role.

    Deliberately a FACT, not a policy: whether overwriting is acceptable differs by skill
    (`debug` continues an open investigation in place; `quality` must never overwrite a
    finished review), so each skill's own contract decides what to do with it.
    """
    # `.exists()`, not `.is_file()`: the question is "would a write here destroy something",
    # and a directory or a symlink-to-existing at that path both mean yes-something-is-there.
    # Two planner surfaces answer a narrower question with `.is_file()`; those report whether
    # the artifact is READABLE, which is a different fact with a different name.
    exists = (repo_root / write_path).exists()
    return {
        "write_artifact_target_exists": exists,
        "write_artifact_effect": "overwrite_existing_content" if exists else "create_new_file",
    }


def subject_scoped_record_payload(
    repo_root: Path,
    *,
    output_dir: str,
    date_text: str,
    title: str,
    record_slug: str,
    template: str,
    validator_command_for: Callable[[str], str],
    remedy: str,
    distinguishers: Sequence[str] = ("2", "3", "4"),
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    """The whole payload for a records-only family: never write over an existing record.

    `critique`, `ideation`, and `retro` derive a dated path from the invocation and then write
    a TEMPLATE to it. So the honest rule for all three is not "refuse another subject's record"
    but the stronger one they can actually keep: refuse ANY existing record. Two bounded
    findings forced this. First, the path and the subject key were both derived from the
    invocation, so `target == invocation` held by construction and the refusal arm was
    unreachable — two default-titled critiques on one day resolved to one file and the second
    destroyed the first while the payload reported `match`. Second, deriving the PATH from the
    title while deriving the KEY from `--subject` produced two records for one subject and a
    run that refused a file it had written itself a minute earlier.

    `record_slug` is therefore the ONE channel: the path, the key, and the alternatives all
    come from it, and a declared `--subject` names the record rather than fighting the title.
    The subject facts are still stamped, because a payload's reader is owed the identity of
    what was declined even when the policy did not need it.

    `validator_command_for` is a callable, not a string: the command names the artifact path,
    so computing it before the path is chosen points the validator at a file nothing writes.
    """
    write_path = f"{output_dir}/{date_text}-{record_slug}.md"
    candidates = [write_path, *(f"{output_dir}/{date_text}-{record_slug}-{tail}.md" for tail in distinguishers)]
    resolved = next((candidate for candidate in candidates if not (repo_root / candidate).exists()), None)
    if resolved is None:
        raise SystemExit(
            f"every dated record path this scaffold derives for `{record_slug}` today already "
            f"exists ({', '.join(candidates)}), and a scaffold writes a fresh template over "
            f"whatever is there. {remedy}"
        )
    refusal = (
        {}
        if resolved == write_path
        else subject_refusal_facts(
            refused_path=write_path,
            refused_subject_key=record_subject_slug(write_path),
            # Records-only families route off an occupied path, not off a disagreeing subject:
            # the filename channel cannot tell two same-slug records apart, so the honest
            # reason is that something is there, never that it belongs to someone else.
            reason="record-occupied",
        )
    )
    return dated_record_payload(
        repo_root,
        write_artifact_path=resolved,
        date_text=date_text,
        title=title,
        template=template,
        validator_command=validator_command_for(resolved),
        extra={
            **(extra or {}),
            **refusal,
            **final_subject_facts(
                invocation_subject_key=record_slug,
                target_subject_key=record_subject_slug(resolved),
                chosen=resolved != write_path,
            ),
        },
    )


def with_subject_identity_facts(
    payload: dict[str, object],
    *,
    invocation_subject_key: str | None,
    target_subject_key: str | None,
) -> dict[str, object]:
    """Stamp the subject-identity facts from the payload's FINAL `write_artifact_path`.

    Same ordering rule as `with_write_target_facts`, and for the same recorded reason: a
    producer that swaps its write target after building the payload must call this last, or
    the facts describe a file the payload no longer names. The caller passes the target key it
    read from that final path.
    """
    payload.update(
        subject_identity_facts(
            invocation_subject_key=invocation_subject_key,
            target_subject_key=target_subject_key,
        )
    )
    return payload


def dated_record_payload(
    repo_root: Path,
    *,
    write_artifact_path: str,
    date_text: str,
    title: str,
    template: str,
    validator_command: str,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    """One shape for a records-only scaffold whose write target is a dated file.

    `critique`, `retro`, and `ideation` each built this dict themselves. They were already
    near-identical; adding the write-target facts to all three made them identical enough for
    the duplicate ratchet to call it a new family, which was the correct verdict -- the fix is
    one owner for the shape, not three copies that happen to agree.
    """
    payload: dict[str, object] = {
        "artifact_path": write_artifact_path,
        "artifact_role": "record",
        "write_artifact_path": write_artifact_path,
        "date": date_text,
        "title": title,
        "template": template,
        "validator_command": validator_command,
    }
    payload.update(extra or {})
    return with_write_target_facts(repo_root, payload)


def with_write_target_facts(repo_root: Path, payload: dict[str, object]) -> dict[str, object]:
    """Stamp the write-target facts from the payload's FINAL `write_artifact_path`.

    Producers that build a payload and then REPLACE its write target must call this last.
    `scaffold_debug_artifact.py` does exactly that: it takes the current-pointer payload and
    swaps in a fresh-record target through a fixed key list. The first version of these facts
    was computed before that swap and was not in the list, so the payload reported
    `overwrite_existing_content` for a path guaranteed not to exist -- while `debug/SKILL.md`
    told the agent to trust the key. Recomputing from the final value is what makes a later
    key addition unable to go stale the same way; a longer copy list would not.

    Idempotent for payloads that HAVE a write target: it recomputes the two fact keys and
    touches nothing else. It raises `KeyError` on a payload with no `write_artifact_path`,
    which is deliberate -- a producer that names no write target should not be asking for
    facts about one -- but it is not "safe to call on anything".
    """
    payload.update(write_target_facts(repo_root, str(payload["write_artifact_path"])))
    return payload


def current_pointer_write_path(repo_root: Path, artifact_path: Path) -> tuple[str, str, str | None]:
    state = current_pointer_state(repo_root, artifact_path)
    if not state["current_pointer_is_symlink"]:
        return str(artifact_path), "current_pointer", None
    return (
        str(state["current_pointer_target_path"]),
        "current_pointer_target",
        str(state["current_pointer_symlink_target"]),
    )


def emit_payload_main(
    payload_for: Callable[..., dict[str, object]],
    *,
    artifact_label: str,
    supports_evidence_mode: bool = False,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help=f"Repo root to scaffold the {artifact_label} artifact into")
    parser.add_argument("--title", help=f"Title for the scaffolded {artifact_label} artifact")
    # The invocation's SUBJECT, which the title cannot carry: `debug --title "Debug Review"`
    # is the default and names no investigation, so without this flag "I am continuing THIS
    # investigation" and "I am starting a new one" are the same invocation -- #628's actual
    # defect. Optional: every family falls back to its own derived key, so existing callers
    # are unchanged and the fallback is what makes the ambiguous case resolve to the
    # non-destructive answer instead of the destructive one.
    parser.add_argument(
        "--subject",
        help=(
            f"Subject key this {artifact_label} invocation is for (e.g. the slug of the record "
            "being continued). Defaults to the family's own derived key."
        ),
    )
    if supports_evidence_mode:
        parser.add_argument(
            "--evidence-led",
            action="store_true",
            help="Require typed adversarial evidence and a consumer receipt in the emitted validator command",
        )
    args = parser.parse_args()

    # Always emit the full structured payload — the run reads the template from
    # `payload["template"]` and the write target, validator command, and
    # size_budget as sibling fields. There is no bare rendered-template mode: a
    # single output shape removes the "forgot --json → the budget/write-path never
    # reached the run" footgun that a flag-gated structured mode invites.
    kwargs = {"title": args.title, "subject": args.subject}
    if supports_evidence_mode:
        kwargs["evidence_mode"] = args.evidence_led
    payload = payload_for(args.repo_root.resolve(), **kwargs)
    emit_yaml(payload)
    return 0


def size_budget(validator, default: int | None, adapter: dict, *, guidance: str) -> dict | None:
    """The `size_budget` block a scaffold publishes, resolved the way the GATE resolves it.

    One owner for both raw-file families (debug, quality), which charge WORDS since
    2026-08-19. The forecast is the
    operational half of an adapter-configurable ceiling: a number discovered only after
    writing long is the wasted draft the field exists to end, so this must never report
    a ceiling the gate does not enforce.

    Three outcomes, each named rather than collapsed:

    - `None` -- the validator never loaded (a consuming repo without the repo-root
      `scripts/` tree). There is no ceiling this install can enforce, so asserting one
      would be worse than publishing none.
    - `source: resolved` -- the adapter was consulted; this IS the gate's number.
    - `source: default (adapter ceiling unresolvable)` -- the validator loaded but its
      resolver could not be reached (a cross-tree version skew). Said, not swallowed:
      returning the default silently would hand a repo that declared 300 a forecast of
      the shipped default with nothing red, re-entering the exact defect the field closes.
    """
    if validator is None or default is None:
        return None
    try:
        cap = validator.resolve_adapter_line_budget(
            lambda _repo_root: adapter,
            Path("."),
            field=validator.WORD_BUDGET_FIELD,
            default=default,
        )
        source = "resolved"
    except Exception:
        cap, source = default, "default (adapter ceiling unresolvable)"
    return {"max_words": cap, "source": source, "guidance": guidance}
