# Attribution: who composed each line

`lines.author` names the voice (Guru, Bhagat, Bhatt or Gursikh) of every line. It is metadata
*about* the scripture and never changes a character of it. This page explains where the value
comes from and how it is proven.

## Why a dedicated pass

`build_corpus.py` reads a composition's author from its heading and carries it forward until the
next heading that names someone. Several kinds of printed evidence were not read, so authorship
"bled" from one composition into the next. A line-level audit (2026-10-23) against an independent
edition found 1,047 lines affected, for example:

- Baba Sheikh Farid Ji's saloks (Angs 1377–1384) tagged as Guru Amar Das Ji's or Guru Arjan Dev Ji's,
  because a `ਮਃ ੩ ॥` label inside his collection was never closed;
- Bhagats Dhanna, Sain, Pipa, Sadhna and Parmanand, and Baba Sundar Ji (Ramkali Sadu), absent from
  the author list because their headings use inflected names (`ਧੰਨੇ ਜੀ ਕੀ`, `ਸਧਨੇ ਕੀ`) or bare labels
  (`ਪੀਪਾ ॥`, `ਸ੍ਰੀ ਸੈਣੁ ॥`);
- Japji with no author at all (no Mahalla is printed over it).

## The rules (`pipeline/attribution.py`, post-pass 4 of `build_corpus.py`)

Each rule is tied to something printed in the Granth:

| Rule | Evidence |
|---|---|
| **P** | A numbered pauri label names its Mahalla: `ਪਉੜੀ ੫ ॥` (Guru Arjan Dev Ji's pauris in Guru Ram Das Ji's Gauri Vaar). |
| **L** | A heading or bare label names the voice of the next shabad/salok: `ਆਸਾ ਬਾਣੀ ਭਗਤ ਧੰਨੇ ਜੀ ਕੀ`, `ਧੰਨਾ ॥`, `ਮਃ ੫ ॥`. A label covers **one** shabad or salok. |
| **C** | A shabad under an unnamed heading (`ਬਾਣੀ ਭਗਤਾਂ ਕੀ`, `ਸਾਰੰਗ ॥`) is signed in its final stanza with one Bhagat's pen-name and never `ਨਾਨਕ`. Words that are also ordinary vocabulary (`ਨਾਮੇ` "in the Name", `ਸੈਣੁ` "friend", `ਧੰਨਾ` "blessed", `ਪਰਮਾਨੰਦ` "bliss") count only in a strict signing position (`ਕਹਿ`, `ਬਦਤਿ`, `ਪ੍ਰਣਵੈ`, `… ਭਣੈ`). |
| **N** | An unsigned shabad takes the signer of its numbered series: the running count (`॥੨॥੧॥`, `॥੨॥੨॥`, `॥੪॥੩॥`) continues with no heading between. |
| **S** | In a Bhagat's salok collection (`ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ`) every salok is the collection's, except one introduced by a `ਮਃ N ॥` label, which ends at its own number. |
| **H** | Otherwise a section heading's named Bhagat repairs bleed from a Guru or a missing tag. It never moves a line from one Bhagat to another. |
| **V** | A bare `ਸਲੋਕੁ ॥` in a Guru's Vaar that opens with `ਕਬੀਰ`/`ਫਰੀਦਾ` is that Bhagat's salok. |
| **E** | Approved editorial decisions in `pipeline/attribution_ledger.json`. |

A heading that names a Mahalla always wins over a pen-name in the verse (Ang 326:
`ਗਉੜੀ ਕਬੀਰ ਜੀ ਕੀ ਨਾਲਿ ਰਲਾਇ ਲਿਖਿਆ ਮਹਲਾ ੫` stays Guru Arjan Dev Ji's).

## The ledger (`pipeline/attribution_ledger.json`)

| Status | Meaning |
|---|---|
| `approved` | Applied by rule E (Japji → Guru Nanak Dev Ji; Ramkali Sadu → Baba Sundar Ji, owner-approved before G3). A G3 entry is `approved` only with a complete, signed ruling in its `g3` field (`pipeline/g3_gate.py`). |
| `held` | A G3 entry applied **only** in a held draft build, so its effect can be proved; never releasable (`g3_gate.py --release-check` fails). Dataset 1.3.0: Surdas's single line, Ang 1253, and the Bhagat-run heading on Ang 524. |
| `proposed` | Recorded for scholarly review, changes nothing: Bhai Mardana's saloks (Ang 553), Raagmala, the per-Bhatt splits, saloks signed by other Bhagats inside Kabir's collection, the Bhagat-run heading on Ang 323. |
| `keep` | Our tag stands on printed evidence although the independent edition differs (Angs 326, 1136, 1253). |

## The G3 approval gate (`pipeline/g3_gate.py`)

Every ledger load, both build passes and CI go through one validator. It enforces a closed status set,
the registry of G3 items, owner approvals pinned by hash, complete rulings (reviewer of record, date,
scope, the reviewer's own reply as a file **signed with his registered SSH key**, and a hash binding the
ruling to what the entry does), and that the committed corpus matches the statuses. On a pull request,
`.github/workflows/g3-gate.yml` runs the **base branch's** gate against the pull request's tree, so a
pull request cannot change the rules it is judged by. Records: `validation/attribution-g3-review/`
(`AUDIT-TRAIL.md`, `RISKS.md`, `SIGN-OFF.md`).

## The verification gate (`pipeline/verify_attribution.py`)

```bash
python3 pipeline/verify_attribution.py <pre.jsonl> corpus/sggs.jsonl --oracle database.sqlite \
  --review-dir validation/attribution-review
```

1. Only `author` differs between the previous and the new corpus (text, `comp_id`, `line_no`,
   `is_header`, markers are identical).
2. The pass is idempotent.
3. Every line that still disagrees with the independent edition lies inside a ledger entry.

The review pack (`validation/attribution-review/README.md`) lists each re-attributed composition
with its printed heading and its first and last verse, verbatim, for human review.

The independent edition (`database.sqlite`, pinned by `pipeline/shabados.SHA256SUMS`) is a
cross-check only: it is never copied into the corpus, never shipped and never cited.
`pipeline/attribution_audit.py` aligns it line by line to produce the diff.

## Structure decisions (`pipeline/structure_ledger.json`)

Where a line belongs (its `section`) and where a composition begins (`is_header`, `comp_id`) are
read from the print by `build_corpus.py`. The few places the detectors miss are reviewed ledger
entries applied by `pipeline/structure.py` (post-pass 5), never detector changes, because a new
heading found by the detector would renumber every later composition.

| Kind | Effect |
|---|---|
| `section` | Lines `start_id`–`end_id` move from section `from` to `to` (Salok Bhagat Kabir Ji, Ang 1364; Salok Sheikh Farid Ji, Ang 1377). |
| `opens` | A printed label stored as a verse becomes the heading of its own composition, issued an id above every id the build has issued (Ang 695: `ਸ੍ਰੀ ਸੈਣੁ ॥`, `ਪੀਪਾ ॥`, `ਧੰਨਾ ॥` → 5381–5383). |

The same status rules apply: only `approved` entries change anything. Each entry states the value it
expects (`from`); the build stops if the corpus no longer matches.
