#!/usr/bin/env python3

"""Replay the declarations a probe record's `## Stimulus` writes, and refuse the inert ones.

`probe_record_lib`'s blind class opens with "It never RUNS anything. It reads captured
observables." This module is that bullet's narrow repair, and it is narrow on purpose --
read `WHAT THIS REPLAYS AND WHAT IT DOES NOT` below before assuming it covers more.

THE DEFECT CLASS, measured rather than imagined (#674). Slice 5 of the probe-provenance
goal published thirteen probe records. FOUR shipped a `## Polarity controls` arm that could
not fail: the stimulus declared a field in a shape the owning reader does not honor, the
declaration was inert, and the speakable-version control reproduced the base observable.
Every one was found by a bounded reviewer hand-tracing the record's own stimulus through
this repo's own reader -- `adapter_lib` for the two flow-sequence cases, the owning
resolver's field list and validators for the other two. Thirteen review rounds; no gate.

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
  measured instance, including a fifth the review rounds did not find.
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
  What it DOES now close is spelling the same heredoc differently: quoted paths, `<<-`,
  hyphenated delimiters and trailing comments are read, and an adapter-shaped target it
  cannot resolve (`${s}-adapter.yaml`, a `.yml` no reader opens) is REFUSED rather than
  dropped, because a silent drop renders `not-configured`, which does not demote.
- The ablation compares the resolver's `data:` block only, so it also drops `valid:`,
  `found:`, `errors:`, `warnings:` and every derived top-level key a resolver renders beside
  the payload. A declaration whose only honest effect is one of those -- the broken
  `startup_probes` case reports five errors and still resolves `startup_probes: []` -- is
  called inert. That is right for this corpus, whose consumers act on `data`; a declaration
  that legitimately only produced an error would be called inert wrongly.
- The ablation is over the RESOLVER's rendered payload, which is what every consumer in
  this repo acts on. A consumer that read the adapter file directly instead would be
  invisible here -- and one that reached a key the resolver drops would be called inert
  when it is live. No such consumer exists today; the census is what watches for one.
- Sandbox REUSE between a document's runs is load-bearing, not tidiness. Mutating it to a
  fresh temp dir per resolve was measured: the announcement and release payloads render the
  repo directory's own name inside `data:` (`product_name`, `repo`, `package_id`), so two
  of the five dead controls stopped being detectable at all.
- It checks WHERE the document was written only against `.agents/`, the one directory every
  adapter reader in this repo opens. A stimulus writing to five different repo roots is
  checked per basename, so a copy-paste slip BETWEEN two of those roots -- writing the retro
  document under the quality root -- is invisible.
- It knows nothing about whether the declared keys are the RIGHT keys for the claim, nor
  whether the record's prose describes what was measured. Those stay rung-2 judgment.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from runtime_bootstrap import import_repo_module

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")

# Borrowed from the same vocabulary `probe_record_lib` borrows, for the same reason: a
# fourth private spelling of "we could not tell" is how the concept drifts apart.
_boundary_probe = import_repo_module(__file__, "scripts.boundary_probe_lib")
STIMULUS_EVALUATED = _boundary_probe.PROBE_EVALUATED
STIMULUS_NOT_CONFIGURED = _boundary_probe.PROBE_NOT_CONFIGURED
STIMULUS_NOT_ESTABLISHED = _boundary_probe.PROBE_NOT_ESTABLISHED

# `cat > <path> <<'DELIM'`. Deliberately WIDE, because a heredoc this regex misses is
# dropped silently and the record then renders `not-configured`, which does not demote --
# so every shape it fails to match is an escape hatch, and a round-1 review enumerated six
# of them. Quoted and unquoted paths, `<<-`, hyphenated delimiters and a trailing comment
# are all accepted now. The quote around the DELIMITER stays significant: unquoted means
# the shell expands the body, so the document on disk is not the document in the record.
_HEREDOC_RE = re.compile(
    r"""^\s*cat\s*>\s*(?P<pathquote>['"]?)(?P<path>[^'"\s]+)(?P=pathquote)\s*"""
    r"""<<-?\s*(?P<quote>['"]?)(?P<delim>[\w-]+)(?P=quote)\s*(?:\#.*)?$"""
)
# `.yaml` ONLY, matching what every reader in this repo opens. Accepting `.yml` here made a
# spelling no resolver reads resolve anyway, and it was refused only by the accident that
# the sandbox then found no file and every declaration read inert -- a right answer with a
# reason that names the wrong defect.
_ADAPTER_NAME_RE = re.compile(r"^(?P<skill>[A-Za-z0-9_-]+)-adapter\.yaml$")
# A heredoc target that LOOKS like an adapter but does not resolve to one. Matched so the
# miss becomes a refusal instead of a silent drop: `${s}-adapter.yaml`, `<skill>-adapter.yaml`
# and `quality-adapter.yml` all reach a reader in the record's prose and none reaches one here.
_ADAPTER_ISH_RE = re.compile(r"adapter\.ya?ml|adapter\.yml", re.IGNORECASE)
# A skill directory name. Template placeholders and shell expansions fail this deliberately:
# a stimulus nobody can paste is not a reproduction step, which is the whole subject of #674.
_SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_VERSION_LINE_RE = re.compile(r"^version\s*:.*$", re.MULTILINE)
# The ONE directory every adapter reader in this repo looks in. Checked because the module
# writes the document to `.agents/<basename>` in its sandbox, so a stimulus that wrote it
# anywhere else describes a run where NOTHING was read -- and replaying it at the readable
# path would report the declarations live and pass the record.
_ADAPTER_DIRECTORY = ".agents"
_COMMENT_LINE_RE = re.compile(r"^\s*#")
_RESOLVE_TIMEOUT_SECONDS = 120


def extract_adapter_documents(stimulus: str) -> list[dict]:
    """Every adapter document the stimulus block writes, in order.

    Returns ``{"filename", "skill", "text", "expanded"}`` per document. Parsing the shell
    rather than executing it is the point: the record's readers are humans and this module,
    and neither should have to run an arbitrary script to learn what the stimulus declares.
    """
    documents: list[dict] = []
    lines = stimulus.splitlines()
    index = 0
    while index < len(lines):
        match = _HEREDOC_RE.match(lines[index])
        if match is None:
            index += 1
            continue
        delimiter = match.group("delim")
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != delimiter:
            body.append(lines[index])
            index += 1
        index += 1
        written_to = PurePosixPath(match.group("path"))
        filename = written_to.name
        name_match = _ADAPTER_NAME_RE.match(filename)
        if name_match is None:
            # A target that looks like an adapter but does not resolve to one is REPORTED,
            # not dropped. Dropping it renders `not-configured`, which does not demote the
            # record -- so silence here is the cheapest escape in the whole module.
            if _ADAPTER_ISH_RE.search(filename):
                documents.append({"filename": filename, "skill": None, "text": "", "expanded": False, "directory": written_to.parent.name})
            continue
        documents.append(
            {
                "filename": filename,
                "skill": name_match.group("skill"),
                "text": "\n".join(body) + "\n",
                # An unquoted heredoc delimiter lets the shell expand `$VAR` and backticks
                # in the body, so what lands on disk is not what the record shows.
                "expanded": match.group("quote") == "",
                # The DIRECTORY the stimulus wrote to, which decides whether any reader saw
                # the document at all. This module resolves from `.agents/`, so without this
                # a stimulus that wrote elsewhere -- a run in which nothing was read --
                # would have its declarations replayed at the one path that does read them.
                "directory": written_to.parent.name,
            }
        )
    return documents


def declaration_lines(text: str) -> list[dict]:
    """Every line of the document that DECLARES something, with its own indent.

    PER LINE, not per top-level key, and a round-1 bounded review is why. Ablating only
    the outer mapping's keys worked on the four measured records by accident of their
    content: each dead declaration happened to be the sole entry under its key, so the key
    collapsed to its default and the ablation saw it. Add one honest sibling and the dead
    one disappears -- appending `id: probe-one` (the ORIGINAL defect key) to the corrected
    quality probe leaves `startup_probes` live, so the top-level ablation reports the
    document clean while the record's control still cannot fail. The reviewer built that
    input; per-line ablation is the answer to it.

    The version line is excluded because `with_supported_version` already owns it: it is
    the arm being controlled FOR, not a declaration under test. Comments and blank lines
    declare nothing.
    """
    declarations: list[dict] = []
    for index, line in enumerate(text.splitlines()):
        if not line.strip() or _COMMENT_LINE_RE.match(line) or _VERSION_LINE_RE.match(line):
            continue
        declarations.append({"index": index, "indent": _indent_of(line), "label": line.strip()})
    return declarations


def _indent_of(line: str) -> int:
    """Indent width in SPACES ONLY, matching `adapter_lib._line_shape`.

    Not `str.isspace()`. A tab-led line is a top-level key to this repo's parser and an
    indented continuation to anything that asks `isspace()`, so the two disagreed about
    what a block contains -- which made an honestly declared tab-indented key read as
    inert, a false refusal on a proof surface.
    """
    return len(line) - len(line.lstrip(" "))


def uninterpreted_lines(text: str) -> list[str]:
    """The operator-facing warning for every line the reader could not interpret."""
    _parsed, sink = _adapter_lib.load_yaml_report(text)
    return _adapter_lib.uninterpreted_warnings(sink)


def with_supported_version(text: str) -> str:
    """The same document with its `version` made speakable, so the control arm can run.

    A document that declares no version is returned unchanged: there is nothing to make
    speakable, and inventing one would resolve a document the record never wrote.
    """
    return _VERSION_LINE_RE.sub(
        f"version: {_adapter_lib.SUPPORTED_ADAPTER_VERSION}", text, count=1
    )


_MUTATION_TOKEN = "probe-mutation"
_NUMERIC_RE = re.compile(r"-?\d+")
# The two reasons a deletion can come back unchanged, kept as distinct words because only
# one of them is a defect. `_UNREAD` refuses; `_RESTATED_DEFAULT` is reported.
_UNREAD = "unread"
_RESTATED_DEFAULT = "restated-default"


def with_mutated_value(text: str, index: int) -> str | None:
    """The document with one declaration's VALUE varied, or None when it owns no scalar.

    This is the discriminator between the two reasons an ablation can come back unchanged,
    and per-line ablation needs it or it refuses honest records. `exemption_globs: []` in
    the prompt-bulk record deletes without effect because the declared value IS the
    reader's default -- a no-op restatement, not a wrong shape. `id: probe-one` deletes
    without effect because no reader reads the key at all. Varying the value separates
    them: the first changes the payload, the second cannot.
    """
    lines = text.splitlines()
    line = lines[index]
    head, separator, value = line.partition(":")
    if not separator:
        stripped = line.strip()
        if not stripped.startswith("- "):
            return None
        return "\n".join(
            lines[:index] + [f"{line.rstrip()}-{_MUTATION_TOKEN}"] + lines[index + 1 :]
        ) + "\n"
    value = value.strip()
    if not value:
        # A block parent owns no scalar to vary. Its liveness is decided by its children,
        # and if deleting the whole block changed nothing then nothing under it was read --
        # which is the unread verdict, reached without needing a variant.
        return None
    return "\n".join(lines[:index] + _mutated_lines(head, value) + lines[index + 1 :]) + "\n"


def _mutated_lines(head: str, value: str) -> list[str]:
    """The declaration re-stated with a different value, IN A SHAPE THIS READER PARSES.

    The first cut varied `[]` to the flow sequence `["probe-mutation"]` and measured
    nothing: `adapter_lib._mapping_value` renders a flow sequence as a plain string, the
    validator drops it, and the varied payload came back identical to the whole one -- so
    every empty-list declaration was reported UNREAD when it was merely restating a
    default. The discriminator emitted the exact malformed shape it exists to detect,
    which is this corpus's own defect class reproduced one level up, again.
    """
    indent = " " * (_indent_of(head) + 2)
    if value == "[]":
        return [f"{head}:", f"{indent}- {_MUTATION_TOKEN}"]
    if value == "{}":
        return [f"{head}:", f"{indent}{_MUTATION_TOKEN}: 1"]
    if _NUMERIC_RE.fullmatch(value):
        return [f"{head}: {int(value) + 1}"]
    return [f"{head}: {value}-{_MUTATION_TOKEN}"]


def without_line(text: str, index: int) -> str:
    """The document with one declaration line, and everything nested under it, removed.

    Text-level rather than parse-and-re-render, because re-rendering would silently repair
    exactly the malformed shapes this module exists to detect -- a flow sequence would come
    back as a block sequence and the inert declaration would resolve as honored.
    """
    lines = text.splitlines()
    indent = _indent_of(lines[index])
    end = index + 1
    while end < len(lines) and (not lines[end].strip() or _indent_of(lines[end]) > indent):
        end += 1
    return "\n".join(lines[:index] + lines[end:]) + "\n"


def _resolver_for(repo_root: Path, skill: str) -> Path | None:
    if not _SKILL_NAME_RE.match(skill):
        return None
    candidate = repo_root / "skills" / "public" / skill / "scripts" / "resolve_adapter.py"
    return candidate if candidate.is_file() else None


def _resolve(repo_root: Path, resolver: Path, sandbox: Path, filename: str, text: str) -> dict:
    """Run one real resolver over one document and return its rendered output.

    The sandbox is REUSED between the whole and ablated runs of a document, so the resolved
    payload cannot differ merely because the temp path differed -- which would make every
    ablation look like a live declaration and silently disarm the whole check.
    """
    agents = sandbox / ".agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / filename).write_text(text, encoding="utf-8")
    try:
        done = subprocess.run(
            [sys.executable, str(resolver), "--repo-root", str(sandbox)],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=_RESOLVE_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - resolver absent
        return {"data": None, "output": f"the resolver could not be run: {exc}", "exit_code": None}
    return {"data": _data_block(done.stdout), "output": done.stdout, "exit_code": done.returncode}


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
    if document["skill"] is None:
        return (
            f"the stimulus writes `{filename}`, which reads as an adapter document and is not "
            "one this module can resolve -- a shell-expanded name, a placeholder, or a "
            "`.yml` spelling no reader opens. Write the literal `<skill>-adapter.yaml` name"
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
    if dropped := uninterpreted_lines(document["text"]):
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

    speakable = with_supported_version(document["text"])
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
    repo_root: Path, resolver: Path, sandbox: Path, filename: str,
    speakable: str, declaration: dict, whole: str,
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
        return _report(STIMULUS_NOT_CONFIGURED, ["the record carries no `## Stimulus` block to replay"], [])
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
