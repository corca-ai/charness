# Issue #747 first real native artifact build (maintainer host, 2026-08-28)

> Built by lane 747-artifact via scripts/build_native_artifact.py
> (pinned toolchain, cargo --locked); non-release proof-of-path build —
> the artifact is NOT published and no native_core declaration exists.

```
== SHA256SUMS ==
9f7c8a6fddace5baa47dae898c05c2ec6144193ccec04c49119e29b4f9062a61  repograph-v8.0.0-x86_64-unknown-linux-gnu.tar.gz
== artifact.json ==
{
  "product": "charness",
  "version": "8.0.0",
  "tuple": "x86_64-unknown-linux-gnu",
  "artifact": "repograph-v8.0.0-x86_64-unknown-linux-gnu.tar.gz",
  "artifact_sha256": "9f7c8a6fddace5baa47dae898c05c2ec6144193ccec04c49119e29b4f9062a61",
  "binary": "repograph",
  "binary_sha256": "0b1e4359553ac187ef1c3948b686bf0da060dccedf041ccc87438a6fb6141aab",
  "binary_size": 3229080,
  "git_tag": null,
  "git_commit": "c00375cabd5699b8c0cb567e8764a5e32844d82a",
  "toolchain": "1.96.0",
  "rustc_version": "rustc 1.96.0 (ac68faa20 2026-05-25)",
  "cargo_lock_sha256": "22c57a48ed1af41cb22a9d4e71493e9a55ad89e821fde17d18cd149a82bde2fa"
}
```
