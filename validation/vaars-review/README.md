# Vaar anatomy review — dataset 1.2.0

`pipeline/build_vaars.py` now reads each Vaar's structure from the print. Only the `vaars` and `vaar_units` tables change, plus the `meta` and `analytics_meta` stamps. `lines` and every other table are content-identical (`compare_builds.py`). Scripture is byte-identical (`diff_scripture.py`: 60,658 → 60,658 rows, no column changed).

As printed: **471 pauris**, each closing with its own ॥N॥ (checked unit by unit), and **972 saloks** (was 955). `vaar_units`: 1,426 → 1,443.

| vaar | raag | Angs | pauris | saloks | changed |
|---|---|---|---|---|---|
| 1 | sireeraag | 83–91 | 21 | 43 | title; last pauri 44→6 lines |
| 2 | maajh | 137–150 | 27 | 63 | — |
| 3 | gaurhee | 300–317 | 33 | 68 | — |
| 4 | gaurhee | 318–323 | 21 | 42 | last pauri 338→5 lines |
| 5 | aasaa | 462–475 | 24 | 59 | title |
| 6 | goojaree | 508–517 | 22 | 44 | — |
| 7 | goojaree | 517–524 | 21 | 42 | last pauri 95→8 lines |
| 8 | bihaagarhaa | 548–556 | 21 | 42 | saloks 41→42 |
| 9 | vadahans | 585–594 | 21 | 43 | — |
| 10 | sorath | 642–653 | 29 | 58 | — |
| 11 | jaitasaree | 705–710 | 20 | 20 | — |
| 12 | soohee | 785–792 | 20 | 47 | title; last pauri 128→5 lines |
| 13 | bilaaval | 849–855 | 13 | 27 | — |
| 14 | raamakalee | 947–956 | 21 | 52 | title; saloks 53→52 |
| 15 | raamakalee | 957–966 | 22 | 44 | — |
| 16 | raamakalee | 966–968 | 8 | 0 | — |
| 17 | maaroo | 1086–1094 | 22 | 47 | — |
| 18 | maaroo | 1094–1102 | 23 | 69 | saloks 52→69; last pauri 91→8 lines |
| 19 | basant | 1193–1193 | 3 | 0 | — |
| 20 | saarang | 1237–1251 | 36 | 74 | — |
| 21 | malaar | 1278–1291 | 28 | 58 | — |
| 22 | kaanarhaa | 1312–1318 | 15 | 30 | last pauri 13→6 lines |
`changes.csv` has the same data with the before and after titles in full.

## What was wrong, and the rule now
- **Titles.** The title was the title composition's first header line, so four Vaars were titled by the ੴ invocation. It is now the heading run's non-ੴ line(s), verbatim, joined by a space. The final danda is trimmed, as before.
- **ਧੁਨੀ rubric.** Ramkali M3's `ਜੋਧੈ ਵੀਰੈ ਪੂਰਬਾਣੀ ਕੀ ਧੁਨੀ ॥` (line 40605, `is_header=0`) became a one-line salok. A ਧੁਨੀ line printed before the first label is now heading.
- **Labels.** `ਡਖਣੇ ਮਃ ੫ ॥` was not a salok label, so Maru M5's 17 inner ਡਖਣੇ saloks were swallowed by the pauris before them. `ਮਰਦਾਨਾ ੧ ॥` (Bihagara) is not flagged as a header. A label now starts with ਸਲੋਕ / ਸਲੋਕੁ / ਮਃ / ਮਹਲਾ / ਡਖਣੇ / ਡਖਣਾ / ਮਰਦਾਨਾ, carries no ॥N॥, and is either a header or a rubric of at most three words.
- **The end of a Vaar.** The final pauri ran on into the composition that follows: Bhagat bani of the same raag, up to 338 lines in Gauri M5. It now ends with its own composition.
- **`comp_id` was not stale.** It always matched `lines`. The apparent mismatch was the run-on final pauri.

## For the scholar review (G3)
- Four pauris carry an explicit `ਪਉੜੀ ਮਃ ੫ ॥` label inside another Guru's Vaar: Gauri M4 pauris 30 and 31 (Ang 316), Sarang pauri 35 (Ang 1251), and Malar pauri 27 (`ਪਉੜੀ ਨਵੀ ਮਃ ੫ ॥`, Ang 1291). The data attributes them to Guru Arjan Dev Ji (M5), from the printed label.
- Line 40605, the ਧੁਨੀ rubric printed without a header flag. Flagged; not changed.

## How this build was made
The PDF and the ~5 GB rebuild were not available here, so only the two tables were rebuilt, in place on the committed 1.1.0 DB.

Running the *old* builder the same way reproduces the committed 1.1.0 DB: all 59 tables identical by `compare_builds.py`. So the in-place step is content-equivalent to step 125 of `rebuild_all.sh`.

`SOURCE_DATE_EPOCH` is the builder commit's time. `meta.version` / `meta.built` were updated as `build_db.py` would set them. The next full rebuild or DR drill will re-stamp the other builders' `analytics_meta` times; their content does not change.
