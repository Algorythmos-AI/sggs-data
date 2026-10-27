# Independent audit: dataset 1.3.0 and the G3 review (PR #17, PR #18)

- **Prepared:** 2026-10-27, on branch `audit/g3-hardening`, which is based on PR #17's head `aeac8fd`.
- **What this is:** an engineering and evidence audit. It is not a scholarly ruling, and nothing here
  records one.

## 0 · Where things stand

| State | Status |
|---|---|
| 1. Engineering implementation (approval gate, tests, CI wiring) | **Complete** on the local branch. Not pushed. |
| 2. Automated validation | **Complete locally.** 112 tests pass (1 skipped: iOS app not in this repo). Every `make ci` gate passes except `g3-release`, which fails **by design**: 8 G3 entries have no ruling. Full rebuild from the PDF: pass. |
| 3. Evidence pack | **Verified** to the extent in § 2. The limits are listed there and in § 6. |
| 4. Scholarly decision | **Pending.** No ruling has been given on A-07, A-08, A-10, A-11 or Ang 323. |
| 5. Release readiness | **Not established.** The release check fails until the rulings are recorded. Consumer-side risks (`RISKS.md` G-4, C-1, C-2) are open. |
| 6. Merge authorised | **No.** PR #17 and PR #18 stay draft. Nothing was merged, pushed or released, and no remote setting was changed. |

## 1 · What changed in this branch, and why

| File | Change |
|---|---|
| `pipeline/g3_gate.py` (new) | One validator for both ledgers, with a closed set of statuses and a complete-ruling requirement bound to each entry's hash. Also provides `--release-check` and `--hash`. |
| `pipeline/attribution.py`, `pipeline/structure.py` | Apply only what the gate lets through. `load_ledger()` validates the file, and a missing ledger is now an error. Rule E fails on ids that are not in the corpus. |
| `pipeline/attribution_ledger.json`, `pipeline/structure_ledger.json` | The seven unruled G3 entries go from `approved` to `held`. Only `status` changes. |
| `pipeline/build_corpus.py` | Log lines only: a `HELD — not a release` banner that names the held entries. |
| `pipeline/tests/test_g3_gate.py` (new) | 29 tests: invalid and complete rulings, statuses, the committed ledgers, and the corpus-to-status binding. |
| `pipeline/tests/test_g3_pack.py` (new) | The pack must match the committed DB and the G3 entries, and every `` `…` *(line N)* `` quote must equal corpus line N exactly. |
| `pipeline/tests/test_structure.py`, `test_attribution.py` | Fixtures use `held` entries with a `g3` block, and `held` is now an allowed status. No assertion was weakened. |
| `scripts/data/g3_attribution_pack.py` | Writes `pack-inputs.json`, recording which inputs the pack was built from. |
| `.github/workflows/data-ci.yml`, `Makefile` | `g3_gate.py --release-check` runs in the required `integrity` job and in `make ci` (`g3-release`). |
| `validation/attribution-g3-review/` | New: `DECISIONS.md`, `EVIDENCE-LEDGER.md`, `CONTRADICTIONS.md`, `RISKS.md`, `SIGN-OFF.md`, this report and `pack-inputs.json`. `README.md` and its template are revised. `RECOMMENDATIONS.md` (PR #18) is **not** edited; its corrections are in § 2 below. |

`corpus/`, `db/`, `MANIFEST.json`, `audit/` and every Gurmukhi character are **unchanged**:
`git diff aeac8fd -- corpus db MANIFEST.json audit` is empty.

## 2 · Independent findings

### 2.1 What was verified directly

- **The printed source.** These PDF pages were read as images: 748 (Ang 695), 1306 (Ang 1253), 577
  (Ang 524), 376 (Ang 323), 1417 (Ang 1364) and 1430 (Ang 1377). The PDF's own text lines were also
  read for Angs 323, 517, 524, 654 and 1253. `pdf_page` is 1-based, and the printed Ang number at the
  head of each page matches the corpus.
- **ShabadOS 4.8.7.** The sha256 `d8e07134…` matches `pipeline/shabados.SHA256SUMS`. Its records for
  every line the items touch were read with our own SQL, and the commentary fields were read raw.
- **Both datasets.** 1.2.0 (`ff5e5de7…`, at `main` `c36e317`) and 1.3.0 (`003cae57…`) were compared cell
  by cell (§ 3).
- **The Encyclopaedia of Sikhism:** see § 2.4.

### 2.2 PR #17 and PR #18 claims: confirmed, corrected or disproved

**Confirmed** (detail and locations in `EVIDENCE-LEDGER.md`):

- **Sahib Singh** (as transcribed in ShabadOS 4.8.7):
  - both A-07 notes, on 53935 and 53943;
  - the Pipa note on 30098;
  - his heading gloss on 58273.

  The quotes differ from ShabadOS only in how ਸ਼ is encoded (U+0A38+U+0A3C against U+0A36). The two are
  canonically equivalent.
- **Faridkot:**
  - on 53935, and its preface on 53934;
  - its shabad introductions on 30080, 30091 and 30098. The anchors are correct, because Faridkot puts
    each introduction on the line before the shabad it introduces;
  - `॥੨੧॥੧॥੨॥ਸੁਧੁ` on 23469.
- **ShabadOS and BaniDB:**
  - BaniDB 4531 is shared by Parmanand's shabad and the Surdas line;
  - 2639–2642 for the four Ang 695 shabads;
  - ShabadOS files the 524 and 323 headings under Kabir.
- **No source read credits line 53935 to Bhagat Namdev Ji.**
- **The A-08 boundaries** match ShabadOS line for line (24, 494 and 297 lines).
- **The Gurus' saloks** stay inside the A-08 collections.
- **The printed counts** on Angs 695, 1253, 1364 and 1377 are as stated.

**Corrected:**

1. **`5FC` and `6AM` are ShabadOS *shabad* ids, not line types.** The line types are 1 Manglacharan,
   2 Sirlekh, 3 Rahao and 4 Pankti. Line 53935 is line `B8PD`, type Pankti.
2. **Faridkot's four Bhagats on 58296** are named as the Chaubole's *speakers* ("ਇਨ ਚਾਰੋਂ ਭਗਤੋਂ ਕੇ
   ਬਚਨ"). Faridkot does not say "addressed to". That wording is the EoS's (II p. 335), so the two sources
   disagree.
3. **Sahib Singh's running summary of Kabir's saloks** is attached to line 58298, not 58297.
4. **Farid's collection ends on Ang 1384** (line 59087), not Ang 1385. "1385" is only ShabadOS's
   section-level page metadata.
5. **"Eleven of the twelve Bhagat-run headings"** should read **11 of 13**: 12 of 14 if Suhi line 33831
   is counted. In 1.2.0 **two** headings carried Guru Arjan Dev Ji, 23470 and 14771. Option (c) of
   A-11 ("no author on any Bhagat-run heading") would touch 13 or 14 lines, not 12.
6. **PR #18 lists Bhai Vir Singh and Rattan Singh Jaggi** among ShabadOS's Granth commentaries. For the
   Granth, ShabadOS 4.8.7 has six translation sources:
   - Sant Singh Khalsa;
   - Manmohan Singh (English and Punjabi);
   - SikhNet;
   - the Faridkot Teeka;
   - Sahib Singh.

   In ShabadOS, Bhai Vir Singh belongs to Vaaran Bhai Gurdas and Jaggi to the Dasam Granth.
7. **PR #18 gives its confidence as "High"** for every item. Its commentaries are read through one
   transcription, and its ShabadOS and BaniDB evidence is one source family. "High" overstates the
   independence of that evidence. `DECISIONS.md` gives a label per question instead.

**Disproved:**

1. **"All the sources read agree on question 3"** (that lines 53936–53943 are Guru Arjan Dev Ji's).
   - ShabadOS files that shabad (`FHM`, STTM 4532) under **Bhagat Surdas Ji**.
   - Faridkot's gloss of 53943 opens "ਸੂਰਦਾਸ ਜੀ ਕਹਿਤੇ ਹੈਂ".
   - Only Sahib Singh, and Faridkot's preface, say it is the Guru's.
   - The EoS contradicts itself: IV p. 288 credits the Guru; I p. 314 says "a hymn from Sūr Dās".
2. **The A-10 fix "matches how the dataset already treats bare labels such as `ਨਾਮਦੇਵ ॥`".** The only
   `ਨਾਮਦੇਵ ॥` (line 50285, Ang 1167) is a **verse inside Bhagat Ravidas Ji's composition 4426**, in both
   1.2.0 and 1.3.0. That is the A-10 defect, unfixed. A possible further instance is `ਕਬੀਰੁ ॥`
   (line 47529).
3. **"Line 23470 holds two things … the corpus never splits a printed line"** (PR #17, A-11).
   - In the print, `ਸੁਧੁ` is the last word of the Vaar's final printed line. The Bhagat-run heading is a
     separate centred line.
   - Both the page image and the PDF's own text lines show this, on Angs 524 and 323 and also 517
     and 654.
   - It is the corpus record that joins them. At every other place `ਸੁਧੁ` is a record of its own.
   - The A-11 attribution question exists because of this join (`DECISIONS.md` A-11, reading (d)).

**Evidence PR #18 left out:**

- **Sahib Singh on 53935:** the following shabad was composed "to explain the one line above". This
  bears on A-07's composition question, reading (c).
- **Sahib Singh and Faridkot on 14770** (Ang 323): `ਸੁਧੁ ਕੀਚੇ` means "to be corrected". Sahib Singh adds
  that in the Kartarpur Bir these words stand outside the margin and have no connection with the Bani.
  His Kartarpur statement is Unverified here.
- **Faridkot on 58296:** "ਵਾ ਏਹ ਸਲੋਕ ਪਤੰਗ ਭਗਤ ਨੇ ਕਹਾ ਹੈ".

### 2.3 New observations about the print

- **The source PDF is a typeset, run-on edition.** Bare Bhagat labels, `ਰਹਾਉ ॥` and `ਮਃ` labels run
  inline. Only principal headings are centred. So for A-10, layout cannot settle heading versus verse.
- **On Ang 1253, line 53935 is printed on a line of its own**, between Parmanand's closing ॥੩॥੧॥੬॥ and
  the centred `ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ ॥` heading.

**Flagged for review, outside these items; nothing changed:**

- **Farid's collection.** Saloks ॥੩੨॥, ॥੧੨੧॥ and ॥੧੨੪॥ are signed `ਨਾਨਕ`/`ਨਾਨਕਾ`, with no printed
  `ਮਃ` label, and are credited to Sheikh Farid Ji (lines 58866, 59067, 59073). ShabadOS and the
  commentaries were not read for them.
- **A spacing difference in a scripture record.** Line 14773 reads `…ਚਉਪਦੇ ੧੪ ॥`, with a space before
  `॥`. The PDF's text layer reads `…ਚਉਪਦੇ ੧੪॥`. `reconcile.py` ignores spaces by design, so its
  char-exact proof does not cover spacing. This needs a human look, as a possible extraction artefact.
  It is **not** corrected here.
- **The `ਸੁਧੁ` join** (§ 2.2, disproved 3) is an extraction behaviour at four places (lines 14771, 23136,
  23470, 28417). Changing record boundaries would change those lines' `gurmukhi` field. That needs a
  logged transform, reconcile and a scholar's review, so it is not proposed here.

### 2.4 Encyclopaedia of Sikhism

- **Editions.** Each volume's edition was read from its own imprint page. They differ:
  - I: 4th ed. 2002, ISBN 81-7380-100-2;
  - II: 3rd ed. 2011, 81-7380-204-1;
  - III: 3rd ed. 2011, 81-7380-349-8;
  - IV: 2nd ed. 2004, 81-7380-530-X.

  A single "Third edition, 2011" citation would be wrong for vols. I and IV.
- **Entries read on the image by the lead auditor:**
  - IV p. 288 (SŪRDĀS);
  - IV p. 240 (SRĪ GURŪ GRANTH SĀHIB);
  - I p. 314 (BHAGAT BĀṆĪ);
  - I p. 567 (DHANNĀ);
  - II p. 335 (JAMĀL).

  Eight further entries were read on the image by an audit agent only, and are marked so.
- **What the EoS supports:**
  - Surdas for line 53935;
  - the A-08 divisions ending on Ang 1384.
- **What the EoS does not settle:**
  - **Who composed lines 53936–53943:** it contradicts itself. IV p. 288 says Guru Arjan composed the
    hymn; I p. 314 says "one line and a hymn from Sūr Dās".
  - **Who the Chaubole's four are:** it says they are "addressed to" the four, while Faridkot says the
    words are theirs.
- **Its hymn and salok counts are mutually inconsistent** (Dhanna 2 against 3; Kabir 239 against 237;
  Farid 112 against 120). They are not used as evidence.
- **PR #18** could not open the EoS and cited it "as in the roster". These pages were not available to
  it.

### 2.5 Identifiers

- **A-07 to A-11, R-21, L-05a and M-P09** are defined in gurbani-soul-ios `docs/review/g3-1.4.9/README.md`
  (blob `fa37988…`, commit `200cf10`). L-05a and M-P09 are not used by any item here.
- **"A-11 / Ang 323"** (PR #18: "A-11b") is not in that list.
- **R1–R4 are editorial text-repair rules** (`audit/editorial-ledger.jsonl` lines 11–14). They are not
  review items, and have nothing to do with these four decisions.
- Definitions are in `EVIDENCE-LEDGER.md` § Identifiers.

## 3 · Data integrity: baseline, commands and results

**Baseline:**

- dataset 1.2.0 = `main` `c36e3172`;
- `db/sggs.sqlite` sha256 `ff5e5de7…`, which equals sggs-platform's `dataset.lock.json` pin.

**Candidate:** PR #17 `aeac8fd`: DB `003cae57…`, corpus `0e228fea…`.

| # | Command | Result |
|---|---|---|
| 1 | `make rebuild PDF=…` (`/usr/bin/python3` 3.9.6 with PyMuPDF, translations and ShabadOS restored and sha-verified), run with the gate code in place and the seven entries `held` | Exit 0. Reconcile: "corpus == source, character for character". All golden tests pass. ShabadOS crosscheck: PASS. Integrity gate: PASS. Corpus `0e228fea…` is **identical**. DB `cdb0b7c2…`. |
| 2 | `compare_builds.py` (committed DB against rebuild 1) | 57 of 59 tables identical. Only `analytics_meta` and `timing_migrations` differ, and both hold build timestamps. Cause: `SOURCE_DATE_EPOCH` defaults to the HEAD commit time, while the committed DB was built at `8bad6f5`. |
| 3 | `SOURCE_DATE_EPOCH=1793005527 make rebuild …` | DB `003cae57…`: **byte-identical** to the committed 1.3.0 DB. Corpus identical. This proves that the `approved` → `held` change and the gate alter no data. |
| 4 | `build_corpus.py` again, after the log-banner edit | Corpus `0e228fea…`, identical. The banner names the seven held entries. |
| 5 | Independent stdlib diff (`AUDIT-REPORT` appendix A), shares no pipeline code, 1.2.0 → 1.3.0 | Same ids in the same order. All text columns (`gurmukhi`, `text`, `translit`, `translit_norm`, `fl_g`, `fl_r`, `skeleton`, `markers`) are code-point- and byte-identical. Changed cells: `author` 2, `section` 791, `comp_id` 29, `line_no` 29, `is_header` 3, each exactly as the applied ledger entries predict. The derived columns `source_category` (1, line 23470: Gurus → Bhagats) and `stanza_index` / `pada_total` (3, the three new heading lines) also changed. **No unexplained change.** |
| 6 | The same script's table pass | 32 of 59 tables differ in content, matching `downstream.md`'s list exactly. The non-obvious ones are explained below. |
| 7 | `diff_scripture.py 1.2.0 1.3.0` with the PR's allow-list | PASS. Only the allowed columns changed. |
| 8 | `make verify`, `guard`, `ledger-check`, `fingerprint`, `quality` | All pass. `ledger-check` reports 0 scripture lines changed against `main`. |
| 9 | Composition ids (1.2.0 → 1.3.0) | `max` 5376 → 5383; distinct 4527 → 4530; the new gaps are exactly 5377–5380; no 1.2.0 id disappeared. 5381–5383 never existed in 1.2.0. 2749 now holds lines 30064–30080 only, all Bhagat Trilochan Ji's. `line_no` runs 1..N in 2749, 5381, 5382 and 5383. |
| 10 | `python3 pipeline/g3_gate.py --release-check` | **Exit 1**, with 8 G3 entries listed: 7 held and 1 proposed. This is expected and correct. |
| 11 | `uvx ruff@0.9.10 check .`; `gitleaks detect --no-git -c .gitleaks.toml` | Both clean. |

**Differences explained** (all have a cause; none is unexplained):

- **`word_freq` and `variants`.** The row counts are unchanged. The frequencies of `ਸ੍ਰੀ`, `ਸੈਣੁ`, `ਪੀਪਾ`
  and `ਧੰਨਾ` each drop by 1, because the three label lines became headings and headings are not counted.
  `downstream.md`'s "`word_freq` loses the 3 label words" is imprecise: **four** words lose one count
  each, and no row is lost. It is corrected here; the generated `downstream.md` is left as generated.
- **`sources`, `meta`, `timing_migrations` and `analytics_meta`** hold build dates and the version.
- **`fts_shabad`, `fts_tri`, the analytics tables and the neighbour tables** are derived from the changed
  `author`, `comp_id` and `is_header` values.

**Not run** (each says why):

- **The iOS DB derivation (`make ios-db`) and the app test suites.** They belong to the consumers'
  release, after a ruling.
- **The DR drill.** It needs a fresh clone and about 5 GB. Two full rebuilds were run instead.
- **`/api/health` on sggs-platform.** It lives in another repository and pins 1.2.0.

## 4 · Do the tests actually catch failures? Mutation and negative tests

Each check was deliberately broken in a throwaway copy, and the test suite was then run. Every
mutation and negative test listed below was **caught**.

| # | Deliberate break | Caught by |
|---|---|---|
| 1 | Reviewer check removed | test_g3_gate (2 errors) |
| 2 | Future-date check removed | 2 failures |
| 3 | Decision-value check removed | 3 failures |
| 4 | Scope check removed | 1 failure |
| 5 | Evidence-file check removed | 1 failure |
| 6 | `entry_sha256` binding removed | 1 failure |
| 7 | Refusal of the fixture reviewer removed | 1 failure |
| 8 | Unknown statuses accepted | 1 failure, 5 errors |
| 9 | Owner-approval allowlist bypassed | 1 failure |
| 10 | Held entry with a filled ruling accepted | 2 failures |
| 11 | Held entries not counted as outstanding | 2 failures |
| 12 | `proposed` treated as applied | 2 failures |
| 13 | Structure entries allowed without `g3` | 1 failure |
| 14 | Rule E bypasses the gate | 1 failure |
| 15 | Structure pass bypasses the gate | **First run: survived.** Test added (`test_the_structure_pass_refuses_an_incomplete_approval`), then 1 failure. |
| 16 | `attribution.load_ledger` unvalidated | **First run: survived.** Test added (`test_both_ledger_loaders_validate`), then 1 failure. |
| 17 | `structure.load_ledger` unvalidated | 1 failure |
| 18 | Held entry flipped to `proposed` with the corpus not rebuilt | `test_the_committed_corpus_is_what_the_ledger_statuses_say` |
| 19 | G3 entry edited without regenerating the pack | `test_generated_for_these_g3_entries` |
| 20 | DB rebuilt without regenerating the pack | `test_generated_from_the_committed_db` |
| 21 | A pack quote with one matra dropped (`ਸੰਗੁ` → `ਸੰਗ`) | `test_every_cited_line_is_quoted_verbatim` |
| N1 | One scripture code point flipped in a DB copy (line 30081, U+0A38 → U+0A36) | `diff_scripture.py` exit 1 ("gurmukhi changed in 1 rows"); `sggs_integrity --compare` exit 1 (`scripture_sha256`, `t0_sha256`, `tables.lines`); the independent diff exits FAIL. |

**Test quality findings:**

- **PR #17 re-baselined every comparison gate in the same change** (`RISKS.md` D-1). Those gates prove
  self-consistency only. The 1.2.0 → 1.3.0 comparison in § 3 was done independently.
- **The previous ledger shape test** accepted `approved` without looking at `g3`. **The previous
  "approved entries hold" test** silently skipped every other status. Both are replaced or extended.

## 5 · Residual risks

See `RISKS.md`. The ones that cannot be closed from this repository:

- **G-2: admin bypass.** It can be closed only by changing the ruleset's bypass.
- **G-3: PR-editable CI.** It needs a required workflow or a second code owner.
- **G-4: consumers pin any commit.** It needs a sggs-platform and gurbani-soul-ios change.
- **C-1: saved links to composition 2749.** It needs an app change.
- **C-2: section names.** It needs the A-08 naming ruling and an app change.

## 6 · Limitations

- **Commentary.** Sahib Singh and Faridkot are read only as transcribed in ShabadOS 4.8.7. The edition
  is unstated, and 128 Darpan notes are cut off at 1,000 characters there. No printed Darpan, Faridkot
  Teeka, Mahan Kosh or Bir facsimile was consulted.
- **The source PDF's own edition** is not established by this audit. It is the file the corpus is
  proven against: sha256 `294a0b99…`.
- **Punjabi gists** were prepared by an agent and checked against context by a second pass, but a
  scholar should read every excerpt in context.
- **Remote settings** (rulesets, CODEOWNERS) were read, not changed.

## 7 · Next actions

1. **Kanwaljit Singh** reviews `DECISIONS.md` and the evidence, and replies with his rulings
   (`SIGN-OFF.md`).
2. **The engineer** records the reply under `rulings/`, fills the `g3` blocks
   (`g3_gate.py --hash <entry>`), runs `--release-check`, and rebuilds if any item is changed.
3. **The owner decides:**
   - whether to push this branch and open it as a draft PR into `fix/attribution-g3-held`;
   - whether to change the `protect-main` bypass (G-2);
   - whether to open consumer issues for G-4, C-1 and C-2.

## Appendix A · The independent diff script

`tools/independent_diff.py` (kept outside the repo, so it shares no code with the pipeline). It is run
as:

```
python3 independent_diff.py <1.2.0.sqlite> <1.3.0.sqlite> pipeline/attribution_ledger.json pipeline/structure_ledger.json
```

It is reproduced in `audit-tools/independent_diff.py` in this folder.
