# Runbook: restore the dataset from the backups (and the quarterly drill)

The dataset can always be rebuilt from its sources alone. This runbook restores it, and the same
procedure is the **quarterly disaster-recovery drill** that proves it still works.

## Where everything lives (3-2-1)

| Asset | Copy 1 | Copy 2 | Copy 3 |
|---|---|---|---|
| Source PDF (`pdf_sha256` in `validation/reconcile-attestation.json`) | private `Algorythmos-AI/sggs-source`, release `source-pdf-v1` | object-lock bucket *(owner decision pending)* | offline drive *(owner decision pending)* |
| English translation sources (`pipeline/translations.SHA256SUMS`) | `sggs-source`, release `translations-en-v1` | — | — |
| ShabadOS database 4.8.7 (`pipeline/shabados.SHA256SUMS`) | `sggs-source`, release `shabados-database-4.8.7` | — | — |
| Corpus, database, ledger, fingerprints, history | this repository (git + LFS) | `sggs-source` release `data-v1.0.0` | every clone |

Nothing in `sggs-source` is ever replaced or deleted: a new edition or release gets a new release.

## Restore (or drill) — one command

```bash
bash scripts/data/dr_drill.sh                       # fresh clone of main, restore, rebuild, compare
bash scripts/data/dr_drill.sh --ref data-v1.0.0     # any past commit or tag
```

It needs `gh` with read access to `sggs-source`, ~5 GB free disk, and the pinned toolchain
(`pipeline/requirements-toolchain.txt`). It clones this repository fresh (nothing from your
checkout is used), restores the PDF, the translation sources and the ShabadOS database from
`sggs-source` — each verified against its committed hash — runs the full fail-hard rebuild
(reconcile char-exact, golden checks, every gate), then requires:

- the rebuilt `corpus/sggs.jsonl` byte-identical to the committed one, and
- the rebuilt database's fingerprint equal to `audit/dataset-fingerprint.json`: scripture
  (`scripture_sha256`, `t0_sha256`), every table and every FTS index.

On a different platform from the one that built the release (the Linux CI drill vs a macOS
release build), tables holding computed floating-point values may differ in the last digit;
`--allow-float-tables` reports those as WARN. Scripture, structure, text and index differences
always fail.

A restored database is then installed by the normal path: a reviewed PR, then the platform's
`dataset.lock.json` bump. Never copy a database into production by hand.

## The quarterly drill

The `dr-drill` workflow runs on a clean GitHub runner on 1 January, April, July and October (and on
demand). It needs the repository secret `SGGS_SOURCE_TOKEN`: a fine-grained token with read-only
**Contents** on `Algorythmos-AI/sggs-source`. After each run, add its RESULT line to
[`audit/dr-drills.md`](../../../audit/dr-drills.md). A failed drill is a P1: the dataset is not
recoverable as released until it passes again.
