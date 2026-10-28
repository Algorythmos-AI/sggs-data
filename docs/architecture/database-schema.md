# Database Schema & the `comp_id` Model

`db/sggs.sqlite` (~104 MiB, Git LFS) is opened read-only (`mode=ro&immutable=1`,
`query_only`). 33 real tables + FTS5 shadow tables, in five layers.

## `lines` — the verse table (60,658 rows)
One display line each: `id`, `ang` (1–1430), `pdf_page`, `raag`, `section`,
`author`, `comp_type`, `ghar`, **`comp_id`**, `line_no`, `is_rahao`, `is_header`,
`markers`, `gurmukhi` (verbatim), `text` (clean), `translit`, `translit_norm`
(phonetic fold, DB-built), `fl_g`/`fl_r`, `skeleton`, `stanza_index`, `pada_total`,
`source_category`.

## `comp_id` groups a whole composition — heading run included

A composition (a shabad, salok, pauri, vaar unit) is the set of `lines` sharing a
`comp_id`. **A run of consecutive heading lines opens ONE composition together with
the body it introduces** — a raag/title line, the `ੴ` invocation, and a
`ਸਲੋਕੁ ਮਃ` label all carry the same `comp_id` as the verses they precede.

```mermaid
flowchart TB
    accTitle: comp_id before and after v1.1.0
    accDescr: Before v1.1.0 a heading line and the invocation after it each had their own comp_id, orphaned from the composition they open; since v1.1.0 the heading run shares the comp_id of the composition, and the vacated ids stay gaps.
    subgraph before["Before v1.1.0 (the bug)"]
      t1["ਟੋਡੀ ਮਹਲਾ ੫ ਘਰੁ ੨ ਚਉਪਦੇ · comp 2844 (orphan)"]
      i1["ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ · comp 2845"]
      v1["verses… · comp 2845"]
      i1 --- v1
    end
    subgraph after["v1.1.0 (fixed)"]
      t2["ਟੋਡੀ ਮਹਲਾ ੫ ਘਰੁ ੨ ਚਉਪਦੇ · comp 2845"]
      i2["ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ · comp 2845"]
      v2["verses… · comp 2845"]
      t2 --- i2 --- v2
    end
```

Before v1.1.0 every heading line got its own `comp_id`, so a title line followed
by a separate `ੴ` invocation became a one-line "orphan" composition that
`/api/shabad/{comp_id}` never fetched — the sheet dropped the printed title. The
fix (`build_corpus.py` post-pass 1b) folds each heading run into the composition it
opens.

### Key invariants (checked by `verify_regroup.py`)
- The run adopts its **last** heading's `comp_id` → **no body line's `comp_id`
  ever changes**, so saved bookmarks, deep links, and analytics keyed on `comp_id`
  stay valid.
- Vacated ids become **permanent gaps**: distinct compositions **4,531**,
  `max(comp_id)` **5,384** (the v1.1.4 build demoted 233 verses mis-flagged as headings and
  burned the ids they had opened, up to 5,380; dataset 1.3.0 issued 5,381–5,383 to the three
  shabads on Ang 695 that a printed Bhagat label opens, and 5,384 to the single Surdas line on
  Ang 1253, which the G3 ruling of 2026-10-28 makes a composition of its own; `pipeline/tests/test_docs_facts.py`
  holds these numbers to the database).
- The one sanctioned exception to "no body line's `comp_id` changes" is an **approved
  `opens` entry** in `pipeline/structure_ledger.json` (`pipeline/structure.py`, post-pass 5):
  a printed label that was stored as a verse becomes the heading of its own composition, and
  its shabad's lines move to a new id above every id ever issued. Each entry is reviewed at G3;
  the old id keeps the shabad it opened with (Ang 695: 2749 is Bhagat Trilochan Ji's alone). A
  `stands` entry moves verse to a new id in the same way without making it a heading (Ang 1253: the
  Surdas line, 5,384). `comp_id` 1 is a gap (Mool Mantar folds into Japji, `comp_id` 2).
  `/api/shabad/{gap}` → 404.
- Every composition's first line is a heading, except composition 5,384 (the single Surdas line,
  which has no printed heading); no heading follows a body line.
- Exactly **3** header-only compositions remain — the closing rubrics `ਜੁਮਲਾ`,
  `ਦੁਤੁਕੇ`, `ਏਹੁ ਸਲੋਕੁ ਆਦਿ ਅੰਤਿ ਪੜਣਾ` (`TRAILING_RUBRICS`), which belong to the
  *preceding* unit and are flagged for scholarly review.

## Layers (grouped)
- **Scripture core:** `lines`, `raags`, `sections`, `authors`, `vaars`, `vaar_units`, `shabd_raag_map`, `shabd_musical_markers`, `shabd_structural_form`, `shabd_poetic_genre`.
- **Search:** `fts`, `fts_en`, `fts_shabad`, `fts_tri`, `variants`, `word_freq`, `canon_tokens`.
- **Translations:** `translations`, `sources`.
- **Analytics:** `concepts`, `concept_lines`, `theme_network`, `theme_fingerprint`, `author_analytics`, `raag_analytics`, `author_distinctive_terms`, `author_resonance`, `line_neighbors`, `shabad_neighbors`.
- **Knowledge / meta:** `raag_timing_claims`, `timing_sources`, `timing_migrations`, `meta`, `analytics_meta`.

## Gotchas
- `comp_type` is known-mislabeled in places; it is suppressed at the display layer. Prefer `comp_id`/`section`.
- `author` comes from the printed evidence (headings, ਮਃ labels, pen-names, shabad numbering) via the
  attribution post-pass; see [attribution.md](attribution.md). Japji is Guru Nanak Dev Ji's (ledger entry
  `japji`); contested attributions (Mardana, Raagmala, Bhatt splits, Surdas) are recorded, not changed.
- `line_neighbors` is built with a nondeterministic random projection — its row *order* varies across rebuilds (its content is what matters).
