#!/usr/bin/env python3

"""Replay the declarations a probe record's `## Stimulus` writes, and refuse the inert ones.

`probe_record_lib`'s blind class opens with "It never RUNS anything. It reads captured
observables." This module is that bullet's narrow repair, and it is narrow on purpose --
read `WHAT THIS REPLAYS AND WHAT IT DOES NOT` below before assuming it covers more.

THE DEFECT CLASS, measured rather than imagined (#674). Slice 5 of the probe-provenance
goal published ten probe records. FOUR shipped a `## Polarity controls` arm that could not
fail: the stimulus declared a field in a shape this repo's own reader does not honor, the
declaration was inert, and the speakable-version control reproduced the base observable.
Every one was found by a bounded reviewer hand-tracing the record's own stimulus through
`scripts/adapter_lib.py`. Thirteen review rounds; no gate saw any of it.

The mechanized form of that hand-trace is a LEAVE-ONE-OUT ABLATION. Take each adapter
document the stimulus writes, make its `version` speakable, and resolve it twice through
the owning skill's real `resolve_adapter.py`: once whole, once with one declared key
deleted. If the resolved payload is byte-identical either way, that key declared NOTHING the
reader honors -- so the arm the record contrasts against it was never live, whatever the
record says it observed. That is the polarity control, per declaration, run by a machine.

WHAT THIS REPLAYS AND WHAT IT DOES NOT.

- It replays the ADAPTER-WRITING half of the stimulus: the `cat > ... -adapter.yaml <<'X'`
  heredocs, through the real resolver. It does NOT run the CLI invocations underneath them
  and does NOT diff their output against `## Base observable` / `## Head observable`.
- That omission is a decision with a measured reason, not an oversight. A whole-output diff
  is defeated by the PARTIAL dead control, which is the shape this corpus actually produced:
  the quality record's dead control flipped three of its five CLIs and reproduced the base
  observable on the other two, so the runs differ and a whole-output comparison passes it.
  It is defeated a second time by volatile bytes (timings, pids, temp paths) in the
  accepting direction. And it would mean executing a record's own shell at a proof surface.
  The ablation is deterministic, needs no shell, and catches all four measured instances.
- So the recorded observables are NOT verified here at all. A record whose captured
  observables were transcribed rather than measured passes this module exactly as it passes
  `probe_record_lib`. The distinct observer remains the countermeasure for that.

BLIND CLASS -- what this mechanism CANNOT see. Written before the first acceptance test,
because the last detector this repo shipped took three review rounds to surface that it
could not see any renderer.

- A stimulus that writes NO adapter document resolves `not-configured` and is not refused.
  This corpus is entirely adapter probes, so the coverage is total today and would be zero
  for a probe of anything else. That is also an escape hatch: move the declaration out of a
  `-adapter.yaml` heredoc and this module has nothing to say.
- The ablation compares the resolver's `data:` block only. A declaration that changes only
  `errors:` -- the broken `startup_probes` case reports five errors and still resolves
  `startup_probes: []` -- is correctly called inert, but a declaration whose ONLY honest
  effect is an error would be called inert too, wrongly. No such declaration exists in this
  corpus; one could.
- A key whose declared value EQUALS the reader's inferred default is reported inert. That
  is deliberate and it is the scaffold record's own stated requirement ("a value that
  differs from the reader's default, so `honored` and `fell back` are distinguishable"),
  but it means this module cannot distinguish "the reader ignores this field" from "the
  author picked an indistinguishable value". Both are dead controls; the remedy differs.
- The ablation is over the RESOLVER's rendered payload, which is what every consumer in
  this repo acts on. A consumer that read the adapter file directly instead would be
  invisible here -- and one that reached a key the resolver drops would be called inert
  when it is live. No such consumer exists today; the census is what watches for one.
- Sandbox REUSE between a document's whole and ablated runs is load-bearing, not tidiness.
  Mutating it to a fresh temp dir per resolve was measured: the announcement and release
  payloads embed their repo path, so two of the five dead controls stopped being detectable
  at all. `test_the_document_is_ablated_as_text...`'s sibling mutation record in the slice
  log holds the reading.
- It knows nothing about whether the declared keys are the RIGHT keys for the claim, nor
  whether the record's prose describes what was measured. Those stay rung-2 judgment.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from runtime_bootstrap import import_repo_module

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")

# Borrowed from the same vocabulary `probe_record_lib` borrows, for the same reason: a
# fourth private spelling of "we could not tell" is how the concept drifts apart.
_boundary_probe = import_repo_module(__file__, "scripts.boundary_probe_lib")
STIMULUS_EVALUATED = _boundary_probe.PROBE_EVALUATED
STIMULUS_NOT_CONFIGURED = _boundary_probe.PROBE_NOT_CONFIGURED
STIMULUS_NOT_ESTABLISHED = _boundary_probe.PROBE_NOT_ESTABLISHED

# `cat > <path> <<'DELIM'` in any of the forms this corpus writes. The quote around the
# delimiter is optional in shell and both forms appear, so it is optional here; an
# UNQUOTED delimiter means the shell would expand the body, which is a different document
# than the one this module reads, and `unexpanded_heredoc` reports that rather than
# pretending the two are the same.
_HEREDOC_RE = re.compile(r"^\s*cat\s*>\s*(?P<path>\S+)\s*<<\s*(?P<quote>['\"]?)(?P<delim>\w+)(?P=quote)\s*$")
_ADAPTER_NAME_RE = re.compile(r"^(?P<skill>[A-Za-z0-9_<>-]+)-adapter\.ya?ml$")
# A skill directory name. `<skill>` and other template placeholders fail this deliberately:
# a stimulus nobody can run verbatim is not a reproduction step, which is the whole subject
# of #674.
_SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_VERSION_LINE_RE = re.compile(r"^version\s*:.*$", re.MULTILINE)
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
        filename = Path(match.group("path")).name
        name_match = _ADAPTER_NAME_RE.match(filename)
        if name_match is None:
            continue
        documents.append(
            {
                "filename": filename,
                "skill": name_match.group("skill"),
                "text": "\n".join(body) + "\n",
                # An unquoted heredoc delimiter lets the shell expand `$VAR` and backticks
                # in the body, so what lands on disk is not what the record shows.
                "expanded": match.group("quote") == "",
            }
        )
    return documents


def top_level_keys(text: str) -> list[str]:
    """The keys the document declares, as this repo's own reader sees them."""
    parsed = _adapter_lib.load_yaml(text)
    return [str(key) for key in parsed] if isinstance(parsed, dict) else []


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


def without_key(text: str, key: str) -> str:
    """The document with one top-level key and its whole block removed.

    Text-level rather than parse-and-re-render, because re-rendering would silently repair
    exactly the malformed shapes this module exists to detect -- a flow sequence would come
    back as a block sequence and the inert declaration would resolve as honored.
    """
    opener = re.compile(rf"^{re.escape(key)}\s*:")
    kept: list[str] = []
    dropping = False
    for line in text.splitlines():
        if dropping:
            # A column-0 non-blank line ends the removed block. Blank lines inside it are
            # dropped with it, so a trailing blank cannot resurrect the next key's parent.
            if line.strip() and not line[:1].isspace():
                dropping = False
            else:
                continue
        if opener.match(line):
            dropping = True
            continue
        kept.append(line)
    return "\n".join(kept) + "\n"


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


def _inspect_document(repo_root: Path, document: dict) -> dict:
    """One document's replay report: reasons that refuse it, plus what was observed."""
    reasons: list[str] = []
    filename = document["filename"]
    report: dict = {"document": filename, "skill": document["skill"], "inert_declarations": []}
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
        as_written = _resolve(repo_root, resolver, sandbox, filename, document["text"])
        report["as_written_exit_code"] = as_written["exit_code"]
        whole = _resolve(repo_root, resolver, sandbox, filename, speakable)
        if whole["data"] is None:
            reasons.append(
                f"resolving `{filename}` at a speakable version rendered no `data:` payload, so "
                f"no declaration in it can be replayed: {whole['output'].strip().splitlines()[-1] if whole['output'].strip() else 'no output'}"
            )
            report["reasons"] = reasons
            return report
        inert: list[str] = []
        for key in top_level_keys(speakable):
            if key == "version":
                continue
            ablated = _resolve(repo_root, resolver, sandbox, filename, without_key(speakable, key))
            if ablated["data"] == whole["data"]:
                inert.append(key)
    report["inert_declarations"] = inert
    if inert:
        reasons.append(
            f"in `{filename}`, deleting {', '.join(f'`{key}`' for key in inert)} changes NOTHING the "
            f"resolver honors at a speakable version, so the polarity control this record contrasts "
            "against declared nothing live. The arm could not have failed"
        )
    report["reasons"] = reasons
    return report


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
