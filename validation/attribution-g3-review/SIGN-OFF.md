# G3 scholarly review: SGGS dataset 1.3.0

**This is a blank form. No ruling has been given.** Nothing in this repository records a decision
by the reviewer until he gives one explicitly. A green CI build, an engineer's approval, an agent's
recommendation (`RECOMMENDATIONS.md`, pull request #18) and the existence of this pack are not
scholarly approval.

Reviewer: **Kanwaljit Singh**
Review date: __________________

The evidence for each item is in `DECISIONS.md` (one record per item), `EVIDENCE-LEDGER.md` and
`CONTRADICTIONS.md`. Each item names the ledger entries a ruling applies to. A ruling covers exactly
those entries as they stand now. Their hashes are in `pack-inputs.json`, and an edited entry needs a
fresh ruling.

| Item | Ledger entries | Ruling (circle one) | Conditions or changes |
|---|---|---|---|
| A-07, Ang 1253, line 53935: author | `surdas-line` | Approve / Change / Reject | |
| A-07, Ang 1253: which composition the line belongs to (separate question; not changed by this PR) | none yet | (a) its own / (b) with Parmanand's shabad, as now / (c) note only / No ruling | |
| A-08, Angs 1363–1384: three sections | `section-salok-kabir`, `section-salok-farid` | Approve / Change / Reject | Section names: short (`ਸਲੋਕ ਭਗਤ ਕਬੀਰ`, `ਸਲੋਕ ਸੇਖ ਫਰੀਦ`) / as printed / other: ______ |
| A-10, Ang 695: the three labels open compositions 5381–5383 | `ang695-sain-opens`, `ang695-pipa-opens`, `ang695-dhanna-opens` | Approve / Change / Reject | |
| A-11, Ang 524, line 23470: author of the heading | `bhagat-run-heading-ang524` | Approve (Bhagat Kabir Ji) / Change (no author / Guru Arjan Dev Ji / other) / Reject | |
| Related Ang 323 case, line 14771 | `bhagat-run-heading-ang323` | Same ruling as A-11 / Separate ruling required / Leave unchanged | |

Conditions, corrections or further evidence required:

&nbsp;

&nbsp;

Scholar's confirmation:

&nbsp;

Prepared for scholarly review by: Kanwaljit Singh. *(The pack is prepared **for** his review. This
line does not record any review or approval.)*

---

## How a ruling is recorded (engineering, after the reviewer has replied)

1. The reviewer's ruling is copied from his own reply (email or a signed copy of this form) into
   `rulings/` in this folder. The file is kept exactly as he sent it.
2. For each entry the ruling covers, the engineer fills its `g3` block:
   - `decision`: `approve`, `change` or `reject`
   - `reviewer`, and `date` (the date of the ruling)
   - `scope`: the item
   - `evidence`: the path of the ruling file
   - `entry_sha256`: from `python3 pipeline/g3_gate.py --hash <entry>`

   The engineer then sets `status` to `approved` or `rejected`. A **Change** edits the entry first,
   so its hash changes, and the edited entry is what the reviewer confirms.
3. `python3 pipeline/g3_gate.py --release-check` must pass, and then the gated rebuild runs.

Never fill a `g3` field from this blank form, from a recommendation, or from anything the reviewer
has not explicitly given.
