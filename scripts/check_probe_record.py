#!/usr/bin/env python3

"""Read a probe record and report which question it managed to answer.

The command surface for `probe_record_lib`. Two modes, and the difference is the whole
reason both exist:

* default -- REPORT. Print the typed state and every undetermined reason, exit 0. This
  is what an author runs while building a record, and what a reader runs to see what a
  record actually establishes. It does not gate, so it cannot be the thing a boundary
  floor trusts.
* `--require-evaluated` -- REFUSE. Exit non-zero unless the record resolves `evaluated`.
  This is the mode a close or a publish runs, where a claim that outran its measurement
  is the failure being prevented.

`--replay-stimulus` composes with either. It adds the one thing the two modes above
structurally cannot do -- it REPLAYS the adapter declarations the record's own `## Stimulus`
writes, through the real resolver, and refuses a declaration the reader does not honor even
at a speakable version (#674). It is OPT-IN rather than part of `--require-evaluated`
because it shells out to sixteen possible resolvers, and the issue-close and release floors
that call this CLI should not silently acquire that cost. `probe_stimulus_replay`'s
docstring owns what it replays and, at greater length, what it does not.

WHAT THIS DOES NOT DO, stated because the name invites the assumption: it does not run
the probe. It reads captured observables out of a file somebody wrote. Its whole tooth
is that an unmeasured claim must now SAY it is unmeasured in a typed word, in a file a
distinct observer can read, rather than rendering identically to a measured one. Whether
the captured values were measured or transcribed is rung-2 judgment; see
`probe_record_lib`'s blind class.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

_probe_record = import_repo_module(__file__, "scripts.probe_record_lib")
_stimulus_replay = import_repo_module(__file__, "scripts.probe_stimulus_replay")
_yaml_output = import_repo_module(__file__, "scripts.yaml_output")

REPO_ROOT = Path(__file__).resolve().parents[1]


def evaluate(repo_root: Path, record_path: Path, *, replay_stimulus: bool = False) -> dict:
    try:
        text = record_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # An unreadable record is `not-established` rather than a crash: "the record could
        # not be read" is exactly the kind of could-not-tell this vocabulary exists to say,
        # and a traceback at a closeout boundary reads as a broken tool, not as a refusal.
        #
        # Built by the LIBRARY, not here. This used to be a hand-rolled dict, which is a
        # second construction of a shape whose single owner exists so no branch can omit a
        # key -- and it had already drifted, missing both `residual_judgment` and the
        # `local` flag the degraded-reason gate reads.
        return _probe_record.unreadable_record_result(
            f"could not read the probe record at `{record_path}`: {exc}"
        )
    parsed = _probe_record.parse_probe_record(text)
    result = _probe_record.resolve_probe_record(parsed, repo_root=repo_root)
    if replay_stimulus:
        return _merge_stimulus_replay(
            result, _stimulus_replay.replay_probe_stimulus(parsed, repo_root=repo_root)
        )
    return result


def _merge_stimulus_replay(result: dict, replay: dict) -> dict:
    """Fold the replay verdict into the record's, in the refusing direction only.

    A replay that resolves `not-established` demotes the record: its reproduction steps do
    not reproduce, so whatever the captured observables say, the record does not establish
    its claim. A replay that PASSES never promotes a record the static resolver refused --
    the two mechanisms answer different questions and only one of them can say `evaluated`.

    The demotion is built by `probe_record_lib.demoted_result`, not here. The first cut set
    the four state-dependent keys in place, which is the second-construction class this
    file's own comment above records -- and that copy had already drifted.
    """
    if replay["state"] != _stimulus_replay.STIMULUS_NOT_ESTABLISHED:
        return {**result, "stimulus_replay": replay}
    demoted = _probe_record.demoted_result(
        result, [f"the stimulus does not reproduce: {reason}" for reason in replay["reasons"]]
    )
    return {**demoted, "stimulus_replay": replay}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--record", type=Path, required=True, help="Path to the probe record to read")
    parser.add_argument(
        "--require-evaluated",
        action="store_true",
        help="Exit non-zero unless the record resolves `evaluated`. Use at a close or publish "
        "boundary; omit while authoring.",
    )
    parser.add_argument(
        "--replay-stimulus",
        action="store_true",
        help="Also replay the adapter declarations the record's `## Stimulus` writes, through the "
        "real resolver, and refuse a declaration the reader does not honor at a speakable version.",
    )
    args = parser.parse_args()
    result = evaluate(args.repo_root.resolve(), args.record, replay_stimulus=args.replay_stimulus)
    result["record"] = str(args.record)
    sys.stdout.write(_yaml_output.render_yaml(result))
    if args.require_evaluated and result["state"] != _probe_record.PROBE_EVALUATED:
        print(
            f"\nFAIL probe record `{args.record}` resolves `{result['state']}`, not "
            f"`{_probe_record.PROBE_EVALUATED}`: it does not establish the claim it carries.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
