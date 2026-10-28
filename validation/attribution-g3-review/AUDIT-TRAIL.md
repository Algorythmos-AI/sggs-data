# Audit trail: G3 review of dataset 1.3.0

This file is the durable record of what happened to the G3 items, when, in which commit, on what
evidence, and what is still open. Read it instead of any chat history. Times are UTC, taken from git and
GitHub, not from memory. Append new events at the end. Never rewrite an earlier one; correct it with a
new dated entry.

**Approval status at the last entry: every G3 item carries Kanwaljit Singh's ruling of 2026-10-28,
relayed by the owner (Sam Kalaliya) from WhatsApp** and recorded as relayed, not as signed by the
reviewer (`SIGN-OFF.md`, `RISKS.md` G-14). The owner signed the reply with his registered key; the release
check passes.

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
| 2026-10-28 07:38 | `7ff4c21` | `DECISIONS.md` gains the engineering recommendations (**not rulings**). `RISKS.md` G-3, G-11, G-12 and G-13 are updated or added. `SIGN-OFF.md` gains the signing step. The README, the architecture doc, `AUDIT-REPORT.md` § 0/§ 7/§ 8 and this trail are updated. | This file |
| 2026-10-28 (session) | none | Ruling forms in English and Punjabi prepared for the reviewer to answer on WhatsApp from his phone. The Punjabi form fixed the English draft's "5 questions" (there are 7) and replaced an example answer that matched the engineering recommendations with a blank one, so as not to steer him. | Owner's chat |
| 2026-10-28 (session) | none | **A reply from Kanwaljit Singh reached the owner on WhatsApp** and was pasted into the session. **Nothing was recorded in the ledgers:** his Q2 answer is ambiguous (it carries Q1's wording), his Q3 answer needs confirming against the implementation, the reply has no closing line or date, and the record must be the WhatsApp export, not a pasted copy. A Punjabi follow-up asking only those points was prepared for the owner to send. His Q6 answer asks for a separate `ਸੁਧੁ` change, which needs its own entry and review. | Owner's chat |
| 2026-10-28 (session) | this commit | **Owner decision:** the reviewer cannot sign on his phone, so the owner signs the WhatsApp export himself as the relayer, recorded openly as relayed. Gate: optional `g3.relayed_by` + `g3.channel`; a relayed ruling verifies the relayer's signature (`RELAYERS`, `CHANNELS`) and is reported as "relayed …, not signed by the reviewer". 10 `RelayedRulings` tests; mutants 40–44. `RISKS.md` G-12 updated and G-14 added; `SIGN-OFF.md` step 1 gains the relayed path. No relayer key is registered yet. | `RISKS.md` G-14 |
| 2026-10-28 (session) | none | The owner relayed the reviewer's clarification: question 2 is **A** (the line stands on its own), question 3 is **B** with the printed names. The owner said he had talked to the reviewer and asked for the rulings to be recorded as given. | Owner's chat |
| 2026-10-28 (session) | this commit | **Rulings recorded, as relayed.** Evidence: both relayed messages, unchanged, in `rulings/2026-10-28-kanwaljit-singh-whatsapp.txt`. All 10 G3 entries `approved` (Q1, Q2, Q3, Q4, Q5, Q7); two new registered entries implement his words: `surdas-own-shabad` (kind `stands`: line 53935 becomes composition 5384, no heading) and `section-chaubole` (printed name). Q5/Q7 "no author" sets `author` null on lines 23470 and 14771. Q6 (`ਸੁਧੁ`) is **not** applied: it splits scripture line records and needs its own entry and proofs. Gate: `to` may be null for attribution; structure kinds are a closed set; `verify_regroup` allows exactly one headless composition (first line 53935). Rebuilt from the PDF in a scratch copy with the signature check stubbed (the signature never reaches the data). | `SIGN-OFF.md` |
| 2026-10-28 (session) | follow-up commit | `mutate.py` on the ruled state (signed simulation): 44/44 mutants plus the scripture flip caught. Five had depended on `held` entries in the committed ledgers; three were re-anchored and two (14, 37) are now held by fixture tests (`PendingRulings`). | `AUDIT-REPORT.md` § 9 |
| 2026-10-28 (owner's terminal) | this commit | **Signed.** The owner generated his relayer key on his own Mac (`~/.ssh/sggs_g3_relayer`, ed25519, fingerprint `SHA256:4inJAUpH0/+XYEfEScj+4ZMX1RD/rHM7DRKs3Xqfm7U`), signed the reply (`.sig`, namespace `sggs-g3-ruling`) and registered the public key as `sam-kalaliya` in `allowed_signers`. The private key never left his machine. `g3_gate.py --release-check`: every G3 ruling is recorded. | `allowed_signers`, `rulings/*.sig` |

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
8. **A fixture shortcut can hide the real path.** Mutant 42 first survived: the fixture relayer returned
   before the code a real relayer takes. A test now signs as a name in `RELAYERS` (2026-10-28).
9. **A test that reads the committed state stops guarding a rule once that state changes.** Mutants
   14 and 37 survived when the last `held` entry was ruled; such rules now have fixture tests.

## Outstanding (owner of each in brackets)

| Item | Owner | Where |
|---|---|---|
| The `ਸੁਧੁ` / `ਸੁਧੁ ਕੀਚੇ` segmentation (his Q6 direction): its own entry, proofs and review | Engineering, then the reviewer | `SIGN-OFF.md` Q6 |
| iOS `GranthNames.sections` has no English name for `ਚਉਬੋਲੇ ਮਹਲਾ ੫`; the web's `CLOSING_FIX`/reader chip become dead code | gurbani-soul-ios, sggs-platform | `downstream.md` |
| Make `g3-base-gate` a required check; restrict the admin bypass; a creation rule for `data-v*` tags | Owner (repository settings) | `RISKS.md` G-2, G-3, G-10 |
| Consumers pin only released datasets; saved links to composition 2749; section names in iOS | Owner (sggs-platform, gurbani-soul-ios) | `RISKS.md` G-4, C-1, C-2 |
| Line 50285 `ਨਾਮਦੇਵ ॥` inside Ravidas's composition; the `ਸੁਧੁ` segmentation item (d) | Needs its own entry and review | `DECISIONS.md` A-10, A-11 |
| PR #17, #18 and #19 | Stay draft; merge not authorised | GitHub |
