"""Render mutation-sweep outcomes and their explicit non-claims.

This module owns the report projection after mutation execution has finished:
it turns sweep state into YAML data, states when caller reachability was not
established, and maps the result to the runner's exit contract. Keeping this
reader-facing policy separate leaves the original script's mutation lifecycle
and test seams intact.
"""

from __future__ import annotations

KILLED = "killed"
SURVIVED = "survived"
REFUSED = "refused"


def render(sweep) -> dict:  # noqa: ANN001
    return {
        "baseline": {
            "earned": sweep.baseline.earned,
            "passed": sweep.baseline.passed,
            "returncode": sweep.baseline.returncode,
            "refusal": sweep.baseline.refusal,
        },
        "mutants": [
            {
                "id": m.id,
                "path": m.path,
                "verdict": m.verdict,
                "detail": m.detail,
                "returncode": m.returncode,
                "removed_calls": list(m.removed_calls) if m.removed_calls is not None else None,
                "declared_call_site": m.declared_call_site,
            }
            for m in sweep.mutants
        ],
        "killed": sum(1 for m in sweep.mutants if m.verdict == KILLED),
        "survived": len(sweep.survived),
        "refused": len(sweep.refused),
        "call_site_mutants": len(sweep.call_site_mutants),
        "call_site_non_claim": call_site_non_claim(sweep),
    }


def call_site_non_claim(sweep):  # noqa: ANN001
    """What a clean sweep with no call-site mutant does NOT establish (`#564`).

    Reported, never refused, and the boundary is deliberate. The tool can see that no
    mutant was DECLARED a call-site test; it CANNOT see whether one was warranted -- a
    sweep over a constant table or a pure predicate legitimately has none. Refusing on
    that would make the runner assert something about the plan it never established,
    which is the class it exists to stop, so this states the gap and leaves the judgement
    with the reader. P5: force the question, do not declare completion.

    Silenced ONLY by a declaration the edit corroborates. An earlier cut let the inferred
    removed-call count silence it, which meant an incidental `.join` deletion in a body
    mutant turned the warning off -- the tool suppressing its own finding on evidence that
    did not mean what it counted.
    """
    # An EMPTY plan still gets the non-claim. It used to be silenced alongside an unearned
    # baseline, which made the emptiest possible sweep -- `0 killed, 0 survived`, exit 0,
    # no warning -- the most unearned clean report this tool can print, while the module
    # docstring promised that a sweep with no declared call-site test says so out loud.
    # An unearned baseline is different: it already refuses loudly and prints no counts.
    if not sweep.baseline.earned:
        return None
    if sweep.call_site_mutants:
        return None
    # Says DECLARED, because that is the condition above. The first wording said "no
    # mutant deleted a call site" -- vocabulary left over from the inference design -- and
    # this tool's own suite has a run where that sentence is printed while the per-mutant
    # line reads `[removes join, str]`. Two contradictory statements in one report, and the
    # operator-facing one was the false one, on a surface whose whole thesis is not
    # reporting what it did not establish.
    claim = (
        'no mutant was DECLARED a call-site test (`"call_site": true`), so a clean result '
        "here says nothing about whether these repairs are still REACHED in production: a "
        "repair pinned only at its own function survives deletion of its caller with the "
        "suite green (#564, measured three times in one goal, none visible in the diff)"
    )
    # And on a non-Python target the reader could not have counted one anyway.
    # `removed_calls` parses a PYTHON ast, so a `.js` file yields `None` -- not
    # `()` -- which means both halves of the call-site mechanism are inert there:
    # no mutant can ever satisfy `call_site_mutants`, so this sentence fires on
    # EVERY Node sweep regardless of the plan, and the one place this tool has
    # teeth (`declared and removed == ()` -> REFUSED) cannot fire either, so a
    # false `"call_site": true` on a JS mutant is accepted uncorroborated.
    #
    # A message that is always printed carries no information, and this repo has
    # shipped that shape before. Naming the cause is what keeps it informative:
    # the author is told the check was INAPPLICABLE, not that they forgot to
    # declare one.
    unparsed = sorted({m.path for m in sweep.mutants if not m.path.endswith(".py")})
    if unparsed:
        claim += (
            "; and the call-site check could not be APPLIED to "
            + ", ".join(unparsed)
            + " at all -- it reads a Python AST, so on a non-Python target it neither "
            "counts a declared caller test nor refuses a false declaration"
        )
    return claim


def exit_code(sweep) -> int:  # noqa: ANN001
    if not sweep.baseline.earned:
        return 2
    if sweep.survived or sweep.refused:
        return 1
    return 0
