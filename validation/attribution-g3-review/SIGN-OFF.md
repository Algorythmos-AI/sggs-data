# G3 scholarly review: SGGS dataset 1.3.0

**This is a blank form. No ruling has been given.** Nothing in this repository records a decision by
the reviewer until he gives one explicitly.

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
