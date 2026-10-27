# Risk register: G3 approval and dataset 1.3.0

Prepared 2026-10-27 for the G3 review of pull request #17.

- **Severity** is the damage if the risk occurs: critical, high, medium or low.
- **Status** says how far it has been dealt with:
  - **closed**: a safeguard exists here, and a test has been seen to fail without it;
  - **mitigated**: reduced, but not eliminated;
  - **open**: needs a change outside this repository or a manual setting;
  - **accepted**: known and left as it is, with the reason given.

"Shown" means the protecting test was made to fail on purpose, and the failure was recorded
(`AUDIT-REPORT.md` § 4).

## A. An unapproved change reaching readers

### G-1 · Held entries were `approved`, with a blank ruling, and were live (critical; closed in sggs-data)

- **Finding.** At `aeac8fd`, seven ledger entries had `status: approved` while `g3.decision`,
  `g3.reviewer` and `g3.date` were null:
  - `surdas-line` and `bhagat-run-heading-ang524`;
  - `section-salok-kabir` and `section-salok-farid`;
  - `ang695-sain-opens`, `ang695-pipa-opens` and `ang695-dhanna-opens`.

  `attribution.py` (rule E) and `structure.py` applied any `approved` entry without reading `g3`, and
  no CI step looked at `g3`.
- **Mitigation.** `pipeline/g3_gate.py` is the one validator, used by both passes, both
  `load_ledger()`s, the tests and CI.
  - The seven entries are now `held`.
  - An `approved` G3 entry needs a complete ruling that is bound to the entry's hash.
  - The release check fails while any G3 entry is held or unruled.
- **Verified.**
  - 29 gate tests and 3 pack tests.
  - 17 deliberate mutations of the gate and of its call sites, all detected (`AUDIT-REPORT.md` § 4).
  - A rebuild from the PDF with the gate in place reproduces the committed DB byte for byte.

### G-2 · An admin can merge past a red `integrity` (high; open, manual setting)

- **Finding.**
  - Ruleset `protect-main` (id 23922939): bypass actor `OrganizationAdmin`, mode `always`.
  - The pull-request rule requires 0 approvals.
  - Required checks `integrity`, `tests` and `secrets` are matched by name, not by integration, with
    `strict: false`.
  - Merges in this project are done with `gh pr merge --admin`.
- **Effect.** The release check is enforced against everyone except an org admin, and the owner is the
  org admin.
- **What would close it** (repository settings; not changed by this audit, which has no authority to):
  - set the `protect-main` bypass to `pull_request` mode, or remove it;
  - pin the required checks to the GitHub Actions integration;
  - turn on `strict`;
  - give `pipeline/g3_gate.py`, the two ledgers and `.github/**` a second code owner.
- **Until then**, the safeguard is a rule of conduct: never admin-merge a pull request whose
  `integrity` job is red because of the G3 step.

### G-3 · A pull request can edit its own CI (high; open, manual setting)

- **Finding.** On a `pull_request` event, GitHub runs the workflow file from the pull request's own
  branch. A pull request could therefore delete the G3 step and pass.
- **Closing it:**
  - an organization required workflow pinned to a protected ref; or
  - a second code owner on `.github/workflows/**` and `pipeline/g3_gate.py`.
- **Detection today:** the diff shows the change, and `test_the_release_check_fails_today…` still runs
  in the `tests` job, which a workflow edit to `integrity` does not remove.

### G-4 · Consumers can pin any sggs-data commit, including this held one (critical; open, cross-repo)

- **Finding.** `sggs-platform/scripts/data/fetch_dataset.py:check_pin`, and its byte-identical copy in
  gurbani-soul-ios, check only that the LFS pointer at `lock.commit` names the pinned oid and size.
  - Nothing requires that commit to be on `main` or tagged `data-v*`.
  - Nothing requires its CI to have passed.
  - Nothing requires its ledgers to pass the release check.

  The held DB (`003cae57…`) is fetchable through `refs/pull/17/head` and the public LFS endpoint.
- **What would close it.** `make dataset` in both consumers refuses a commit that:
  - is not reachable from sggs-data `main` or a `data-v*` tag; or
  - whose `pipeline/g3_gate.py --release-check` fails at that commit.

  This is a change in sggs-platform and gurbani-soul-ios. It is not made here.

### G-5 · A held DB carries no marker of its own (medium; mitigated)

- **Finding.** `MANIFEST.json` and the DB `meta` table do not record that held entries were applied.
- **Why not closed here.** Stamping them would change the DB bytes and force a rebuild for an
  informational field.
- **Mitigation.**
  - The build log prints `HELD — not a release: 7 G3 entries …`.
  - The release check fails on the ledgers that produced the DB.
  - `test_the_committed_corpus_is_what_the_ledger_statuses_say` ties the ledger statuses to the
    committed corpus.
  - G-4's fix would give consumers the refusal.

### G-6 · The ledger status was not bound to the committed artifacts (high; closed in sggs-data)

- **Finding.** Only a full rebuild compared the corpus against the ledgers. CI did not.
- **Mitigation.** A new test checks every applied entry's `to` value, and every unapplied G3 entry's
  `from` value, against `corpus/sggs.jsonl`. The hash chain already ties the corpus to the DB
  (`MANIFEST`, attestation).
- **Shown** (mutation 18). Flipping a held entry to `proposed` without rebuilding fails the test.

### G-7 · A ruling recorded for one version of an entry, applied to another (high; closed)

- **Mitigation.** `g3.entry_sha256` is the hash of the entry minus its status, hold note and `g3`. Any
  edit to its range, `from`, `to`, reason or evidence voids the ruling.
- **Shown** (mutation 6).

### G-8 · A scholar's item passed off as an owner approval by deleting its `g3` block (high; closed)

- **Mitigation.**
  - An approved attribution entry with no `g3` must be in `OWNER_APPROVED` (`japji`, `sadu`).
  - Every structure entry must carry `g3`.
- **Shown** (mutations 9 and 13).

### G-9 · Earlier "G3" approvals were recorded as owner confirmations (medium; for the record)

- **Finding.** `audit/editorial-ledger.jsonl` E004–E011 read: "Scholarly review completed; approval
  confirmed by the owner (Sam Kalaliya) on 2026-09-24 - gate G3."
- **Context.** These are text-repair entries, outside this pull request. They show that the project has
  previously recorded a scholarly review through the owner's confirmation, with no reviewer named.
- **This audit** neither changes nor judges those entries. It records the precedent so that the
  1.3.0 rulings name their reviewer.

## B. Data integrity

### D-1 · Every gate was re-baselined by the same pull request it judges (high; mitigated)

- **Finding.** PR #17 re-recorded four things at once:
  - `audit/scripture-baseline.json`;
  - `audit/dataset-fingerprint.json`;
  - `audit/data-quality-baseline.json`;
  - the `verify_regroup` expectations.

  Those gates therefore prove that the new build is consistent with itself, not that it matches 1.2.0.
- **Mitigation.** This audit compared 1.2.0 with 1.3.0 independently (`AUDIT-REPORT.md` § 3):
  - with a stdlib script that shares no code with the pipeline;
  - with `diff_scripture.py`;
  - with `compare_builds.py`.

  `scripture_sha256` and `t0_sha256` are unchanged. Every changed `lines` cell is predicted by a ledger
  entry or by a derived column.
- **Open.** No CI job diffs a pull request's DB against its base DB. Recommended: a `base-diff` job that
  fetches the base DB through LFS and runs `diff_scripture.py --allow …`.

### D-2 · Composition-id non-reuse rests on a re-recordable baseline (medium; open)

- **Finding.**
  - `data_quality.py` compares the gap count and the gap-list hash by equality.
  - The burned ids 5377–5380 are recorded nowhere durable; they exist only through `comp_seq` at
    build time.
- **Verified** independently for 1.3.0:
  - the new gaps are exactly 5377–5380;
  - no 1.2.0 id disappeared;
  - 5381–5383 never existed in 1.2.0.
- **Recommended:** a committed comp-id registry (issued, burned, live) checked for monotonicity
  against the base.

### D-3 · Rebuild reproducibility depends on `SOURCE_DATE_EPOCH` (low; documented)

- **Finding.** `rebuild_all.sh` defaults the epoch to the HEAD commit time. The committed DB was built
  at `8bad6f5`, so:
  - a rebuild at `aeac8fd` gives `cdb0b7c2…`, which differs only in `analytics_meta` and
    `timing_migrations` timestamps;
  - a rebuild with `SOURCE_DATE_EPOCH=1793005527` gives `003cae57…`, byte-identical.
- **Recommended:** record the build epoch in `MANIFEST.json`.

### D-4 · Interpreter drift (low; documented)

- **Finding.** 1.3.0 was built with `/usr/bin/python3` 3.9.6 (SQLite 3.51.0) and 1.2.0 with SQLite
  3.53.4. The content is identical, but the file bytes are reproducible only with the same interpreter.
  This audit's rebuild used the same interpreter as PR #17.

### D-5 · `write_attestation.py` records `reconciled_char_exact` and `golden_pass` as constants (low; open)

- **Finding.** The attestation is trustworthy only because the Makefile runs reconcile and golden
  first.
- **Verified here:** reconcile char-exact and golden pass were run by this audit (`AUDIT-REPORT.md` § 3).

## C. Consumers (sggs-platform, gurbani-soul-ios)

### C-1 · Saved items reopen the wrong composition after A-10 (medium; open, cross-repo)

- **Where comp_id is persisted:**
  - iOS `SavedLine.compId` (`Persistence/SavedLine.swift:12`);
  - Spotlight identifiers `saved-<line>-comp-<comp>`;
  - widget links `sggs://shabad/<compId>?line=`;
  - web pins (`store.ts`, `Pin.comp_id`).
- **What happens.** After the split, a line saved from 30081–30109 still points at 2749, which now
  holds only Bhagat Trilochan Ji's 17 lines. `ShabadSheet.swift:65` does not find the focus line, and
  the sheet shows the top of the wrong shabad without saying so.
- **Recommended:** when the focus line is not in the composition, resolve the composition from the
  line id.

### C-2 · Section names differ between the data and the apps (medium; open, needs the A-08 ruling)

- **The data** uses `ਸਲੋਕ ਭਗਤ ਕਬੀਰ` and `ਸਲੋਕ ਸੇਖ ਫਰੀਦ`.
- **iOS** `GranthNames.swift:40` is keyed on the printed headings (`ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ`,
  `ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ`), so the new sections would get no English name.
- **The web** `browse.ts` patches the old `ਚਉਬੋਲੇ` row into three, which would duplicate rows once
  the data has its own.
- The A-08 ruling on names decides which side changes.

### C-3 · Cached shabad responses (low; open)

The platform CDN caches `/api/shabad/*` for an hour (`s-maxage=3600`). After a dataset bump,
`/api/shabad/2749` can serve the old four-shabad response for up to an hour.

### C-4 · Test pins (low)

- iOS `VoiceReaderTests` skips after the split.
- The 36-voice pins are consistent with A-07.
- No composition-id range assumption was found (`Router.swift` accepts `1...Int32.max`).

## D. The review pack itself

### P-1 · A stale pack shown to the reviewer (high; closed)

- **Mitigation.** `pack-inputs.json` records the DB and the G3 entries the pack was generated from.
  `test_g3_pack` fails when either moves without regeneration.
- **Shown** (mutations 19 and 20).
- **Also verified:** regenerating the pack from its inputs reproduces the committed `README.md`,
  `evidence.md`, `downstream.md` and `changes.csv` byte for byte.

### P-2 · Commentary read through one transcription (medium; accepted, disclosed)

- **Finding.** Every Sahib Singh and Faridkot passage in this pack is read as transcribed in the
  ShabadOS 4.8.7 database. The edition is not stated there.
  - 128 Sahib Singh notes are cut off at 1,000 characters, among them the A-07 and A-10 notes cited.
  - No printed Darpan or Faridkot Teeka was consulted.
- **The pack** labels these quotations accordingly (`EVIDENCE-LEDGER.md`).

### P-3 · ShabadOS and BaniDB counted as two sources (medium; closed in the text)

- **Finding.** ShabadOS carries the BaniDB/STTM shabad ids, and the two group lines identically
  except in 13 places, A-07 among them. For grouping they are one lineage, and the pack counts them so.
