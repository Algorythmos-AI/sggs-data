# Proofs: scripture byte-identical (dataset 1.2.0 → 1.3.0)

- **Baseline:** dataset 1.2.0 (`main` c36e317), `db/sggs.sqlite` sha256 `ff5e5de7…`.
- **New build:** dataset 1.3.0, `db/sggs.sqlite` sha256 `003cae57…`.
- **Source PDF:** matches the reconcile attestation (sha256 `294a0b99…`).
- **Toolchain:** `/usr/bin/python3` 3.9.6 with PyMuPDF/numpy/scipy (`make doctor`). The translation and
  ShabadOS inputs are verified against `pipeline/*.SHA256SUMS`.

## 1. The full gated rebuild: `make rebuild` (`pipeline/rebuild_all.sh`)

```
attribution: 1047 lines re-attributed from printed evidence, 3 flagged for scholarly review
structure: 852 field changes from approved structure-ledger entries
RECONCILED: corpus == source, character for character.
ALL GOLDEN TESTS PASS
crosscheck: PASS -- every disagreement with ShabadOS is a reviewed, flagged attribution
  additive integrity: existing tables row-identical, scripture intact ✓
[vaars] roster OK — matches canonical 22 Vaars exactly
GUARD (banis) PASS
integrity gate: PASS
installed db/sggs.sqlite sha256=003cae578902f2677ea1e18a888f91be1fa32fb1256f07c2cced7f52f7122f91
DONE — db/sggs.sqlite rebuilt, gated and fingerprinted (DATASET_VERSION 1.3.0)
```

The rebuilt `corpus/sggs.jsonl` (sha256 `0e228fea…`) and `corpus/by-raag/` are byte-identical to the
files committed earlier on this branch. Those came from `build_corpus.py` and `build_db.py` alone.

Compared field by field with the 1.2.0 corpus (60,658 records), only these fields change:

```
section 791 · comp_id 29 · line_no 29 · is_header 3 · author 2
```

`gurmukhi`, `text`, `markers`, `translit`, `fl_g`, `fl_r`, `skeleton`, `ang`, `pdf_page`, `is_rahao`,
`raag`, `comp_type` and `ghar` are identical for every id.

## 2. Byte-level scripture diff: `scripts/data/diff_scripture.py`

```
python3 scripts/data/diff_scripture.py pre-1.2.0.sqlite db/sggs.sqlite \
  --allow author section is_header comp_id line_no source_category stanza_index pada_total
rows: 60658 -> 60658
  author             changed in      2 rows (allowed; e.g. id 23470)
  comp_id            changed in     29 rows (allowed; e.g. id 30081)
  is_header          changed in      3 rows (allowed; e.g. id 30081)
  line_no            changed in     29 rows (allowed; e.g. id 30081)
  pada_total         changed in      3 rows (allowed; e.g. id 30081)
  section            changed in    791 rows (allowed; e.g. id 58297)
  source_category    changed in      1 rows (allowed; e.g. id 23470)
  stanza_index       changed in      3 rows (allowed; e.g. id 30081)
RESULT: PASS — only allowed columns changed; scripture byte-identical
```

Three of these columns are derived:

- `source_category` rolls up `author`: line 23470 moves from Gurus to Bhagats. The Surdas line stays
  Bhagats.
- `stanza_index` and `pada_total` are counted per composition: they change on the three new heading lines.

## 3. Integrity fingerprint: `audit/dataset-fingerprint.json`, 1.2.0 vs 1.3.0

| | |
|---|---|
| `scripture_sha256` (id + gurmukhi; the iOS manifest's definition) | **identical** |
| `t0_sha256` (id, ang, gurmukhi, text, markers) | **identical** |
| `fts_index.fts` (scripture full-text) | **identical** |
| `fts_index.fts_en` (English) | **identical** |
| `fts_index.fts_tri`, `fts_index.fts_shabad` | changed: these index **verse** lines grouped by composition, so the three labels leave them and composition 2749 splits |

## 4. Every table that moved: `scripts/data/compare_builds.py`

30 of 59 tables differ. Each one is explained by the five metadata changes:

- `lines`: the columns in §2.
- `authors`, `author_analytics` and `author_facts` gain a row (35 → 36). `author_resonance` has 670 → 679
  rows. `author_distinctive_terms` and `theme_fingerprint` (2,315 → 2,316) change because they are
  computed per author.
- `sections` has 13 → 15 rows. `raags` changes because Dhanasari's `n_shabads` goes from 105 to 108.
  `raag_analytics` counts per-raag compositions.
- `shabd_raag_map`, `shabd_musical_markers` and `shabd_structural_form` each have 4,527 → 4,530 rows (one
  row per composition). `shabad_neighbors` has 43,800 → 43,830 rows, and `theme_network` recomputes its
  composition-level co-occurrence.
- `fts_tri` (55,511 → 55,508 rows), `fts_shabad` (4,524 → 4,527), `line_neighbors` (532,227 → 532,212),
  `word_freq` and `variants` index **verse** lines only. The three labels that become headings leave
  them. In `variants`, only the frequencies of `ਧੰਨਾ`, `ਪੀਪਾ` and `ਸ੍ਰੀ` move (6 rows), and no variant is
  added or removed.
- `meta`, `analytics_meta`, `sources` and `timing_migrations` carry the version and build-date stamps
  (`SOURCE_DATE_EPOCH` = this branch's commit time).

These tables are **content-identical** to 1.2.0: `vaars` (22), `vaar_units` (1,443), `banis`,
`bani_lines`, `extra_lines`, `translations`, `fts`, `fts_en`, `concepts`, `concept_lines`, `canon_tokens`,
`author_mentions`, `author_dialogues` and `shabd_poetic_genre`.

## 5. Structural invariants: `pipeline/verify_regroup.py --invariants db/sggs.sqlite`

```
  ok   distinct comps == 4530 (got 4530)
  ok   every comp's first line is a header (0 bad)
  ok   no header follows a body line within a comp (0 bad)
  ok   header-only comps == the 3 trailing rubrics
  ok   line_no contiguous within every comp (0 bad)
RESULT: PASS — structural invariants hold on the current DB.
```

## 6. ShabadOS authorship gate: `pipeline/crosscheck_authors.py`, ShabadOS 4.8.7

```
1.2.0: aligned 58771 lines with ShabadOS; author agrees on 58584 (99.6818%)
1.3.0: aligned 58771 lines with ShabadOS; author agrees on 58585 (99.6835%)
crosscheck: PASS
```

The flag `surdas-tuk` is removed, because line 53935 now agrees. Every other flag covers the same lines
as before.

## 7. Re-baselines (after the proofs above, as a deliberate step)

Before re-baselining, `guard_scripture.py` failed on exactly the tables in §4. `data_quality.py` failed on
exactly the expected counts:

```
comp_id: count 4530 (baseline 4527) · max 5383 (5376) · gaps 853 (849) · headings 5150 (5147)
```

There are 4 more gaps because the burned ids 5377–5380 now lie below the new maximum. No id was freed.
The re-baselines were then recorded with `scripts/data/rebaseline_pretiming.sh` (which writes
`audit/scripture-baseline.json`) and `pipeline/data_quality.py --write-baseline` (which writes
`audit/data-quality-baseline.json`).

## 8. `make ci`

```
ledger check: PASS — 4 editorial rules == code, 11 applications; 0 scripture line(s) changed vs c36e317
data quality: PASS — 60658 lines, 4530 compositions (853 gaps), 5150 headings
GUARD (banis) PASS
Ran 80 tests — OK (skipped=1)
make ci: PASS
```

`ruff check .` and `gitleaks detect --no-git` are clean.
