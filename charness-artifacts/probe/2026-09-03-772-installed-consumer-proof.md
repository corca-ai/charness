# #772 installed-consumer proof (Goal Run #765, integrated closeout)

Date: 2026-09-03
Source commit under test: `55a1f235e7a36ce68f0258d2a68b453fcdbd56f6`
Installed checkout commit (readback from `~/.agents/src/charness` in the sandbox): `55a1f235e7a36ce68f0258d2a68b453fcdbd56f6`
Recipe: `charness-artifacts/goal-runs/765/briefs/map-772.md` section 3, rerun verbatim by `/tmp/install-proof-772.sh`
Transcripts: `charness-artifacts/probe/2026-09-03-772-installed-consumer-proof-transcripts/`

## Capability claim

A consumer who installs charness from this commit through `init.sh` gets a
working `charness` CLI and an exported plugin whose quality skill runs against
the consumer's own repository without executing any authoring-repo `tools/`
gate and without a `tools/` directory in the export.

## Non-claims

- No release, tag, or publish happened; `charness version` reports the
  manifest version already on this tree (8.0.2).
- No host app (Codex, Claude) was installed or mutated: the sandbox PATH strips
  both binaries, so `init.sh` prepared the managed checkout and marketplace
  only.
- The exported `run-quality.sh` is not claimed to run a consumer's quality
  lane; it refuses by name (see below), which is the #769 critique's F9
  disposition.
- The proof ran on the operator's machine, not a fresh OS image; python3 and
  git came from the host.

## Isolation

`HOME`, `CHARNESS_STATE_HOME`, `CHARNESS_CONFIG_HOME` rooted at
`/tmp/charness-772-proof/home`; `CHARNESS_NO_UPDATE_CHECK=1`; PATH reduced to
`/usr/local/bin:/usr/bin:/bin` plus the sandbox's `~/.local/bin` after
install. `init.sh --home-root <sandbox> --repo-url /home/hwidong/codes/charness`
cloned the source checkout, so the network was not touched.

## Executed proof

| step | command (from the throwaway consumer repo) | exit | observed |
| --- | --- | --- | --- |
| install | `bash init.sh --home-root $SB/home --repo-url <source>` | 0 | managed checkout at `$SB/home/.agents/src/charness`, same commit as the source |
| doctor | `charness doctor` | 0 | `managed_checkout: true`, `target_repo_root: $SB/consumer`, `checkout_version: 8.0.2` |
| update | `charness update` | 0 | completed actions listed in `update.out` |
| version | `charness version` | 0 | `version: 8.0.2` |
| doctor state | `charness doctor --write-state` | 0 | state files under `$SB/home/.local/state/charness/` |
| quality plan | `python3 $SKILL_DIR/scripts/plan_quality_run.py --repo-root .` | 0 | plan emitted from the installed export |
| regenerable facts | `python3 $SKILL_DIR/scripts/check_regenerable_facts.py --repo-root .` | 0 | consumer surfaces checked |
| runtime summary | `python3 $SKILL_DIR/scripts/render_runtime_summary.py --repo-root .` | 0 | typed not-configured advisory |
| ergonomics | `python3 $SKILL_DIR/scripts/inventory_skill_ergonomics.py --repo-root .` | 0 | typed unconfigured status |
| exported runner | `bash $P/scripts/run-quality.sh --read-only` | 1 | refuses by name: `run-quality: refusing to run from an installed/exported copy without a source checkout.` |

`$SKILL_DIR` is `$SB/home/.codex/plugins/charness/skills/quality` and `$P` is
`$SB/home/.codex/plugins/charness`. Every exit code is in `exits.txt`.

## The `tools/` assertions

- `$P/tools` does not exist (`tools-grep.out`, first line).
- No command transcript (`init`, `doctor`, `update`, `version`, quality
  scripts, exported runner) contains a root `tools/` reference; the only hits
  in `tools-grep-transcripts.out` are the grep outputs themselves.
- The installed export's source carries string references to the authoring
  repo's `tools/` gates (61 sites across 17 files, mostly
  `scripts/staged_commit_gate_plan.py` and
  `scripts/adapters/quality_universes_lib.py`). These are the `export-guard:`
  and advisory references that `tools.check_export_self_sufficiency` classifies
  (`exported_tools_code_references: []`, status pass at this commit). None is
  executed by the commands above; a consumer commit-time plan schedules a
  `tools/` gate only when the file is present, which it is not.

This differs from map-772 section 3.4, measured before #769 landed the
guarded references; the assertion that matters (no shipped `tools/`, no
executed `tools/` gate) holds at both commits.

## The exported runner (F9, F10)

- F9: map-772 section 3.5 observed the exported `run-quality.sh` dying on a
  missing `.githooks/runtime-env.sh`. At this commit it refuses by name with
  the package root and the reason (`rq.err`). The consumer route stays the
  planner over the consumer's own declared list, which is what the quality
  plan step above exercised.
- F10: the exported-copy test seeds a narrower shape than a real install.
  This live proof is the evidence for the real shape; the seeded test is not
  widened.

## Release lane

`./scripts/run-quality.sh --release` on the integrated tree: 84 passed, 0 failed (`docs-graph-awiki` prints FAIL as an uncounted advisory), run at `3fd042d4c`.
The first run found nine release-only reds that the standing lane's marker
filter had excluded since #768 (in-process loaders and the packaging); they
are fixed in `1da602d3f`; the release changed-line gate then refused to claim the four stubs until a standing test drove them (`1a9235c34`, `3fd042d4c`), and the lane was rerun green on that committed tree.

## Cleanup

Sandbox `/tmp/charness-772-proof` is disposable; the transcripts were copied
beside this record before deletion.
