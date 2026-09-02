#!/usr/bin/env python3

"""Replay the declarations a probe record's `## Stimulus` writes, and refuse the inert ones.

`probe_record_lib`'s blind class opens with "It never RUNS anything. It reads captured
observables." This module is that bullet's narrow repair, and it is narrow on purpose --
read `WHAT THIS REPLAYS AND WHAT IT DOES NOT` below before assuming it covers more.

THE DEFECT CLASS, measured rather than imagined (#674). Slice 5 of the probe-provenance
goal published thirteen probe records. FIVE shipped a `## Polarity controls` arm that could
not fail -- six arms in all, since the quality record shipped two: the stimulus declared a
field in a shape the owning reader does not honor, the declaration was inert, and the
speakable-version control reproduced the base observable. Four of the five were found by
hand, tracing the record's own stimulus through this repo's own reader (`adapter_lib` for
the flow-sequence cases, the owning resolver's field list and validators for the rest);
the fifth is the one this module found on its first sweep. Across every review round slice
5 paid for, no gate saw any of it.

The mechanized form of that hand-trace is a LEAVE-ONE-OUT ABLATION, PER DECLARATION LINE.
Take each adapter document the stimulus writes, make its `version` speakable, and resolve
it through the owning skill's real `resolve_adapter.py` three ways: whole, with one
declaration deleted, and with that declaration's value varied. A payload identical under
BOTH deletion and variation means no reader reads that key at all -- so the arm the record
contrasts against it was never live, whatever the record says it observed. Identical under
deletion but not variation means the declared value merely restates the reader's own
default, which is reported and not refused.

Per LINE rather than per top-level key because a round-1 review defeated the key version:
each measured dead declaration happened to be the sole entry under its key, so the key
collapsed to its default and a top-level ablation saw it. Append `id: probe-one` -- the
original defect key -- to the CORRECTED quality probe and the parent stays live while the
control still cannot fail.

WHAT THIS REPLAYS AND WHAT IT DOES NOT.

- It replays the ADAPTER-WRITING half of the stimulus: the `cat > ... -adapter.yaml <<'X'`
  heredocs, through the real resolver. It does NOT run the CLI invocations underneath them
  and does NOT diff their output against `## Base observable` / `## Head observable`.
- That omission is a decision with a measured reason, not an oversight. A whole-output diff
  is defeated by the PARTIAL dead control, which is the shape this corpus actually produced:
  the quality record's dead control flipped three of its five CLIs, reproduced the base
  observable byte-for-byte on one and the base's WEAK verdict on another, so the runs
  differ and a whole-output comparison passes it. It is defeated a second time by volatile
  bytes (timings, pids, temp paths) in the accepting direction. And it would mean executing
  a record's own shell at a proof surface. The ablation needs no shell and catches every
  arm in the regression corpus beside `tests/test_probe_stimulus_replay.py` -- five of the
  six measured arms, including the record no review round found. The quality record's FIRST
  generation is not reproduced there and no claim is made about it.
- So the recorded observables are NOT verified here at all. A record whose captured
  observables were transcribed rather than measured passes this module exactly as it passes
  `probe_record_lib`. The distinct observer remains the countermeasure for that.

BLIND CLASS -- what this mechanism CANNOT see. Written before the first acceptance test,
because the last detector this repo shipped took three review rounds to surface that it
could not see any renderer. Round 1 rewrote this list after defeating three of its bullets.

- A stimulus that writes NO adapter document resolves `not-configured` and is not refused.
  This corpus is entirely adapter probes, so coverage is total today and would be zero for a
  probe of anything else. Moving the declaration out of a `cat` heredoc -- to `printf`, to
  `tee`, to a fixture file the stimulus copies -- is an escape hatch this cannot close.
  Four MORE heredoc spellings are read than were (quoted paths, `<<-`, hyphenated
  delimiters, trailing comments) and that is four, not a closed class: a redirect written
  after the heredoc, a `$ ` transcript prompt, a trailing `&& echo ok`, a backslash-quoted
  delimiter, a path
  containing a space and `cat >>` all still fail the regex. Widening again only moves the
  boundary, so the BOUNDARY reports -- an unmatched `cat` line that names an adapter
  document is refused, as is an adapter-shaped target that resolves to no reader
  (`${s}-adapter.yaml`, `.yml`, `Quality-Adapter.YAML`). A silent drop renders
  `not-configured`, which does not demote, so every miss that stays silent is an escape.
- IT MEASURES WHETHER THE RESOLVER HONORS A DECLARATION, NOT WHETHER ANY CONSUMER READS IT,
  and that gap admits a real defect rather than merely limiting coverage. A field that
  passes arbitrary nested keys through into `data:` verbatim -- `adapter_validators`
  `command_timing_log` returns `dict(value)`, and `host_extensions` exists to carry keys
  charness does not read -- makes an unread key CHANGE the payload when ablated, so it
  reads live and the record passes. Reproduced: `command_timing_log` with an extra
  `probe_one: x` resolves `evaluated`. The converse (a key the resolver drops being
  called inert when a direct file reader uses it) is the same gap from the other side and
  equally unclosed.
- The ablation compares the resolver's `data:` block only, so it also drops `valid:`,
  `found:`, `errors:`, `warnings:` and every derived top-level key a resolver renders beside
  the payload. A declaration whose only honest effect is one of those -- the broken
  `startup_probes` case reports five errors and still resolves `startup_probes: []` -- is
  called inert. That is right for this corpus, whose consumers act on `data`; a declaration
  that legitimately only produced an error would be called inert wrongly.
- The VARIANT cannot preserve an ENUM. Booleans, integers, floats and quoted scalars vary
  within their own type now, but a field the reader constrains to a member set has no
  type-preserving variant this module can compute. No enum field in today's corpus has a
  DEFAULT -- absence is an error -- so the ablation moves the payload and returns live
  before any variant runs; a future enum field WITH a default would be refused wrongly.
- Sandbox REUSE between a document's runs is load-bearing, not tidiness. Mutating it to a
  fresh temp dir per resolve was measured: the announcement and release payloads render the
  repo directory's own name inside `data:` (`product_name`, `repo`, `package_id`), so two
  of the six dead controls in the regression corpus stopped being detectable at all.
- Two heredocs writing the SAME filename are replayed independently, each in its own
  sandbox. If a stimulus overwrites its own adapter, the superseded first write -- which
  never existed on disk when the CLI ran -- is still resolved and can be refused. That is
  the refusing direction, so it cannot hide a defect; it can still be a wrong answer about
  what the record ran.
- `with_mutated_value` splits a line on its first raw `:`, while `adapter_lib` finds the
  separator quote-aware. For a quoted key containing a colon the emitted variant declares a
  different KEY, so it is not guaranteed to be "the same declaration with a different
  value" -- the property the whole discriminator rests on. No corpus case reaches it.
- It checks WHERE the document was written only against `.agents/`, the one directory every
  adapter reader in this repo opens. A stimulus writing to five different repo roots is
  checked per basename, so a copy-paste slip BETWEEN two of those roots -- writing the retro
  document under the quality root -- is invisible.
- It knows nothing about whether the declared keys are the RIGHT keys for the claim, nor
  whether the record's prose describes what was measured. Those stay rung-2 judgment.
"""

from __future__ import annotations

import sys
import tempfile
from functools import lru_cache
from pathlib import Path

from runtime_bootstrap import import_repo_module
from scripts.subprocess_guard import run_process

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
_documents = import_repo_module(__file__, "scripts.probe_stimulus_documents")

# Re-exported so the split stays an implementation detail: `probe_stimulus_replay` remains
# the one import site for anything that replays a stimulus.
extract_adapter_documents = _documents.extract_adapter_documents
declaration_lines = _documents.declaration_lines
uninterpreted_lines = _documents.uninterpreted_lines
with_supported_version = _documents.with_supported_version
with_mutated_value = _documents.with_mutated_value
without_line = _documents.without_line
_indent_of = _documents._indent_of
_SKILL_NAME_RE = _documents._SKILL_NAME_RE
_ADAPTER_DIRECTORY = _documents._ADAPTER_DIRECTORY
_UNREAD = _documents._UNREAD
_RESTATED_DEFAULT = _documents._RESTATED_DEFAULT

# Borrowed from the same vocabulary `probe_record_lib` borrows, for the same reason: a
# fourth private spelling of "we could not tell" is how the concept drifts apart.
_boundary_probe = import_repo_module(__file__, "scripts.boundary_probe_lib")
STIMULUS_EVALUATED = _boundary_probe.PROBE_EVALUATED
STIMULUS_NOT_CONFIGURED = _boundary_probe.PROBE_NOT_CONFIGURED
STIMULUS_NOT_ESTABLISHED = _boundary_probe.PROBE_NOT_ESTABLISHED

_RESOLVE_TIMEOUT_SECONDS = 120


@lru_cache(maxsize=None)
def _resolver_loader(resolver: str):
    """Load one resolver's pure adapter function once for this replay process."""
    import runpy

    namespace = runpy.run_path(resolver)
    loader = namespace.get("load_adapter")
    if callable(loader):
        return loader
    policy = namespace.get("adapter_policy")
    loader = getattr(policy, "load_adapter", None)
    if callable(loader):
        return loader
    raise AttributeError(f"resolver {resolver} does not expose a load_adapter callable")


def _resolver_for(repo_root: Path, skill: str) -> Path | None:
    if not _SKILL_NAME_RE.match(skill):
        return None
    candidate = repo_root / "skills" / "public" / skill / "scripts" / "resolve_adapter.py"
    return candidate if candidate.is_file() else None


def _resolve(repo_root: Path, resolver: Path, sandbox: Path, filename: str, text: str) -> dict:
    """Resolve one document in-process and return its structured adapter output.

    The sandbox is REUSED between the whole and ablated runs of a document, so the resolved
    payload cannot differ merely because the temp path differed -- which would make every
    ablation look like a live declaration and silently disarm the whole check.
    """
    agents = sandbox / ".agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / filename).write_text(text, encoding="utf-8")
    try:
        payload = _resolver_loader(str(resolver))(sandbox)
    except Exception as exc:  # pragma: no cover - resolver absent or broken
        return {"data": None, "output": f"the resolver could not be run: {exc}", "exit_code": None}
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
        return {"data": None, "output": repr(payload), "exit_code": None}
    return {
        "data": payload["data"],
        "output": repr(payload),
        "exit_code": 0 if payload.get("valid") is not False else 1,
    }


def _resolve_process(
    repo_root: Path, resolver: Path, sandbox: Path, filename: str, text: str
) -> dict:
    """Run one resolver entrypoint as a process for delivery-boundary smoke tests."""
    agents = sandbox / ".agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / filename).write_text(text, encoding="utf-8")
    try:
        done = run_process(
            [sys.executable, str(resolver), "--repo-root", str(sandbox)],
            cwd=repo_root,
            timeout_seconds=_RESOLVE_TIMEOUT_SECONDS,
        )
    except OSError as exc:  # pragma: no cover - resolver absent
        return {"data": None, "output": f"the resolver could not be run: {exc}", "exit_code": None}
    output = done.stdout + done.stderr
    return {
        "data": _data_block(output),
        "output": output,
        "exit_code": None if done.returncode == 124 else done.returncode,
    }


def _data_block(output: str) -> str | None:
    """The resolver's `data:` mapping, verbatim, or None when it rendered none.

    Compared as TEXT rather than as a parsed structure so this module needs no YAML reader
    of its own -- and so a resolver that renders a payload this repo's loader could not read
    back is compared as what the operator actually sees.
    """
    lines = output.splitlines()
    for index, line in enumerate(lines):
        if line.rstrip() != "data:":
            continue
        block = [line]
        for candidate in lines[index + 1 :]:
            if candidate.strip() and not candidate[:1].isspace():
                break
            block.append(candidate.rstrip())
        return "\n".join(block)
    return None


def _shape_refusal(document: dict) -> str | None:
    """The reason this document cannot be replayed AT ALL, read without running anything.

    Split from `_inspect_document` so the "can this be replayed" question and the "what did
    the replay find" question are answered in separate places -- each of these four is a
    terminal verdict about the STIMULUS, and interleaving them with the ablation put the
    whole thing over the complexity bar with the two concerns tangled.
    """
    filename = document["filename"]
    if document.get("unreadable_command"):
        return (
            f"the stimulus line `{filename}` names an adapter document in a shell form this "
            "module cannot read, so what it writes is unknown. Refusing rather than dropping "
            "it: a dropped document renders `not-configured`, which does not demote. Write it "
            "as `cat > <path>/<skill>-adapter.yaml <<'DELIM'`"
        )
    if document["skill"] is None:
        return (
            f"the stimulus writes `{filename}`, which reads as an adapter document and is not "
            "a name any reader in this repo opens. Every resolver opens exactly "
            f"`{_ADAPTER_DIRECTORY}/<skill>-adapter.yaml`, lowercase, literal, no shell "
            "expansion and no `.yml`. Write that name"
        )
    if document["directory"] != _ADAPTER_DIRECTORY:
        # A run in which the document was written where no reader looks is a run in which
        # NOTHING was read. Replaying its declarations from `.agents/` -- the only path any
        # resolver in this repo opens -- would report them live and pass the record, which
        # is the module manufacturing the very contrast the record failed to produce.
        return (
            f"the stimulus writes `{filename}` into `{document['directory'] or '.'}/`, and every "
            f"adapter reader in this repo opens `{_ADAPTER_DIRECTORY}/` only. Nothing read this "
            "document, so no arm contrasted against it was live"
        )
    try:
        uninterpreted_lines(document["text"])
    except ValueError as exc:
        # A construct this repo's reader REFUSES outright (`version: !!int 9` and friends).
        # It has to be a verdict here, not a raise: `adapter_lib` throws from the shared
        # parser, so a checker that let it out would traceback on exactly the input class
        # `#673` is filed about -- the defect shape, reproduced inside the detector for it.
        return (
            f"the `{filename}` document the stimulus writes is one this repo's own reader "
            f"refuses outright ({_adapter_lib.parse_failure_error(exc)}), so nothing in it "
            "reaches any consumer and no arm contrasted against it was live"
        )
    if not declaration_lines(with_supported_version(document["text"])):
        # The maximal form of the defect class, and one line long. A document declaring
        # nothing but a version leaves the speakable control resolving charness defaults --
        # byte-identical to the base observable every record in this corpus contrasts
        # against. Reporting `evaluated` for it is the silent pass this module refuses.
        return (
            f"the `{filename}` document declares nothing but a version, so the speakable "
            "control contrasts against the reader's own defaults and cannot fail"
        )
    return None


def _inspect_document(repo_root: Path, document: dict) -> dict:
    """One document's replay report: reasons that refuse it, plus what was observed."""
    reasons: list[str] = []
    filename = document["filename"]
    report: dict = {"document": filename, "skill": document["skill"], "inert_declarations": []}
    if refusal := _shape_refusal(document):
        report["reasons"] = [refusal]
        return report
    if document["expanded"]:
        reasons.append(
            f"the `{filename}` heredoc uses an UNQUOTED delimiter, so the shell expands the "
            "body before it reaches disk; the document a reader replays is not the document "
            "printed in the record. Quote the delimiter"
        )
    speakable = with_supported_version(document["text"])
    # The SPEAKABLE text, not the raw one: the ablation resolves the speakable form, so
    # reading dropped lines from the raw text let the two disagree -- `version: >` folds
    # its following lines into a block scalar, `version: 1` leaves them over-indented and
    # dropped. The ablation still failed closed; the operator was told the wrong reason.
    if dropped := uninterpreted_lines(speakable):
        reasons.append(
            f"the `{filename}` document the stimulus writes has lines this repo's own reader "
            f"does not interpret, so the stimulus declares less than it appears to: {'; '.join(dropped)}"
        )
    resolver = _resolver_for(repo_root, document["skill"])
    if resolver is None:
        reasons.append(
            f"`{filename}` names no public resolver (`skills/public/{document['skill']}/scripts/"
            "resolve_adapter.py` does not exist), so the stimulus cannot be replayed as written. "
            "A templated placeholder is not a reproduction step; write the document out per skill"
        )
        report["reasons"] = reasons
        return report

    with tempfile.TemporaryDirectory(prefix="probe-stimulus-") as scratch:
        sandbox = Path(scratch)
        whole = _resolve(repo_root, resolver, sandbox, filename, speakable)
        if whole["data"] is None:
            reasons.append(
                f"resolving `{filename}` at a speakable version rendered no `data:` payload, so "
                f"no declaration in it can be replayed: {_last_line(whole['output'])}"
            )
            report["reasons"] = reasons
            return report
        inert: list[str] = []
        restated_defaults: list[str] = []
        for declaration in declaration_lines(speakable):
            label = declaration["label"]
            verdict, reason = _declaration_verdict(
                repo_root, resolver, sandbox, filename, speakable, declaration, whole["data"]
            )
            if reason:
                reasons.append(f"in `{filename}`, {reason}")
            if verdict == _UNREAD:
                inert.append(label)
            elif verdict == _RESTATED_DEFAULT:
                restated_defaults.append(label)
    report["inert_declarations"] = inert
    report["restated_defaults"] = restated_defaults
    if inert:
        reasons.append(
            f"in `{filename}`, no value of {', '.join(f'`{label}`' for label in inert)} changes "
            "ANYTHING the resolver honors at a speakable version -- deleting it and varying it "
            "both leave the payload identical, so the reader does not read it and the polarity "
            "control this record contrasts against declared nothing live"
        )
    report["reasons"] = reasons
    return report


def _declaration_verdict(
    repo_root: Path,
    resolver: Path,
    sandbox: Path,
    filename: str,
    speakable: str,
    declaration: dict,
    whole: object,
) -> tuple[str | None, str | None]:
    """``(verdict, reason)`` for ONE declaration: is it read, unread, or a restated default?

    Two resolves, and both fail CLOSED. A resolve that produced no payload is unequal to
    `whole`, which reads as "this declaration is live" -- so a resolver that timed out or
    could not start turned a refusal into a pass, silently and nondeterministically. An
    untested declaration is untested, and says so.
    """
    label = declaration["label"]
    ablated = _resolve(
        repo_root, resolver, sandbox, filename, without_line(speakable, declaration["index"])
    )
    if ablated["data"] is None:
        return None, (
            f"the ablated resolve of `{label}` produced no payload, so that declaration was "
            f"never tested: {_last_line(ablated['output'])}"
        )
    if ablated["data"] != whole:
        return None, None
    variant = with_mutated_value(speakable, declaration["index"])
    if variant is None:
        # A line owning no scalar to vary is a block parent whose WHOLE block deleted
        # without effect, which is already the unread verdict -- no variant is owed.
        return _UNREAD, None
    varied = _resolve(repo_root, resolver, sandbox, filename, variant)
    if varied["data"] is None:
        return None, (
            f"the varied resolve of `{label}` produced no payload, so whether the reader reads "
            f"that key at all was never settled: {_last_line(varied['output'])}"
        )
    return (_UNREAD if varied["data"] == whole else _RESTATED_DEFAULT), None


def _last_line(output: str) -> str:
    return output.strip().splitlines()[-1] if output.strip() else "no output"


def replay_probe_stimulus(record: dict, *, repo_root: Path) -> dict:
    """Replay every adapter document the record's `## Stimulus` writes.

    ``state`` is `not-configured` when the stimulus writes no adapter document -- this
    module genuinely has no question to answer there, and saying `evaluated` would be the
    silent-pass shape the whole probe-record vocabulary exists to refuse.
    """
    stimulus = (record.get("sections") or {}).get("stimulus") or ""
    if not stimulus.strip():
        return _report(
            STIMULUS_NOT_CONFIGURED, ["the record carries no `## Stimulus` block to replay"], []
        )
    documents = extract_adapter_documents(stimulus)
    if not documents:
        return _report(
            STIMULUS_NOT_CONFIGURED,
            [
                "the `## Stimulus` writes no `*-adapter.yaml` heredoc, so this module has nothing "
                "to replay; it checks adapter declarations and nothing else"
            ],
            [],
        )
    reports = [_inspect_document(repo_root, document) for document in documents]
    reasons = [reason for report in reports for reason in report["reasons"]]
    state = STIMULUS_NOT_ESTABLISHED if reasons else STIMULUS_EVALUATED
    return _report(state, reasons, reports)


def _report(state: str, reasons: list[str], documents: list[dict]) -> dict:
    """Every return built once, so no branch can omit a key a consumer branches on."""
    return {
        "state": state,
        "reasons": list(reasons),
        "documents": list(documents),
    }
