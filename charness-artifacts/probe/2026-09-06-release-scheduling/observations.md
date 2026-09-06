# Release verification scheduling observation

Date: 2026-09-06

## Question and disposition

Can a prepare-time pytest pass be reused after commit/amend and claims records
change, based on worktree bytes excluding the release/review artifacts?
Disposition: that proposed independence is **not established**. Actual pytest
processes read the excluded artifacts and internal Git observations. This is
not a measured Q/P verdict difference or proof that every observed read affects
a verdict. It warrants the simpler design: execute pytest against the final
state instead of constructing an incomplete equivalence claim.

## Method and bounded evidence

A read-only investigator ran the declared pytest-release selection under
`strace -ff -qq -e trace=execve,chdir,openat,newfstatat,readlink -s 500`, invoking
`python3 scripts/run_quality_engine.py --repo-root . --gates .agents/quality-gates.yaml --read-only --labels pytest-release`.
Tracing was interrupted after about eight minutes because amplification produced
5.7 GB, not a useful passing receipt. This probe was too broad and its trace cost
is investigation overhead, not time saved. No passing suite or comparison cell
is claimed. Production observer source was unchanged during the trace; the
worktree/artifact state was not frozen for a Q/P differential experiment.

The parent independently read these exact excerpts and rehashed their source
trace files. Absolute paths below are literal observed syscall data, not
portable artifact locators. Trace filenames identify the sources of the retained excerpts.

```text
trace.3584966:28
execve("/usr/bin/git", ["git", "-C", "/home/hwidong/codes/charness", "show", ":scripts/artifact-referent-local-context.json"], 0x560febc1fc00 /* 96 vars */) = 0
trace.3584992:28
execve("/usr/bin/git", ["git", "-C", "/home/hwidong/codes/charness", "rev-list", "HEAD"], 0x560febc08850 /* 96 vars */) = 0
trace.3599527:1
chdir("/home/hwidong/codes/charness")   = 0
trace.3599527:28
execve("/usr/bin/git", ["git", "status", "--porcelain", "--", "charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md"], 0x560febc1ed00 /* 96 vars */) = 0
trace.3578786:456468
openat(AT_FDCWD, "/home/hwidong/codes/charness/charness-artifacts/release/latest.md", O_RDONLY|O_CLOEXEC) = 13
trace.3578786:602236
openat(AT_FDCWD, "/home/hwidong/codes/charness/charness-artifacts/release-review/2026-08-13-v5.2.0-claims-review.md", O_RDONLY|O_CLOEXEC) = 13
```

Original trace SHA256 values:

- `trace.3584966`: `13fa2043c2a5d42e171718cab35f527e286bf462b82d1c4e4fb57a39b212c3c5`
- `trace.3584992`: `0ebfff403403437b6e1801bf729a76c9e9ff886b6793289375980c9fdd41c4bf`
- `trace.3599527`: `669717f60bb2638d3adc61f0ac91fd4245de1275c63ad17e07b3494af6ea0d77`
- `trace.3578786`: `d55d3c501f9e721105c846506a89af795dc36859e999a2afe7f04be7e6e1d9a8`

The bounded excerpts above are durable evidence; original trace bulk is runtime
reproduction material, not a release prerequisite or portable approval carrier.
The 5.7 GB temporary originals were deleted after excerpt/hash capture; they are
not retained or recoverable from this record.

## Disconfirmers and limitations

The parent checked `tests/conftest.py` and `scripts/core/repo_file_listing.py`:
the default live listing unions tracked and nonignored untracked files. Moving
a file from untracked to tracked alone therefore does not prove a semantic
change. `tests/seed_cache.py` hashes HEAD/diff to choose an execution namespace;
namespace drift alone does not prove a test-verdict dependency either. Most
fixture Git activity occurs in temporary repositories. None of those facts
removes the directly observed live release/review reads above.

Source SHA256: conftest `4e2918a964cdbe88abe68a0e399f95a5bdfe9f94bb2529d8070c53b6482c97ee`;
listing `4fd0f7475ee435be0bec04745f94c2215bd12536b52a477011fbbbab2cb0a4a1`;
seed cache `0c6dc61320774c0e609bea7c5bba0bb67cb90d7e3482fb4d1d08e5308c43ee53`.

## Next move

The living release-reuse WorkItem owns the revised scheduling contract. Prepare
reports the deferred pytest subject honestly; resume runs the ordinary full
release lane on exact current R. No cross-commit reuse, generalized cache,
invariance oracle, or v2 handoff is needed. Final publication proof remains
current. The bounded design follow-up `goal805-design-release-repair` accepted
this design with no findings before implementation; its supplied snapshot is
design evidence, not approval of later code.

## Implementation evidence (pre-integration)

The parent implemented scheduling in the existing runner and release owner,
without a cache, new receipt schema, or new executable. A native read-only
advisory reviewer found two concrete survivors: a shell chain could be mistaken
for a simple runner invocation, and receipt-emission failure could still exit 0.
Both were repaired with focused negative controls before formal code review.

Standing command:

```sh
python3 scripts/gates_support/run_standing_pytest.py --repo-root . --include-release-only --pytest-target tests/quality_gates/test_release_publish.py::test_prepare_claims_resume_schedules_one_final_suite --pytest-target tests/quality_gates/test_quality_runner_release_order.py --pytest-target tests/quality_gates/test_prepush_runtime_regime.py --pytest-target tests/test_release_lane_receipt.py --pytest-target tests/quality_gates/test_run_quality_engine.py --pytest-target tests/quality_gates/test_release_quality_status_binding.py --pytest-target tests/quality_gates/test_release_quality_gate_visibility.py
```

Observed: 93 passed in 10.64s (standing wrapper 11.8s). The topology fixture
carries an honest pending prepared record through committed claims review and
resume, counts one final instrumented suite, and refuses final failure before
tag/push/release creation. Its command is instrumented, not the real repository
suite. Separate real engine fixture tests verify exact selection, no variant
fallback, unknown-gate execution, partial persistence, and failed persistence.
Real pre-push fixture tests reject partial/prepare/missing-pytest handoffs and
take ordinary full fallback. Scoped local commit floors remain unchanged.

Initial test mistakes were fixture defects, not production failures: the engine
seed deliberately includes two unrelated unproven gates, and `git tag --list` is
a read, not publication. Correcting those stimuli/observations made the desired
claims testable without weakening production behavior.

Python lint and shell checks passed. Code length passed with existing advisory
warnings. The development page exceeded its word budget when the new behavior
was duplicated there; its existing routing table now points to the release
adapter owner instead. Final export, integrated broad/changed-line proof, formal
code review, actual release timing and installed behavior are still unproven.

## Bounded code review and repair

The two file-backed reviews `goal805-code-release-integrity` and
`goal805-code-release-operability` returned BLOCK, with delivered findings and
clean read-only boundaries. Both current packet bindings were verified before
repair. Typed results are retained under `charness-artifacts/goal-runs/805/reviews/`.

- Act Before Ship: R811-PI-01, relative receipt paths were interpreted against
  different directories by writer and copier. The outside-repo/stale-caller-file
  negative test reproduced a passing stale last receipt. Resolve the destination
  once against the repository and pass that absolute path through both owners.
- Act Before Ship: R811-PI-02 and R811-OPERABILITY-01 are the same finding. A
  trailing newline survived argv recognition but split the appended modifier
  into another shell command. The command assertion reproduced it; native commands
  now execute `shlex.join` of the accepted argv, including final receipt arguments.
  Unsupported shell chains still retain their original full-execution text.
- Bundle Anyway: use the same normalization for final receipt collection, the
  direct sibling of preparation's append path.
- Over-Worry: introducing a cache or general shell parser is unnecessary here.
- Valid but Defer: actual release/net timing and installed behavior remain later
  Goal acceptance, not inferred from these code tests.

After repair, 48 relevant tests passed in 8.26s (wrapper 9.1s), including the
previous two failures and the topology flow; Python lint passed. An actual-shell
newline roundtrip was then added to the existing command visibility tests. One
bounded repair follow-up will read the repaired owners; no third code round.
