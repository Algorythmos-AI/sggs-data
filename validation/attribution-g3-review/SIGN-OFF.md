# G3 scholarly review: SGGS dataset 1.3.0

## Recorded ruling: Kanwaljit Singh, 2026-10-28 (relayed by Sam Kalaliya via WhatsApp)

Kanwaljit Singh answered the Punjabi WhatsApp form from his phone. The owner, Sam Kalaliya, relayed his
reply and his clarification of questions 2 and 3, and attests that both are his. The reply is kept
unchanged in `rulings/2026-10-28-kanwaljit-singh-whatsapp.txt`; it is signed by the relayer, not by the
reviewer (`RISKS.md` G-14). The reply carries no date of its own; 2026-10-28 is the date it was relayed.

| Q | Item | His answer | Recorded as |
|---|---|---|---|
| 1 | A-07 author, line 53935 | A: Bhagat Surdas Ji | `surdas-line` approve |
| 2 | A-07 composition, line 53935 | A: the line stands on its own (clarified: "Ans - A"; the option text he quoted is question 1's) | new `surdas-own-shabad` (kind `stands`, composition 5384, no heading) approve |
| 3 | A-08, Angs 1363–1384 | B: keep the Bir's order, text and Angs; headings and bookmarks at the printed headings, named as printed: ਚਉਬੋਲੇ ਮਹਲਾ ੫ / ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ / ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ | `section-salok-kabir`, `section-salok-farid` change (printed names); new `section-chaubole` approve. Only the `section` label moves; no line, order or Ang changes. |
| 4 | A-10, Ang 695 | A: yes, each label opens its own shabad, as printed | the three `ang695-*-opens` approve |
| 5 | A-11, Ang 524 heading | B: no author (the Bhagats' shared heading; the Kabir chaupada after it stays Kabir's) | `bhagat-run-heading-ang524` change (`to` null) |
| 6 | A-11 (d), `ਸੁਧੁ` / `ਸੁਧੁ ਕੀਚੇ` on Angs 323, 517, 524, 654 | Y, and: join it to the Vaar's last line as printed, not to the next heading | **Not applied in 1.3.0.** It splits four line records, so it needs its own entry, scripture proofs and review (`AUDIT-TRAIL.md`, outstanding). |
| 7 | A-11, Ang 323 heading | S: the same ruling as question 5 | `bhagat-run-heading-ang323` change (`to` null) |

The form below is the one he answered, kept as it was sent.

---

**The form as sent (2026-10-28).**

None of the following is scholarly approval:

- a green CI build;
- an engineer's approval;
- an agent's recommendation (`RECOMMENDATIONS.md`, pull request #18);
- the existence of this pack.

This is the **only** ruling form. The other pages are evidence.

**G3 Scholarly Review, SGGS Dataset 1.3.0**

Reviewer (designated; this line does not record a review): Kanwaljit Singh
Review date: __________________

The evidence for each item is in `DECISIONS.md` (one record per item), `EVIDENCE-LEDGER.md` and
`CONTRADICTIONS.md`.

- **What a ruling covers.** A ruling covers exactly the ledger entries named against its item. They
  are bound by what each entry *does* (its range, from and to), recorded in `pack-inputs.json`.
- **If an entry is edited later**, the ruling on it is void and must be given again.

| Item | Ledger entries | Ruling (circle one) | Conditions or changes |
|---|---|---|---|
| A-07, Ang 1253, line 53935: author | `surdas-line` | Approve (Bhagat Surdas Ji) / Change (author: ______) / Reject (keep Bhagat Namdev Ji) | |
| A-07: which composition line 53935 belongs to (a separate question; this PR does not change it) | none yet | (a) its own / (b) with Parmanand's shabad, as now / (c) with the following ਮਹਲਾ ੫ shabad (the dataset can record this only as a note) / No ruling | |
| A-08, Angs 1363–1384: three sections | `section-salok-kabir`, `section-salok-farid` | Approve / Change / Reject | Section names: short (`ਸਲੋਕ ਭਗਤ ਕਬੀਰ`, `ਸਲੋਕ ਸੇਖ ਫਰੀਦ`) / as printed / other: ______ |
| A-10, Ang 695: the three labels open compositions 5381–5383 | `ang695-sain-opens`, `ang695-pipa-opens`, `ang695-dhanna-opens` | Approve / Change / Reject | |
| A-11, Ang 524, line 23470: author of the heading | `bhagat-run-heading-ang524` | Approve (Bhagat Kabir Ji) / Change (no author / Guru Arjan Dev Ji / other: ______) / Reject (keep Guru Arjan Dev Ji) | |
| A-11 (d): open the `ਸੁਧੁ` segmentation question (lines 14771, 23136, 23470, 28417) as its own item? | none | Yes / No | |
| Related Ang 323 case, line 14771 | `bhagat-run-heading-ang323` | Same ruling / Separate ruling required / Leave unchanged | |

Conditions, corrections or further evidence required:

&nbsp;

&nbsp;

Scholar's confirmation:

&nbsp;

Prepared for scholarly review by: Kanwaljit Singh

*This pack was prepared by engineering (the G3 audit of 2026-10-27) **for** Kanwaljit Singh's review. The
line above names the reviewer the pack is for. It does not record that he prepared, reviewed or
approved anything.*

---

## How a ruling is recorded (engineering, after the reviewer has replied)

The gate (`pipeline/g3_gate.py`) refuses any ruling that does not meet every step below.

1. **Keep his reply, with his signature.** The reviewer's own reply (this form, filled in by him) is
   saved **unchanged** as a regular file in `rulings/` in this folder. It may not be a symlink. Its
   sha256 is recorded. **He signs it himself**, with the key registered for him in `allowed_signers`
   (`RISKS.md` G-12):
   `ssh-keygen -Y sign -f <his private key> -n sggs-g3-ruling <reply file>`.
   That writes `<reply file>.sig`, which is committed next to the reply. The gate verifies it against
   the base branch's `allowed_signers`; a reply without a valid signature counts as no ruling. Nobody
   else signs for him, and nobody else holds his private key.

   **Relayed reply (the owner's decision, 2026-10-28).** If he replies by WhatsApp from a phone, the
   evidence is the WhatsApp chat **export** ("Export chat → Without media"), saved unchanged. The relayer
   of record (`RELAYERS`, the owner) signs that export with his own registered key, attesting that it is
   the reviewer's reply as received:
   `ssh-keygen -Y sign -f <relayer's private key> -n sggs-g3-ruling <export file>`.
   The `g3` block then also carries `relayed_by` (the relayer's name) and `channel: whatsapp`, and the
   gate reports the ruling as relayed, not as signed by the reviewer (`RISKS.md` G-14).
2. **Fill the `g3` block.** For each entry his ruling covers, the engineer fills the entry's `g3`
   block:
   - `decision`: `approve`, `change` or `reject`;
   - `reviewer`: one of the gate's reviewers of record (`REVIEWERS`);
   - `date`: the date of the ruling, not before 2026-10-26;
   - `scope`: the item;
   - `evidence`: `validation/attribution-g3-review/rulings/<file>`;
   - `evidence_sha256`;
   - `entry_sha256`: from `python3 pipeline/g3_gate.py --hash <entry>`.

   The engineer then sets `status` to `approved` or `rejected`. A **Change** edits the entry first, so
   its hash changes, and the reviewer confirms the edited entry.
3. **Check and rebuild.** `python3 pipeline/g3_gate.py --release-check` must pass (and, on a pull
   request, the base-branch check `g3-base-gate`). It also checks that
   the committed corpus matches the statuses. Then the gated rebuild runs and the pack is regenerated.

Never fill a `g3` field from this blank form, from a recommendation, or from anything the reviewer
has not explicitly given.
