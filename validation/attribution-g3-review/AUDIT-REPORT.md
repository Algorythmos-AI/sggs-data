# Independent audit: dataset 1.3.0 and the G3 review (PR #17, PR #18)

- **Prepared:** 2026-10-27, on branch `audit/g3-hardening`, which is based on PR #17's head `aeac8fd`.
- **Revised:** 2026-10-28 after PR #19's first CI run (§ 8, `AUDIT-TRAIL.md`).
- **What this is:** an engineering and evidence audit. It is not a scholarly ruling, and nothing here
  records one.

## 0 · Where things stand

| State | Status |
|---|---|
| 1. Engineering implementation (approval gate, signed rulings, base-branch gate, tests, CI wiring) | **Complete**, pushed to `audit/g3-hardening` (draft PR #19). |
| 2. Automated validation | **Complete.** 140 tests pass (1 skipped: iOS app not in this repo). `make ci` runs every gate, and all of them pass except `g3-release`, which runs last and fails **by design**: 8 G3 entries have no ruling (7 held, 1 proposed). Full rebuild from the PDF, re-run 2026-10-28: byte-identical. 39 mutants and one scripture negative test: all caught (§ 4, § 8). |
| 3. Evidence pack | **Verified** to the extent in § 2. The limits are listed there and in § 6. |
| 4. Scholarly decision | **Pending.** No ruling has been given on A-07, A-08, A-10, A-11 or Ang 323. |
| 5. Release readiness | **Not established.** The release check fails until the rulings are recorded. Consumer-side risks (`RISKS.md` G-4, C-1, C-2) are open. |
| 6. Merge authorised | **No.** PR #17, #18 and #19 stay draft. Nothing was merged or released, and no remote setting was changed. `audit/g3-hardening` was pushed with the owner's authorisation (2026-10-28). |

## 1 · What changed in this branch, and why

| File | Change |
|---|---|
| `pipeline/g3_gate.py` (new) | One validator for both ledgers. It provides `--release-check` and `--hash`. It enforces:<br>• a closed set of statuses;<br>• a registry of the G3 items (`G3_ENTRIES`): an item cannot be dropped, renamed, stripped of its `g3` block or set to `keep`;<br>• owner approvals pinned by hash;<br>• a complete ruling: a reviewer of record (`REVIEWERS`), a date from 2026-10-26 to today, scope = item, the reviewer's reply as a hash-pinned, non-symlinked file in `rulings/`, and the hash of the entry's acting fields;<br>• a check that the committed corpus matches the statuses. |
| `pipeline/attribution.py`, `pipeline/structure.py` | Apply only what the gate lets through. `load_ledger()` validates the whole ledger, and a missing ledger is now an error. Rule E fails on ids that are not in the corpus. `gate=` passes keyword arguments to the gate, for tests only. |
| `pipeline/attribution_ledger.json`, `pipeline/structure_ledger.json` | The seven unruled G3 entries go from `approved` to `held`. Separately, the prose of `bhagat-run-heading-ang524` (`reason`, `review`) is corrected: it now says "11 of the other 12", and that the print does not join `ਸੁਧੁ` to the heading. No acting field changes. |
| `pipeline/build_corpus.py` | Log lines only: a `HELD — not a release` banner that names the held entries. |
| `pipeline/tests/test_g3_gate.py` (new) | 42 tests. They cover invalid, unprovenanced and complete rulings; statuses; the registry; the owner pins; the committed ledgers and corpus; the adversarial review's stripped-ledger attack; and `main()`'s pass and fail paths. |
| `pipeline/tests/test_g3_pack.py` (new) | 4 tests. The pack must match the committed DB and the G3 entries. `README.md` must equal its rendered template. Every `` `…` *(line N)* `` quote must equal corpus line N exactly. |
| `pipeline/tests/test_structure.py`, `test_attribution.py` | Fixtures use `held` entries with a `g3` block, and `held` is now an allowed status. No assertion was weakened. |
| `scripts/data/g3_attribution_pack.py` | Writes `pack-inputs.json`, recording which inputs the pack was built from. |
| `.github/workflows/data-ci.yml`, `Makefile` | `g3_gate.py --release-check` runs as the **last** step of the required `integrity` job (`if: !cancelled()`), and last in `make ci` (`g3-release`). A held PR therefore still gets every other check. |
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
   - On Angs 524 and 323, both the page image and the PDF's own text lines show this. On Angs 517 and
     654, only the text lines were read.
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
| 12 | After the adversarial-review fixes: `build_corpus.py` again, through the revised gate (`SOURCE_DATE_EPOCH=1793005527`, `/usr/bin/python3` 3.9.6) | Corpus `0e228fea…`: **identical**; the HELD banner names the 7 entries. The full DB rebuild (rows 1–3) was **not** re-run for this revision. The DB build reads the corpus, not the ledgers (`RISKS.md`, the agent C finding on Q2), so the corpus identity is what this revision could change. |
| 13 | `make -k ci` | Every gate passes: verify, guard, ledger-check, fingerprint `identical`, quality, and 126 tests. `g3-release` runs last and fails by design (8 entries). |

**Differences explained** (all have a cause; none is unexplained):

- **`word_freq` and `variants`.** The row counts are unchanged. The frequencies of `ਸ੍ਰੀ`, `ਸੈਣੁ`, `ਪੀਪਾ`
  and `ਧੰਨਾ` each drop by 1, because the three label lines became headings and headings are not counted.
  `downstream.md`'s table shows this correctly. The README's summary line ("`word_freq` loses the 3
  label words") was imprecise: **four** words lose one count each, and no row is lost. It is corrected in
  `README.template.md`, and the README is regenerated from it.
- **`sources`, `meta`, `timing_migrations` and `analytics_meta`** hold build dates and the version.
- **`fts_shabad`, `fts_tri`, the analytics tables and the neighbour tables** are derived from the changed
  `author`, `comp_id` and `is_header` values.

**Not run** (each says why):

- **The iOS DB derivation (`make ios-db`) and the app test suites.** They belong to the consumers'
  release, after a ruling.
- **The DR drill.** It needs a fresh clone and about 5 GB. Two full rebuilds were run instead.
- **`/api/health` on sggs-platform.** It lives in another repository and pins 1.2.0.

## 4 · Do the tests actually catch failures? Mutation and negative tests

`audit-tools/mutate.py <repo> <scratch>` reproduces every row below from the repository alone. It works
on a copy-on-write clone: it applies each deliberate break, runs the gate, pack, structure and
attribution tests, and restores the file. The output is `audit-tools/mutation.out`.

**Final run: 31 mutants plus one scripture negative test, all caught (0 survived).** The tests were
earlier made to catch mutants that had survived:

- **First pass.** The structure pass and `attribution.load_ledger` could bypass the gate without any
  test failing. `test_the_structure_pass_refuses_an_incomplete_approval` and
  `test_both_ledger_loaders_validate` were added.
- **After the adversarial review's fixes.** The owner-approval allowlist (mutant 11) and the corpus
  check inside the CLI (mutant 21) went unnoticed. `test_a_new_entry_cannot_be_approved_without_a_ruling`
  and `test_the_cli_checks_the_corpus_not_only_the_ledgers` were added.

The previous runs are kept in git history; this table is the current run.

```
 1 KILLED    reviewer-of-record check removed                     failures=8
 2 KILLED    future-date check removed                            failures=1
 3 KILLED    minimum-date check removed                           failures=1
 4 KILLED    decision check removed                               failures=3
 5 KILLED    scope check removed                                  failures=1
 6 KILLED    evidence location check removed                      failures=2, errors=10
 7 KILLED    symlink refusal removed                              failures=1
 8 KILLED    ruling-file hash check removed                       failures=1
 9 KILLED    entry_sha256 binding removed                         failures=1
10 KILLED    unknown statuses accepted                            failures=1, errors=5
11 KILLED    owner-approval allowlist bypassed                    failures=1
12 KILLED    G3 item may be `keep`                                errors=1
13 KILLED    held/proposed with a filled ruling accepted          failures=2
14 KILLED    held not counted as outstanding                      failures=2
15 KILLED    `proposed` treated as applied                        failures=5
16 KILLED    structure entries allowed without g3                 failures=1
17 KILLED    registered G3 entry may lose its g3 block            failures=4
18 KILLED    registered G3 entry may be missing                   errors=2
19 KILLED    owner-approved pin not checked                       failures=1
20 KILLED    unregistered g3 entries accepted                     failures=1
21 KILLED    release check skips the corpus                       failures=1
22 KILLED    non-integer ids accepted                             failures=3
23 KILLED    rule E bypasses the gate                             failures=1
24 KILLED    structure pass bypasses the gate                     failures=1
25 KILLED    attribution.load_ledger unvalidated                  failures=1
26 KILLED    structure.load_ledger unvalidated                    failures=1
27 KILLED    held entry flipped to proposed, corpus not rebuilt   failures=5
28 KILLED    G3 entry edited without regenerating the pack        failures=1
29 KILLED    DB rebuilt without regenerating the pack             failures=1
30 KILLED    a pack quote misquoted by one matra                  failures=1
31 KILLED    README.md hand-edited (stale against its template)   failures=1
N1 KILLED    one scripture code point flipped (U+0A38->U+0A36, line 30081)   diff_scripture exit 1, fingerprint exit 1
0 survived
```

**Test quality findings:**

- **PR #17 re-baselined every comparison gate in the same change** (`RISKS.md` D-1). Those gates prove
  self-consistency only. The 1.2.0 → 1.3.0 comparison in § 3 was done independently.
- **The previous ledger shape test** accepted `approved` without looking at `g3`. **The previous
  "approved entries hold" test** silently skipped every other status. Both are replaced or extended.

## 4b · The adversarial review and what changed because of it

A fresh-context reviewer was given only the diff and the pack, and asked to find reasons to reject
them. It made 13 findings. Each one, and what was done:

| # | Finding (severity) | Done |
|---|---|---|
| 1 | The G3 step failed before six other `integrity` checks, and `make ci` stopped at it, so a held PR lost its fingerprint, guard and regroup checks (high) | **Fixed.** The step is last, with `if: !cancelled()`; `g3-release` is last in `make ci`. |
| 2 | `--release-check` checked only the ledgers. Stripping `g3` blocks, or setting G3 entries to `keep`, passed with the held DB still committed (high) | **Fixed.** There is a registry of G3 items, `keep` is refused for a G3 item, and the CLI checks the corpus against the statuses. Tests cover the stripped-ledger attack and the corpus check. |
| 3 | A ruling's shape was checked, not its provenance: blank form as evidence, reviewer "x", a 1900 date, symlinks, a zero-width-space fixture name (high) | **Fixed.** Reviewer of record, minimum date, evidence must be the reply file in `rulings/` (regular, not a symlink, sha256-pinned). Each case is tested. |
| 4 | "Never bypassed by an admin merge" is unenforced; the `data-v*` tag ruleset does not restrict **creation** (high) | **Documented, not closable here.** The workflow comment now says it is unenforced against admins. `RISKS.md` G-2 and G-10. |
| 5 | Owner approvals were bound by name only (medium) | **Fixed.** Pinned by `entry_sha256`. |
| 6 | The ruling hash covered prose, including two statements the pack shows are false (medium) | **Fixed.** The hash covers acting fields only, and the false prose in the Ang 524 entry is corrected. |
| 7 | Two ruling forms that disagreed; "Prepared … by: Kanwaljit Singh" readable as his act (medium) | **Fixed.** SIGN-OFF.md is the only form, with every option aligned to DECISIONS.md. The reviewer line is marked "designated". The user's template line is kept, with a note that it records nothing. |
| 8 | The dataset attributes the other two `ਸੁਧੁ` joins inconsistently (medium) | **Added** to DECISIONS A-11 and CONTRADICTIONS. |
| 9 | "SOS = BaniDB except 13" was checked one way only (low-medium) | **Relabelled.** The 16 absent STTM ids are listed as unexamined. |
| 10 | Angs 517 and 654 were said to be image-checked (low) | **Corrected:** text layer only. |
| 11 | Mutation evidence was inconsistent and partly not reproducible (low) | **Fixed.** `mutate.py` now reproduces all 31 mutants plus N1. |
| 12 | Test gaps: no success path, no `apply` with a full ruling, wall-clock dependence (low) | **Fixed.** `main()` success path and both passes run with a complete fixture ruling; "today" is UTC + 1 day. |
| 13 | README staleness not enforced; the README's word_freq line was wrong (low) | **Fixed.** A render test, and the line corrected in the template. |

## 5 · Residual risks

See `RISKS.md`. The ones that cannot be closed from this repository:

- **G-2: admin bypass.** It can be closed only by changing the ruleset's bypass.
- **G-3: PR-editable CI.** Mitigated by `g3-gate.yml` (base-branch gate); enforced only once
  `g3-base-gate` is a required check.
- **G-12: no reviewer key registered.** No ruling can verify until one is (by design).
- **G-4: consumers pin any commit.** It needs a sggs-platform and gurbani-soul-ios change.
- **G-10: `data-v*` tags can be created on any commit.** It needs a tag-creation rule.
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
   - ~~whether to push this branch and open it as a draft PR~~ (done 2026-10-28: PR #19, draft);
   - registering the reviewer's public key from a key he sends (G-12);
   - making `g3-base-gate` a required check (G-3), changing the `protect-main` bypass (G-2) and adding
     a creation rule for `data-v*` tags (G-10);
   - whether to open consumer issues for G-4, C-1 and C-2.

## 8 · Revision of 2026-10-28: PR #19's CI run

**What CI showed.** Run 40627048618 (`integrity`, at `8237336`): every scripture and data step passed;
the last step, the G3 release check, failed listing 8 entries. That failure is the gate working. The
"8 against seven" difference is `bhagat-run-heading-ang323`, which is `proposed` (not applied) where the
other seven are `held` (`RISKS.md` G-13).

**What was asked, and what was not done.** The owner asked that the rulings be recorded "as Kanwaljit
Singh" from the Bir so that CI goes green. That was declined: it would fabricate a scholarly approval,
and the print does not decide these editorial questions (`AUDIT-TRAIL.md`). Instead, engineering
recommendations, labelled as not rulings, were added to `DECISIONS.md`.

**What changed** (commits `581f720`, code, and `7ff4c21`, documentation):

| File | Change |
|---|---|
| `pipeline/g3_gate.py` | A ruling verifies only with the reviewer's SSH signature over his reply, checked against `allowed_signers` in the gate's own tree (`PRINCIPALS`, `SIGNERS`, `SIG_NAMESPACE`). `--tree DIR` judges another checkout's data with this copy's code and anchors. Applied and G3 entries must carry every acting field. The release summary splits held and proposed. |
| `.github/workflows/g3-gate.yml` (new) | `pull_request_target`: the base branch's gate judges the pull request's tree, read as data only. |
| `pipeline/tests/test_g3_gate.py` | 56 tests (was 42): `SignedRulings` (8), `BaseBranchGate` (3), `WorkflowRules` (2), required fields, and all eight entries by name in the CLI output. |
| `audit-tools/mutate.py` | Mutants 32–39; creates its scratch directory. |
| `DECISIONS.md`, `RISKS.md`, `SIGN-OFF.md`, `README.template.md` / `README.md`, `AUDIT-TRAIL.md` (new), `docs/architecture/attribution.md` | Recommendations (not rulings), G-3/G-11 updated, G-12/G-13 added, the signing step, the trail. |

**Commands and results** (2026-10-28):

| # | Command | Result |
|---|---|---|
| 14 | `SOURCE_DATE_EPOCH=1793005527 make rebuild PDF=…` in a copy-on-write clone of `8237336` | Exit 0. Reconcile char-exact, golden pass, integrity gate PASS. DB `003cae57…`, corpus `0e228fea…`: **byte-identical** to the committed 1.3.0. Closes row 12's open point. |
| 15 | `/usr/bin/python3 pipeline/build_corpus.py` through the `581f720` gate | Corpus `0e228fea…`, identical; the HELD banner names the seven held entries. |
| 16 | `python3 -m unittest discover -s pipeline/tests` | 140 tests, OK (1 skipped). |
| 17 | `audit-tools/mutate.py` | 39 of 39 mutants killed; N1 (scripture code point flipped) killed; 0 survived. |
| 18 | `make -k ci` | Every gate passes except `g3-release`: "8 G3 entries … (7 held: applied only in this draft build; 1 proposed: not applied)". |
| 19 | `g3_gate.py --release-check --tree .` | Same 8 entries, exit 1. |
| 20 | `uvx ruff@0.9.10 check .`; `gitleaks detect --no-git -c .gitleaks.toml`; `actionlint` | All clean. |
| 21 | `git diff aeac8fd -- corpus db MANIFEST.json audit` | Empty. No ledger status or `g3` field changed in this revision. |

**Not verified.** `g3-gate.yml` has not run on GitHub: `pull_request_target` uses the base branch's
workflow file, and PR #19's base does not have it yet. Its behaviour is covered by the `--tree` tests and
the workflow-rule tests, not by a live run.

## Appendix A · The independent diff script

`audit-tools/independent_diff.py` in this folder. It imports nothing from the pipeline (stdlib only), so
it does not share the code it checks. It is run as:

```
python3 independent_diff.py <1.2.0.sqlite> <1.3.0.sqlite> pipeline/attribution_ledger.json pipeline/structure_ledger.json
```

Also in `audit-tools/`:

- `mutate.py`: § 4.
- `extract_shabados.py`: the ShabadOS extraction used for the commentary rows. It needs `gurmukhiutils`
  for display only.
- Their outputs.
