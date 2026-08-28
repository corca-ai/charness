# repograph

Non-production spike crate for issue #745. It provides a typed inventory and
panic-safe Python parser; no gate, hook, skill, or export may depend on it.

## Build

The crate pins Rust 1.96.0 and the parser dependencies required by the spike.
Build it from this directory with:

```bash
cargo build --release --offline
```

## Run

`parse-corpus` acquires one Git file snapshot and emits one JSON document. The
default exclusion is the `plugins/` prefix; pass `--exclude-prefix` to replace
it. A NUL-separated repository-relative file list can be injected instead:

```bash
target/release/repograph parse-corpus --repo-root fixtures \
  --file-list fixtures/file-list.nul
```

The fixture list intentionally includes malformed files, so that command exits
3 and reports typed failures. Use `--exclude-prefix` repeatedly when a clean
scope needs more than the default exclusion.

The committed fixture tree is synthetic and includes deliberate failures. A
clean canonical checkout scan therefore also excludes `native/repograph/fixtures/`:

```bash
target/release/repograph parse-corpus --repo-root ../.. \
  --exclude-prefix plugins/ \
  --exclude-prefix native/repograph/fixtures/
```

The validator spike commands emit one versioned JSON document each:

```bash
target/release/repograph export-safe --repo-root ../..
target/release/repograph match-surfaces --repo-root ../.. --path README.md
target/release/repograph standalone-targets --repo-root ../..
```

The topology command emits typed nodes, edges, roots, mirror destinations, and
role conditions from the same inventory. Its default excludes are `plugins/`
and `native/repograph/fixtures/`:

```bash
target/release/repograph graph --repo-root ../..
```

The additive carrier diagnostic emits command-carrier nodes, validation
commands, program-position `invokes` edges, path references, unresolved
carriers, and run-quality label observations:

```bash
target/release/repograph carriers --repo-root ../..
```

Use repeatable `--analyzer-result FILE` options to record identity-only
provider inputs; this lane marks their scope `unestablished` until a later
lane supplies provider parsing.

The query commands classify changed paths with the same role resolver and
surface matcher, including deleted paths supplied by `--path`:

```bash
target/release/repograph classify --repo-root ../.. --path scripts/example.py
target/release/repograph changed --repo-root ../.. --path scripts/example.py
```

The parity and benchmark harnesses are investigative only and are not wired
into repository gates:

```bash
python3 parity/run_parity.py --repo-root ../..
python3 parity/run_bench.py --repo-root ../..
```

## Test

Run the unit and fixture tests with:

```bash
cargo test --offline
cargo fmt -- --check
cargo clippy --offline --all-targets -- -D warnings
```

Plan and evidence:
[spike plan](../../charness-artifacts/design-studies/2026-08-28-issue-745-rust-core-spike-plan.md).
The frozen command contract is [ABI.md](./ABI.md).
