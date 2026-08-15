#!/usr/bin/env python3

"""Refuse an ungrounded quantity in authored release prose; flag overclaiming words.

The derived block next door proves *notes == derivation* for the surfaces
somebody registered. It cannot see a claim the author simply typed, and the
recorded false claims were exactly that: typed prose. Exempting prose from the
mechanism would exempt the surface that failed.

TWO SEVERITIES, and the split is the repair a bounded review forced. Run against
this repo's own most recently hand-audited release note, the first version of
this rule produced 49 findings — including `"...can opt into the lesson
lifecycle at all"` and `"verified only after the release has been published"`,
which is the honest-limits language the north star requires. A rule that refuses
the sentence that makes a note honest is a rule an author disables, and its
only escape hatch also disarmed the arm that works.

So:

- `bare-quantity` — a digit run or a cardinal number WORD — is BLOCKING. This is
  the recorded failure: "twelve public skill scripts still declare one" over a
  measured zero. `twelve` is a word, so a digit-only rule would have been inert
  against its own instance.
- `bare-completeness-word` — `only`, `all`, `every`, `none`, `still`,
  `repo-wide` — is ADVISORY. Every one of these has a structural English use no
  regex separates from its claim-bearing use, and the measured casualties were
  honest-limits sentences.

  This is a DEVIATION from the release contract, which says these words are
  forbidden and that the lint refuses each of them. It is recorded as such in
  the contract's `## Deviations Awaiting Owner Ruling`, with the measurement
  attached, and the criterion stands unamended until the owner rules. It is
  explicitly NOT justified by the contract's "no prose claim-extractor"
  non-goal: that non-goal rejects building an extractor, while the same Fixed
  Decision that lists these words calls for "a regex-shaped lint with an obvious
  negative case" — which is what this is. The contract asked for the refusal;
  the evidence is why it was not delivered.

Number words are in scope for the blocking arm; the words that merely COLOUR a
quantity are not. That line is where measurement put it, not where it read
best.

Non-claims: this refuses UNGROUNDED quantities, not wrong ones — a marker whose
value is false is the derived block's job. And an author can always ground a
quantity by writing a claim marker or moving an identifier into a code span.
"""
from __future__ import annotations

import argparse
import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_claims = SKILL_RUNTIME.load_local_skill_module(__file__, "release_notes_claims")
_yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
emit_yaml = _yaml_output.emit_yaml

#: `one` is deliberately absent. "one of", "no one", and "one another" are
#: structural English, not quantity claims. The hole is real and stated: a note
#: asserting "one script declares it" passes the blocking arm. `score`, `couple`,
#: `both`, and `half` are absent too, for the same structural-English reason.
#: (The recorded
#: false sentence happens to contain `one` in exactly that position — "twelve
#: public skill scripts still declare one" — which is why it is caught by
#: `twelve` and not by `one`.)
_NUMBER_WORDS = (
    "two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty "
    "ninety hundred thousand million billion zero dozen dozens"
).split()

#: The release contract's list, verbatim. Advisory, for the reason in the module
#: docstring: every one of these has a structural English use that no regex
#: separates from its claim-bearing use.
_COMPLETENESS_WORDS = ("only", "all", "every", "none", "still", "repo-wide")

#: NO hyphen in these lookarounds, and that is the correction of a real escape.
#: English writes every cardinal from 21 to 99 with a hyphen, and `-` in the
#: lookarounds made both halves fail: in `twenty-seven`, `twenty` failed the
#: lookahead and `seven` failed the lookbehind, so "twenty-seven public skill
#: scripts still declare one" passed the blocking arm clean -- the recorded
#: sentence, one hyphen away. `_COMPLETENESS_RE` still needs the hyphen because
#: `repo-wide` is itself hyphenated.
_NUMBER_WORD_RE = re.compile(r"(?<!\w)(" + "|".join(_NUMBER_WORDS) + r")(?!\w)", re.IGNORECASE)
_COMPLETENESS_RE = re.compile(r"(?<![\w-])(" + "|".join(_COMPLETENESS_WORDS) + r")(?![\w-])", re.IGNORECASE)
#: A digit run that is not part of a larger token. `H2` (a markdown heading
#: level) reported `2` as a quantity claim without the word lookarounds.
#:
#: The hyphen is deliberately NOT in these lookarounds. It was, briefly, to
#: exempt `exit-3` -- and it bought that narrow exemption by blanking every
#: hyphen-adjacent digit in the document, so `12-15` and every other numeric
#: range went unreported. `exit-3` now has its own exemption below, which is
#: where a narrow exemption belongs.
_DIGIT_RE = re.compile(r"(?<![\w.])\d+(?!\w)")

BLOCKING_KINDS = ("bare-quantity", "unbalanced-code-fence", "notes-unreadable")

#: A fence is three-or-more backticks or tildes, and a run closes only on the
#: SAME character. Matching backticks alone let a note fenced with `~~~` past
#: this rule while `audit_public_release_narrative._FENCE_RE`, one file away in
#: the same skill, masked it — two fence models in one skill disagreeing.
_FENCE_LINE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")

#: Regions whose contents are not authored narrative.
_EXEMPT_PATTERNS = (
    # HTML comments carry the derived block's delimiters, the generator's
    # guidance, and any authoring note. None of it renders in a published
    # release body, so none of it is a claim a reader can act on.
    ("html-comment", re.compile(r"(?s)<!--.*?-->")),
    ("claim-marker", _claims.CLAIM_MARKER_RE),
    ("inline-code", re.compile(r"`[^`\n]+`")),
    ("link-target", re.compile(r"\]\([^)\n]*\)")),
    ("url", re.compile(r"https?://\S+")),
    # An ISO date is a point in time, not a quantity claim about the tree.
    ("iso-date", re.compile(r"\d{4}-\d{2}-\d{2}")),
    # Ordered-list markers: markdown structure, not a claim.
    ("list-marker", re.compile(r"(?m)^[ \t]*\d+\.[ \t]")),
    # An issue or PR reference. A hash-prefixed tracker number is a NAME, and
    # release notes are largely made of them; refusing one taught authors that
    # the rule does not understand prose.
    ("issue-reference", re.compile(r"#\d+")),
    # An exit code is an identifier of a program state, not a measurement of the
    # tree. This repo's breaking-change notes are largely made of them
    # ("exits 2", "exit 3"), and every one was a false refusal.
    ("exit-code", re.compile(r"(?i)\bexits?(?:[ \t]+code)?[ \t-]+\d+")),
)


def _IS_LINE_BREAK(char: str) -> bool:
    return len(char.splitlines()) != 1 or char in "\r\n"


def _version_patterns(versions: tuple[str, ...]) -> list[re.Pattern[str]]:
    """A release note names its own version and the one it rolls back to.

    Built from the versions the CALLER supplies rather than from a general
    version-shaped regex: a loose `\\d+\\.\\d+\\.\\d+` would also exempt "we
    measured 3.1.4 seconds", and every exemption here is a hole in the rule.
    Callers that know a previous version should pass it — the publish gate reads
    it from the packaging manifest for exactly this reason.
    """
    patterns = []
    for version in versions:
        bare = version[1:] if version.startswith("v") else version
        if not bare:
            continue
        patterns.append(re.compile(r"v?" + re.escape(bare)))
    return patterns


def _fence_spans(text: str) -> tuple[list[tuple[int, int]], int | None]:
    """Character spans of fenced blocks, and the line of a MIS-PAIRED fence.

    Scanned line by line rather than with one non-greedy regex, because the
    regex form paired an opening fence with the next backticks-only line and
    blanked everything between them.

    Two mis-pairing signals, and the second is the one that matters. A fence
    still open at end of file is the obvious case. The subtle case is a fence
    opener WITH an info string (```yaml) appearing while a fence is already
    open: by CommonMark that is literal text inside a code block, so the
    document is valid and the scan is correct — and the note still means
    something the author did not write. It is the exact shape a note with one
    forgotten closer takes, because the generated claim block below it opens
    every chunk with ```yaml. A release note nesting an info-string fence inside
    a code block is vanishingly rare; a release note with a stray fence above a
    generated block is one keystroke away, and it silently exempts every claim
    in between.
    """
    spans: list[tuple[int, int]] = []
    offset = 0
    open_marker: str | None = None
    open_length = 0
    open_start = 0
    open_line = 0
    mispaired: int | None = None
    for line_no, line in enumerate(text.splitlines(keepends=True), start=1):
        match = _FENCE_LINE_RE.match(line.rstrip("\n"))
        if match:
            marker, info = match.group(1), match.group(2).strip()
            closes = open_marker is not None and marker[0] == open_marker and len(marker) >= open_length
            if open_marker is None:
                open_marker, open_length, open_start, open_line = marker[0], len(marker), offset, line_no
            elif closes and not info:
                spans.append((open_start, offset + len(line)))
                open_marker = None
            elif closes and info and mispaired is None:
                # A fence that COULD have closed this run but carries an info
                # string. A shorter inner fence is a legitimate nested example
                # and is left alone; this one is the forgotten-closer shape.
                mispaired = open_line
        offset += len(line)
    if open_marker is not None:
        mispaired = open_line
    return spans, mispaired


def mask_exempt_regions(text: str, versions: tuple[str, ...] = (), *, mask_fences: bool = True) -> str:
    """``text`` with every non-narrative region replaced by spaces.

    Spaces, not deletion: offsets have to survive so a finding can name the line
    and column an author actually looks at. Newlines are preserved likewise.
    """
    masked = list(text)

    def blank(start: int, end: int) -> None:
        for index in range(start, end):
            # Preserve every character `str.splitlines` treats as a break, not
            # just "\n". Blanking a lone "\r" or a "\u2028" inside an exempt
            # region shortened the masked text by a line, so `zip` below silently
            # dropped the file's LAST line and every finding after that point
            # named the wrong source line.
            if not _IS_LINE_BREAK(masked[index]):
                masked[index] = " "

    if mask_fences:
        for start, end in _fence_spans(text)[0]:
            blank(start, end)
    for _label, pattern in _EXEMPT_PATTERNS:
        for match in pattern.finditer("".join(masked)):
            blank(match.start(), match.end())
    for pattern in _version_patterns(versions):
        for match in pattern.finditer("".join(masked)):
            blank(match.start(), match.end())
    return "".join(masked)


def _finding(kind: str, line_no: int, column: int, token: str, detail: str, source: str) -> dict[str, object]:
    return {
        "kind": kind,
        "severity": "blocking" if kind in BLOCKING_KINDS else "advisory",
        "line": line_no,
        "column": column,
        "token": token,
        "detail": detail,
        "source": source,
    }


_QUANTITY_REMEDY = (
    "Ground it in a `{{claim:<surface>.count=<value>}}` marker the publish gate re-derives, "
    "or move it inside a code span if it is a path, flag, or identifier."
)


def _findings_for_line(line_no: int, line: str, source_line: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    # Digits and number words are ONE rule with two spellings, so they are one
    # loop. Written as two near-identical blocks, the second is where the kind or
    # the severity gets typed differently and half the blocking arm silently
    # becomes advisory.
    for pattern, phrasing in ((_DIGIT_RE, "in authored prose"), (_NUMBER_WORD_RE, "written as a word")):
        for match in pattern.finditer(line):
            findings.append(
                _finding(
                    "bare-quantity", line_no, match.start() + 1, match.group(0),
                    f"line {line_no} carries the bare quantity `{match.group(0)}` {phrasing}. {_QUANTITY_REMEDY}",
                    source_line.strip(),
                )
            )
    for match in _COMPLETENESS_RE.finditer(line):
        findings.append(
            _finding(
                "bare-completeness-word", line_no, match.start() + 1, match.group(0),
                f"line {line_no} carries the completeness word `{match.group(0)}` in authored prose. "
                "It reads as measured; advisory only, because this word has a structural English use no "
                "regex separates from a claim. Check that something measured it.",
                source_line.strip(),
            )
        )
    return sorted(findings, key=lambda finding: finding["column"])


def lint_text(text: str, *, versions: tuple[str, ...] = ()) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    mispaired = _fence_spans(text)[1]
    if mispaired is not None:
        findings.append(
            _finding(
                "unbalanced-code-fence", mispaired, 1, "",
                f"the code fence opened at line {mispaired} is never closed, or closes somewhere the "
                "author did not intend: a later fence opener appears while it is still open. Everything "
                "in between reads as code and is exempted from this rule, which is how an ungrounded "
                "claim escapes.",
                "",
            )
        )
    # When the fences are mis-paired, their masking is not trusted. Suppressing
    # it means the claims that WERE hidden get reported alongside the fence
    # finding, instead of surfacing only after the operator repairs the fence and
    # runs again. Some genuine code content will be reported too; the note is
    # already blocked, so extra lines here cost a read, not a false green.
    masked = mask_exempt_regions(text, versions, mask_fences=mispaired is None)
    for line_no, (masked_line, source_line) in enumerate(zip(masked.splitlines(), text.splitlines()), start=1):
        findings.extend(_findings_for_line(line_no, masked_line, source_line))
    return findings


def lint_file(path: Path, *, versions: tuple[str, ...] = ()) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        # `ValueError` covers `UnicodeDecodeError`. Catching `OSError` alone let a
        # non-UTF-8 notes file traceback out of a function whose whole contract is
        # to return a finding instead.
        return [_finding("notes-unreadable", 0, 0, "", f"could not read the notes file `{path}`: {exc}", "")]
    return lint_text(text, versions=versions)


def blocking(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    return [finding for finding in findings if finding["severity"] == "blocking"]


def finding_lines(findings: list[dict[str, object]]) -> list[str]:
    return [f"[{finding['severity']}] {finding['kind']}: {finding['detail']}" for finding in findings]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root (unused for the rule; kept for command-surface consistency)")
    parser.add_argument("--notes-file", type=Path, required=True, help="Release notes file whose authored prose is linted")
    parser.add_argument("--version", action="append", default=[], help="A release version this note may name without grounding it; repeatable, and worth passing the version being rolled back to as well")
    args = parser.parse_args()

    findings = lint_file(args.notes_file, versions=tuple(args.version))
    blockers = blocking(findings)
    emit_yaml(
        {
            "notes_file": str(args.notes_file),
            "status": "clean" if not blockers else "contained-claim-required",
            "finding_count": len(findings),
            "blocking_count": len(blockers),
            "advisory_count": len(findings) - len(blockers),
            "findings": findings,
        }
    )
    # Advisories do not fail the command. An author who cannot get to zero
    # without deleting an honest hedge would otherwise learn to ignore the exit
    # code, and then the blocking arm goes unread with it.
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
