# Goal Run #744 Activation Readback

Date: 2026-08-30 Asia/Seoul
Status: verified target roundtrip

## Published prerequisite

- Provider main before activation artifacts: `ad17d9ef3c4f86a3221a93169096ff37ccdccefc`
- Exact Quality Core run: <https://github.com/corca-ai/charness/actions/runs/33295938275>
- Immutable binding SHA-256: `2b5ac12a3722897bc5a11e88a881b45784adcbaab5e84840629ccd1d57421eb8`
- Frozen draft SHA-256: `eec33587771e5f6abf0e06eb32b1291f475b5b549860c96f73f89218fda44e20`

## Provider roundtrip

- Thirteen managed child bodies returned `verified-write` with byte-identical readback.
- Ten approved existing issues were added to #744 and returned `verified-write`.
- The binding-enforced graph read returned exactly 17 children: 4 closed and 13 open, with no missing or unexpected identities.
- Expected-child file and current membership SHA-256: `8c7d8a81f9fcb8d66977cca5ee569a8d8bbdd4632508f06fe980dd92a8f312b8`.
- The parent body update preserved the exact live human body and appended one valid Goal Run metadata block.
- A clean `goal_run_pickup.py --objective '/goal #744'` returned `verified-read` and selected #758 from parent cursor revision 1.

Every write and graph read has a paired started/terminal receipt under `observations/`. This record does not claim completion of any currently open child.

## First execution proof

Mutation Tests was dispatched at the exact prerequisite main SHA as run <https://github.com/corca-ai/charness/actions/runs/33296181601>. Its result is not claimed here while the run is in progress.
