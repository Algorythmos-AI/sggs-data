# Audit trail: G3 review of dataset 1.3.0

This file is the durable record of what happened to the G3 items, when, in which commit, on what
evidence, and what is still open. Read it instead of any chat history. Times are UTC, taken from git and
GitHub, not from memory. Append new events at the end. Never rewrite an earlier one; correct it with a
new dated entry.

**Approval status at the last entry: no G3 item has a ruling.** Every `g3` field in both ledgers is
blank. No reviewer key is registered. Nothing in this repository records a decision by Kanwaljit Singh.

## Events

| When (UTC) | Commit / run | What happened | Evidence |
|---|---|---|---|
| 2026-10-26 09:07 | PR #17 opened (draft) | `fix/attribution-g3-held`: four attribution and structure fixes held for G3 (A-07, A-08, A-10, A-11), with Ang 323 as a proposed twin. | PR #17 |
| 2026-10-26 09:27 | `aeac8fd` | DB rebuilt for 1.3.0 (`003cae57…`). At this commit the seven G3 entries were `approved` with a blank ruling, and nothing checked the `g3` field. | `RISKS.md` G-1 |
| 2026-10-27 18:33 | PR #18 opened (draft) | `RECOMMENDATIONS.md`, an agent's recommendations into PR #17. Not a ruling. | PR #18 |
| 2026-10-27 22:21 | `68c1ffb` | The G3 gate (`pipeline/g3_gate.py`): the seven entries become `held`; a ruling must be complete; `--release-check` fails while any is outstanding. | `AUDIT-REPORT.md` § 1 |
| 2026-10-27 22:38 | `c1dcd5f` | The independent audit and the decision pack: print read as page images, ShabadOS 4.8.7, EoS per volume. | `DECISIONS.md`, `EVIDENCE-LEDGER.md`, `CONTRADICTIONS.md` |
| 2026-10-27 23:09 | `8237336` | The adversarial review's 13 findings closed or recorded (CI order, corpus binding, owner pins, provenance). 31 mutants, all caught. | `AUDIT-REPORT.md` § 4, § 4b |
| 2026-10-28 03:30 | PR #19 opened (draft); runs 40627048618, 40627048635 | `audit/g3-hardening` → `fix/attribution-g3-held`, with the owner's authorisation. `integrity` fails only at the G3 step, listing **8** entries; the pack said "seven held" (`RISKS.md` G-13). The title check failed on a non-conventional title; renamed `fix(data): …`, and the re-run passed. | GitHub Actions |
| 2026-10-28 (session) | none | The owner asked for the gate to be made green by recording rulings "as Kanwaljit Singh" from the Bir. **Declined.** Writing his name, decision or date into a ledger without his own ruling would fabricate a scholarly approval. Re-reading the print would not settle these questions anyway: it settles layout, not authorship or editorial boundaries (`DECISIONS.md`). | This file |
| 2026-10-28 07:22–07:24 (log file times) | (no commit; rebuild in a COW clone of `8237336`) | Full `make rebuild` with `SOURCE_DATE_EPOCH=1793005527`: exit 0, reconcile char-exact, golden pass, integrity PASS. DB `003cae57…` and corpus `0e228fea…`, **byte-identical** to the committed 1.3.0. This closes `AUDIT-REPORT.md` § 3 row 12's open point. | `AUDIT-REPORT.md` § 8 |
| 2026-10-28 07:35 | `581f720` | Gate: rulings must carry the reviewer's own SSH signature; `--tree` and `g3-gate.yml` judge a PR with the **base** branch's gate (closes G-11's residual, mitigates G-3); required fields; the 8-entry summary (closes G-13). 140 tests pass; 39 mutants plus the scripture flip, all caught; `build_corpus` through the new gate gives corpus `0e228fea…`, identical. | `AUDIT-REPORT.md` § 8 |
| 2026-10-28 07:39 | `7ff4c21` | `DECISIONS.md` gains the engineering recommendations (**not rulings**). `RISKS.md` G-3, G-11, G-12 and G-13 are updated or added. `SIGN-OFF.md` gains the signing step. The README, the architecture doc, `AUDIT-REPORT.md` § 0/§ 7/§ 8 and this trail are updated. | This file |

## Lessons recorded so they are not repeated

1. **A ledger status is not an approval.** At `aeac8fd`, `approved` with a blank `g3` was live. Every
   status is now checked by one gate, everywhere a ledger is read (G-1).
2. **Count what the tool counts.** "Seven held" and "8 outstanding" were both true. Reports now name the
   statuses behind every number (G-13).
3. **A gate judged by the code under review is not a gate.** The base branch's gate judges a PR (G-3).
4. **A file in `rulings/` is not proof of who wrote it.** Signatures, and keys only on the base branch
   (G-11, G-12).
5. **Never make CI green by recording a ruling no one gave.** Asked for on 2026-10-28; declined. The
   fail-closed state is correct until the reviewer rules.
6. **Commit messages state counts that match the data.** An earlier message said "five" for seven entries
   and was corrected before push. Re-read counts against the ledgers before every commit.
7. **Re-read before claiming a convention.** The A-08 naming recommendation was first written with
   examples that did not fit, and was corrected against the DB (`DECISIONS.md`).

## Outstanding (owner of each in brackets)

| Item | Owner | Where |
|---|---|---|
| Rulings on A-07, A-08, A-10, A-11 / Ang 524, Ang 323 | Kanwaljit Singh | `SIGN-OFF.md`, `DECISIONS.md` |
| Register the reviewer's public key | Owner, from a key the reviewer sends | `RISKS.md` G-12 |
| Make `g3-base-gate` a required check; restrict the admin bypass; a creation rule for `data-v*` tags | Owner (repository settings) | `RISKS.md` G-2, G-3, G-10 |
| Consumers pin only released datasets; saved links to composition 2749; section names in iOS | Owner (sggs-platform, gurbani-soul-ios) | `RISKS.md` G-4, C-1, C-2 |
| Line 50285 `ਨਾਮਦੇਵ ॥` inside Ravidas's composition; the `ਸੁਧੁ` segmentation item (d) | Needs its own entry and review | `DECISIONS.md` A-10, A-11 |
| PR #17, #18 and #19 | Stay draft; merge not authorised | GitHub |
