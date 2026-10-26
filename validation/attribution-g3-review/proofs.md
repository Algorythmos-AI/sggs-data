# Proofs: scripture byte-identical (dataset 1.2.0 → 1.3.0)

Baseline: dataset 1.2.0 (`main` c36e317, `db/sggs.sqlite` sha256 `ff5e5de7…`). The source PDF matches
the reconcile attestation (sha256 `294a0b99…`). Toolchain: `/usr/bin/python3` 3.9.6 with
PyMuPDF/numpy/scipy (`make doctor`).

## Done

### 1. Corpus extraction with the new post-pass

```
/usr/bin/python3 pipeline/build_corpus.py <PDF> new.jsonl
```

This compares the new corpus with the committed 1.2.0 corpus, field by field, for all 60,658 records:

```
section 791 · comp_id 29 · line_no 29 · is_header 3 · author 2     (no other field differs)
```

`gurmukhi`, `text`, `markers`, `translit`, `fl_g`, `fl_r`, `skeleton`, `ang`, `pdf_page`, `is_rahao`,
`raag`, `comp_type` and `ghar` are identical for every id.

### 2. Reconcile and golden (`make reconcile`, which refreshed `validation/reconcile-attestation.json`)

```
pdf chars   : 1,643,385
corpus chars: 1,643,385
RECONCILED: corpus == source, character for character.
golden PASS
```

### 3. Byte-level scripture diff on the database (`scripts/data/diff_scripture.py`)

Both base databases (`pipeline/build_db.py`: `lines` + FTS + aggregates) are built from the 1.2.0 corpus
and the 1.3.0 corpus:

```
rows: 60658 -> 60658
  author             changed in      2 rows (allowed; e.g. id 23470)
  comp_id            changed in     29 rows (allowed; e.g. id 30081)
  is_header          changed in      3 rows (allowed; e.g. id 30081)
  line_no            changed in     29 rows (allowed; e.g. id 30081)
  section            changed in    791 rows (allowed; e.g. id 58297)
RESULT: PASS — only allowed columns changed; scripture byte-identical
```

### 4. Integrity fingerprint (`pipeline/sggs_integrity.py`) on the same two databases

| | 1.2.0 | 1.3.0 |
|---|---|---|
| `scripture_sha256` (id + gurmukhi, the iOS manifest's definition) | `0eff4bae…` | **identical** |
| `t0_sha256` (id, ang, gurmukhi, text, markers) | `2c6289f1…` | **identical** |
| `fts_index.fts` (the scripture full-text index) | | **identical** |

The tables whose content differs are all metadata, or derived from `is_header`/`author`:

- `lines`: the five columns above.
- `authors`: 35 → 36 rows.
- `sections`: 13 → 15 rows.
- `raags`: Dhanasari `n_shabads` 105 → 108.
- `word_freq`: four label words leave it as their lines become headings.

`downstream.md` has the numbers.

### 5. ShabadOS authorship gate (`pipeline/crosscheck_authors.py`, ShabadOS 4.8.7)

```
1.2.0: aligned 58771 lines with ShabadOS; author agrees on 58584 (99.6818%)
1.3.0: aligned 58771 lines with ShabadOS; author agrees on 58585 (99.6835%)
crosscheck: PASS -- every disagreement with ShabadOS is a reviewed, flagged attribution
```

The flag `surdas-tuk` is removed, because line 53935 now agrees. Every other flag covers the same lines
as before.

### 6. Tests and lint

`python3 -m unittest discover -s pipeline/tests` ran 80 tests. All pass except the two
`test_docs_facts` checks that read `db/sggs.sqlite`: the schema page already states the 1.3.0 counts
(4,530 / 5,383), and the committed database is still the 1.2.0 build. `ruff check .` passes.

## Pending: the full database rebuild

`make rebuild` (`pipeline/rebuild_all.sh`) refuses to start below 5 GiB free. The machine had 4.1–4.9 GiB
free while this pack was prepared, because other builds were running. The rebuild aborted at pre-flight
with nothing written. When there is room, run:

```bash
cp db/sggs.sqlite /tmp/pre.sqlite
make rebuild PDF=../Siri-Guru-Granth-Sahib-in-Gurmukhi-with-Index.pdf
python3 scripts/data/diff_scripture.py /tmp/pre.sqlite db/sggs.sqlite \
  --allow author section is_header comp_id line_no source_category stanza_index pada_total
python3 scripts/data/compare_builds.py /tmp/pre.sqlite db/sggs.sqlite      # lists every derived table that moved
python3 pipeline/verify_regroup.py --invariants db/sggs.sqlite            # 4,530 compositions
# re-baseline as a conscious act, after the proofs (runbook: docs/process/runbooks/rebuild-db.md)
python3 pipeline/timing/step0_baseline.py --db <pretiming-copy> --force --skip-backup
python3 pipeline/data_quality.py --write-baseline  # comp_id count/max/gaps move by design
make ci
python3 scripts/data/g3_attribution_pack.py /tmp/pre.sqlite db/sggs.sqlite database.sqlite validation/attribution-g3-review
```

Then commit the DB (Git LFS), `MANIFEST.json`, `audit/` and the regenerated pack.
