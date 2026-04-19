# Release Source Snapshot

The public `Option 1` deliverable is regenerated from `authoritative-summary.csv` in this directory.

- This CSV is intentionally tracked in git so `make release` does not depend on the large local `results/inspect/` tree.
- Maintainers with the original raw full-run folders can refresh this snapshot with `make refresh-authoritative`.
- The raw `results/inspect/` directories remain useful for local provenance and debugging, but they are not required for public release regeneration.
