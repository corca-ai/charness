Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**What shipped.** The gate no longer roots itself at the exported `plugins/charness`
copy, so it measures the repo tree and reads the repo-root markdownlint config rather
than a narrower one.

**The residual an earlier review of this issue recorded as unfixed is also repaired.** A
reference pointed consuming repos at an exported `check-links-internal.sh` that refuses
when run inside a consumer repo. That reference now names the half that is runnable
there and the environment variable that retargets the other half, and the refusal text
now names the reader's own repo root alongside the script root, so a reader can see which
tree the gate resolved.

Behavior #618: the rooting fix is demonstrated by the gate reading the repo-root config
and the previously-missed tracked files; the reference repair is demonstrated by
`skills/public/setup/references/default-surfaces.md` naming the runnable half
(`check_doc_links.py`) and the `CHARNESS_REPO_ROOT` retarget for the other.

Critique #618: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
