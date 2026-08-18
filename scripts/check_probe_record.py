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
_yaml_output = import_repo_module(__file__, "scripts.yaml_output")

REPO_ROOT = Path(__file__).resolve().parents[1]


def evaluate(repo_root: Path, record_path: Path) -> dict:
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
    return _probe_record.resolve_probe_record_text(text, repo_root=repo_root)


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
    args = parser.parse_args()
    result = evaluate(args.repo_root.resolve(), args.record)
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
