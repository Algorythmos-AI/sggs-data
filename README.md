# sggs-data

The verbatim corpus of **Sri Guru Granth Sahib Ji** (60,658 lines · 1,430 Angs), the SQLite/FTS5
dataset built from it, and the pipeline that builds and **proves** them.

The engineering wiki publishes this repository's docs at
[docs.gurbanisoul.com/data](https://docs.gurbanisoul.com/data/), pinned at a commit; edit them here.

> **Prime directive.** The Gurmukhi is verbatim from the source edition and is never edited,
> normalised or "corrected". Suspected issues are flagged for scholarly review, never fixed. The only
> sanctioned text transforms are registered in [`audit/editorial-ledger.jsonl`](audit/editorial-ledger.jsonl),
> and CI rejects any scripture change without a new, reviewed ledger entry.

## What is here

| Path | Contents |
|---|---|
| `corpus/sggs.jsonl` | the machine-readable corpus — the data source of truth (SHA-pinned) |
| `db/sggs.sqlite` | the dataset: lines + FTS5 indexes, translations layer, analytics, timing claims, bani registry (Git LFS) |
| `pipeline/` | PDF → corpus → DB, the gates (`reconcile.py`, `golden_test.py`, `verify_regroup.py`, `ledger_check.py`, `sggs_integrity.py`) and `pipeline/tests/` |
| `audit/` | scripture baseline, editorial ledger, dataset fingerprint |
| `validation/` | reconcile attestation, concept seeds, review packs |
| `DATASET_VERSION` | the dataset's own SemVer (independent of the apps) |

## Guarantees (enforced in CI)
- **Char-exact**: the corpus equals the source edition character for character (attested by `make reconcile`).
- **Fingerprinted**: every table and every FTS5 index matches `audit/dataset-fingerprint.json`, by content, across SQLite versions.
- **Reproducible**: the same commit + source + toolchain rebuilds identical content (`make compare-builds`).
- **Governed**: scripture text changes only through the editorial ledger.

## Use it
```bash
git lfs pull                     # the database is in Git LFS
make ci                          # the gates CI runs (no source PDF needed)
make fetch-translations          # private translation inputs (access required), then:
make rebuild PDF=/path/to/source.pdf
```

Consumers (the web/API platform and the iOS app) pin a dataset commit or `data-vX.Y.Z` release and
verify it by fingerprint before use.

Maintained by Algorythmos Pty Ltd. See [NOTICE.md](NOTICE.md) for licensing and attribution.
