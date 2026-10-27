# Held for G3: four attribution and structure fixes (dataset 1.3.0)

**Build status: complete.** The database is rebuilt from the PDF through every gate. Reconcile is
char-exact, the golden suite and the ShabadOS gate pass, and scripture is byte-identical. `make ci` passes
every gate except `g3-release`, which fails by design until the rulings are recorded. `proofs.md` has the
outputs. The audit reproduced the rebuild byte for byte (`AUDIT-REPORT.md` § 3).

**Status: HELD. The G3 scholar's sign-off is required. No ruling has been given.** The fixes are applied
in a draft pull request, as `held` ledger entries, so that the rebuild can prove their exact effect.
**Merging is not the approval:** the approval is the reviewer's own ruling, recorded in each entry's `g3`
block (`SIGN-OFF.md`). The CI check `g3_gate.py --release-check` fails until it is recorded.

**Read with the audit (2026-10-27).** An independent audit re-checked this pack against the print and the
sources, and corrects several statements below. The corrected statements are marked *[corrected]*.

- `DECISIONS.md`: one decision record per item, with each question kept separate.
- `EVIDENCE-LEDGER.md`: every claim, its source and where it was found.
- `CONTRADICTIONS.md`: where the sources agree and where they differ.
- `RISKS.md`: technical risks.
- `AUDIT-REPORT.md`: what was checked, how, and the results.
- `SIGN-OFF.md`: the blank form for the reviewer.

**What changes.** Only facts *about* lines change: who the dataset credits a line to (`author`), which
part of the Granth it is filed under (`section`), whether it is a heading (`is_header`), and which
composition it belongs to (`comp_id`, `line_no`). **No Gurmukhi character changes.** The technical section
at the end gives the proofs.

**How the quotes were made.** Every quoted Gurmukhi line in this pack was filled in from the dataset by a
script (`scripts/data/g3_attribution_pack.py`, and the same lookup for this page). None was typed by hand.
The short names in running text, such as a heading's first words, were checked against the corpus by the
same script. Each quote carries its line id and its Ang, "Sri Guru Granth Sahib Ji · Ang N". `evidence.md` shows every line
that an item touches, with its value before and after this pull request and ShabadOS's record for it.

**The sources compared.**

- **The print.** This is the source of record that the corpus is proven against, character for character.
- **ShabadOS 4.8.7.** This is the pinned ShabadOS database (`pipeline/shabados.SHA256SUMS`). It is a
  cross-check only. Nothing from it is copied into the dataset. It also records the SikhiToTheMax/BaniDB
  shabad id (`sttm`), so it shows how BaniDB groups the lines too.
- **The app's draft roster note** for Bhagat Surdas Ji (G3 item R-21, still a draft). It is quoted here only
  where it bears on an item.

This pack picks no tradition. Where the sources differ, it says so and lists the options. Each item ends
with a decision line in the form the G3 1.4.9 pack uses: **Approve** (ship as in this pull request),
**Change** (write what you want), or **Reject** (leave the dataset as it is).

| # | G3 1.4.9 item | Ang | In one line |
|---|---|---|---|
| 1 | A-07 | 1253 | The single line before `ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ` is credited to Bhagat Surdas Ji, not Bhagat Namdev Ji. |
| 2 | A-08 | 1363–1384 | Salok Bhagat Kabir Ji and Salok Sheikh Farid Ji become their own sections, out of `ਚਉਬੋਲੇ`. |
| 3 | A-10 | 695 | The three Bhagat labels become headings, so Sain, Pipa and Dhanna each have their own composition. |
| 4 | A-11 (Ang 524) | 524 | The Bhagat-run heading of Gujri is credited to the run's first Bhagat, as 11 of the other 12 do (Ang 323's is still open). |

---

## 1 · A-07 · Bhagat Surdas Ji's line, Ang 1253

**What the print shows.** These lines appear in this order on Ang 1253:

> ਨਾਮਦੇਵ ਜਾ ਕੇ ਜੀਅ ਐਸੀ ਤੈਸੋ ਤਾ ਕੈ ਪ੍ਰੇਮ ਪ੍ਰਗਾਸ ॥੨॥੩॥ *(line 53924, the close of Bhagat Namdev Ji's third shabad)*
> ਸਾਰੰਗ ॥ · ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥ *(lines 53925–53926, the heading of the next shabad)*
> ਪਰਮਾਨੰਦ ਸਾਧਸੰਗਤਿ ਮਿਲਿ ਕਥਾ ਪੁਨੀਤ ਨ ਚਾਲੀ ॥੩॥੧॥੬॥ *(line 53934, Bhagat Parmanand Ji's closing verse)*
> **ਛਾਡਿ ਮਨ ਹਰਿ ਬਿਮੁਖਨ ਕੋ ਸੰਗੁ ॥** *(line 53935)*
> ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ ॥ · ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥ *(lines 53936–53937, a heading)*
> ਸੂਰਦਾਸ ਮਨੁ ਪ੍ਰਭਿ ਹਥਿ ਲੀਨੋ ਦੀਨੋ ਇਹੁ ਪਰਲੋਕ ॥੨॥੧॥੮॥ *(line 53943, the close of that shabad)*
>
> — Sri Guru Granth Sahib Ji · Ang 1253

Line 53935 has no heading, no pen-name and no number of its own.

**The printed count.** The Bhagat Bani of Sarang numbers its compositions as one running series. The last
number in each closing marker, as printed, runs:

| line | closes | last number |
|---|---|---|
| 53882 | Kabir (1st) | ੧ |
| 53892 | Kabir (2nd) | ੨ |
| 53924 | Namdev (his own count; 3 shabads) | ੩ |
| 53934 | Parmanand | ੬ |
| 53935 | the single line | none |
| 53943 | `ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ` shabad | ੮ |
| 53951 | Kabir | ੯ |

The count goes from 6 to 8. One composition is counted between Parmanand's shabad and the shabad headed
`ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ`, and the single line is the only thing printed there. The same count also includes
the `ਮਹਲਾ ੫` shabad in the Bhagat series. This is an observation for the scholar. The pack draws no
conclusion from it.

**The dataset today (1.2.0).** Line 53935 is credited to **Bhagat Namdev Ji**. No source supports that. The
build carries the last named heading forward, here `ਸਾਰੰਗ ਬਾਣੀ ਨਾਮਦੇਉ ਜੀ ਕੀ ॥` (line 53893), until another heading names
someone. In 1.1.0, Parmanand's shabad was corrected from its own heading and signature. Line 53935 has no
printed evidence of its own, so 1.1.0 left it as it was and flagged it for G3. It sits in composition 4846
(Parmanand's) as that composition's 11th line, by position. The app therefore counts 35 voices, and Surdas
is not among them.

**ShabadOS 4.8.7.**

- It credits the line to **Bhagat Surdas Ji**, as a shabad of its own (`5FC`, a verse line).
- It records the same BaniDB/STTM id, **4531**, for that line and for Parmanand's shabad. BaniDB groups the
  single line with Parmanand's shabad.
- It credits the shabad headed `ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ` (lines 53936–53943) to **Bhagat Surdas Ji** as well.
  The dataset credits that shabad to Guru Arjan Dev Ji, from the printed `ਮਹਲਾ ੫`. The reviewed ledger
  entry `keep-ang1253-surdas-shabad` and the ShabadOS flag `sarang-m5-surdas` record that difference.
  **This pull request does not change it.**

**The app's draft roster note (R-21)** says that the Granth keeps one line of Surdas's, and that the shabad
after it, headed with his name, is Guru Arjan Dev Ji's, "written in response". It cites the Encyclopaedia of
Sikhism and Prof. Sahib Singh, who agree that the following shabad is Guru Arjan Dev Ji's although it names
Surdas where the Gurus usually sign ਨਾਨਕ. It also notes that some scholars hold there were two Surdases.

**Where the sources differ.** Three separate questions are involved, and they should not be merged:

1. **Who composed line 53935?** ShabadOS, the roster note and the findings file all say **Bhagat Surdas Ji**.
   The current tag, Bhagat Namdev Ji, has no source behind it.
2. **Which composition does it belong to?** Here the sources disagree:
   - (a) **Its own.** ShabadOS files it as a separate shabad, and the printed count leaves one place for it.
   - (b) **With Parmanand's shabad, before it.** BaniDB's shabad id groups it there. The dataset puts it
     there today because of where it is printed.
   - (c) **With the `ਮਹਲਾ ੫` shabad after it, which answers it and names Surdas.** This is the "written in
     response" reading. The line is printed *before* that shabad's heading. The dataset never moves a verse,
     and it requires every composition to begin with its heading. So the dataset can record this reading
     only as a note, not by grouping.

   Secondary accounts also say that the line is the opening of a longer composition by Surdas, of which the
   Granth sets down only this line. This pack has not verified that, and nothing here depends on it.
3. **Who composed the following shabad?** The print says `ਮਹਲਾ ੫`, and the dataset keeps Guru Arjan Dev Ji.
   ShabadOS says Surdas. This question is outside this item and unchanged, and it is listed so that it is
   not lost.

**The change in this pull request.** The ledger entry `surdas-line` (`pipeline/attribution_ledger.json`)
moves from `proposed` to `held` (applied in this draft; no ruling yet):

| line | field | 1.2.0 | 1.3.0 |
|---|---|---|---|
| 53935 | `author` | Bhagat Namdev Ji | **Bhagat Surdas Ji** |

The change is to the author only, so question 2 stays at (b), by position. The app then counts **36
voices**, and the voices of Sarang go from 9 to 10. The ShabadOS flag `surdas-tuk` is removed, because the
dataset and ShabadOS now agree on this line.

If you choose 2(a), a follow-up is needed: a composition that opens with a verse, not a heading, needs a new
ledger kind and an explicit exception to the structural invariant. 2(c) cannot be represented by grouping.

**Decision 1 (A-07, line 53935):** ☐ Approve (Bhagat Surdas Ji, author only, as in this pull request) ·
☐ Change (author: ______ · composition: ☐ (a) own ☐ (b) as now ☐ (c) note only) · ☐ Reject (keep Bhagat Namdev Ji)

---

## 2 · A-08 · Salok Bhagat Kabir Ji and Salok Sheikh Farid Ji, Angs 1363–1384

**What the print shows.**

> ਚਉਬੋਲੇ ਮਹਲਾ ੫ *(line 58273, Ang 1363)*
> ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ *(line 58297, Ang 1364)*
> ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ *(line 58791, Ang 1377)*
> ਸਵਯੇ ਸ੍ਰੀ ਮੁਖਬਾਕ੍ਯ੍ਯ ਮਹਲਾ ੫ ॥ *(line 59089, Ang 1385, the Swaiyye that follow)*

**The dataset today (1.2.0).** One section, `ਚਉਬੋਲੇ`, runs from Ang 1363 to Ang 1384 and holds 815 lines:
the Chaubole, then both salok collections. The pipeline's own list of sections already names
`ਸਲੋਕ ਭਗਤ ਕਬੀਰ` and `ਸਲੋਕ ਸੇਖ ਫਰੀਦ`. But the detector opens a section after the raags only when the
heading line also carries a Mahalla or ੴ, and these two headings carry neither. The headings' `author`
values are already right: Bhagat Kabir Ji and Sheikh Farid Ji.

**ShabadOS 4.8.7** has three sections: Chaubolas Fifth Mehl (Angs 1363–1364), Salok Kabeer Jee
(1364–1377) and Salok Fareed Jee (1377–1385). The Gurus' saloks printed inside each collection (the
`ਮਹਲਾ ੫ ॥` labels at Ang 1375 and the `ਮਃ ੩ ॥` label at Ang 1378, among others) stay inside that
collection's section there too.

**The change in this pull request.** Two `section` entries in the new `pipeline/structure_ledger.json`:

| lines | Angs | `section` 1.2.0 | `section` 1.3.0 | lines |
|---|---|---|---|---|
| 58273–58296 | 1363–1364 | ਚਉਬੋਲੇ | ਚਉਬੋਲੇ (unchanged) | 24 |
| 58297–58790 | 1364–1377 | ਚਉਬੋਲੇ | **ਸਲੋਕ ਭਗਤ ਕਬੀਰ** | 494 |
| 58791–59087 | 1377–1384 | ਚਉਬੋਲੇ | **ਸਲੋਕ ਸੇਖ ਫਰੀਦ** | 297 |

The Gurus' saloks inside each collection stay in that collection's section, as the print sets them and as
ShabadOS files them. Their `author` does not change.

**Open choices.** The section *names* follow the pipeline's own short canonical form (as `ਚਉਬੋਲੇ` stands for
`ਚਉਬੋਲੇ ਮਹਲਾ ੫`). The alternative is the full printed heading. The app's Index currently keys its English
names on the full headings, so it needs the short names added either way. The boundaries are as printed,
from heading to heading.

**Decision 2 (A-08):** ☐ Approve (split as in this pull request) · ☐ Change (names or boundaries: ______) · ☐ Reject (keep one section)

---

## 3 · A-10 · Composition 2749, Ang 695

**What the print shows.** One heading opens the Dhanasari Bhagat Bani. Four shabads follow, and each one
closes with its own number in a single running series. Each shabad after the first is opened by a bare
name label:

> ਧਨਾਸਰੀ ਬਾਣੀ ਭਗਤਾਂ ਕੀ ਤ੍ਰਿਲੋਚਨ *(line 30064, the heading)*
> ਬਦਤਿ ਤ੍ਰਿਲੋਚਨ ਰਾਮ ਜੀ ॥੬॥੧॥ *(line 30080, Bhagat Trilochan Ji's close)*
> **ਸ੍ਰੀ ਸੈਣੁ ॥** *(line 30081)* … ਸੈਨੁ ਭਣੈ ਭਜੁ ਪਰਮਾਨੰਦੇ ॥੪॥੨॥ *(line 30091)*
> **ਪੀਪਾ ॥** *(line 30092)* … ਪੀਪਾ ਪ੍ਰਣਵੈ ਪਰਮ ਤਤੁ ਹੈ ਸਤਿਗੁਰੁ ਹੋਇ ਲਖਾਵੈ ॥੨॥੩॥ *(line 30098)*
> **ਧੰਨਾ ॥** *(line 30099)* … ਜਨੁ ਧੰਨਾ ਲੇਵੈ ਮੰਗੀ ॥੨॥੪॥ *(line 30109)*
>
> — Sri Guru Granth Sahib Ji · Ang 695

**The dataset today (1.2.0).** The three labels are stored as verses (`is_header = 0`). All 46 lines
therefore share Trilochan's composition, 2749. The shabad sheet and a Hukam draw treat four Bhagats' bani
as one composition. The *authors* have been right since 1.1.0 (G3 A-01 to A-03, which ask you to confirm
them). Only the grouping is wrong.

**ShabadOS 4.8.7** has four separate shabads: `R0X` (BaniDB 2639, Trilochan), `LB4` (2640, Sain), `E2C`
(2641, Pipa) and `37J` (2642, Dhanna). It is not consistent about the labels themselves: `ਸ੍ਰੀ ਸੈਣੁ ॥` and
`ਧੰਨਾ ॥` are typed as headings, but `ਪੀਪਾ ॥` is typed as a verse.

**The change in this pull request.** Three `opens` entries in `pipeline/structure_ledger.json`:

| label line | `is_header` | lines | `comp_id` 1.2.0 → 1.3.0 |
|---|---|---|---|
| 30081 | 0 → **1** | 30081–30091 (11) | 2749 → **5381** |
| 30092 | 0 → **1** | 30092–30098 (7) | 2749 → **5382** |
| 30099 | 0 → **1** | 30099–30109 (11) | 2749 → **5383** |

`line_no` restarts at 1 in each new composition. Composition 2749 keeps the heading and Trilochan's
shabad (17 lines).

**Why the new ids are 5381–5383, not in reading order.** Composition ids are never moved and never reused.
Every id up to 5380 has been issued (5377–5380 were burned in v1.1.4). The only ids free for these shabads
are therefore above that. A search of sggs-platform and gurbani-soul-ios found no code that orders by
`comp_id`: readers order by line id. A saved link to composition 2749 now opens Trilochan's shabad alone.
*[corrected]* A saved *line* does **not** open its own shabad on its own: the iOS app and the web store the
line's composition id with it, so a saved Sain, Pipa or Dhanna line reopens composition 2749
(`RISKS.md` C-1).

**Open choices.** The label becomes the heading of its shabad. This is ShabadOS's reading for two of the
three labels. *[corrected]* It is **not** how the dataset treats `ਨਾਮਦੇਵ ॥` (line 50285): that label is still
a verse inside Bhagat Ravidas Ji's composition 4426, the same defect, unfixed (`DECISIONS.md` A-10). The print
runs all three labels on inline, so its layout does not settle heading versus verse.
The alternative is to leave the labels as verses and the grouping as it is.

**Decision 3 (A-10):** ☐ Approve (fix as in this pull request) · ☐ Change: ______ · ☐ Reject (leave as one composition)

---

## 4 · A-11 · The Bhagat-run heading on Ang 524

**What the print shows.** Gujri ki Vaar (Mahalla 5) ends, and the Bhagat Bani of Gujri begins:

> ਗੁਰ ਪ੍ਰਸਾਦਿ ਨਾਨਕ ਸਚਿ ਸਮਾਇਆ ॥੨੧॥੧॥੨॥ *(line 23469, the Vaar's last pauri)*
> ਸੁਧੁ ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ *(line 23470)*
> ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥ *(line 23471)*
> ਸ੍ਰੀ ਕਬੀਰ ਜੀਉ ਕਾ ਚਉਪਦਾ ਘਰੁ ੨ ਦੂਜਾ ॥ *(line 23472)*
>
> — Sri Guru Granth Sahib Ji · Ang 524

Line 23470 holds two things. Its first word, `ਸੁਧੁ`, is the rubric that closes the Vaar. The rest is the
heading of the Bhagat Bani. *[corrected]* In the print they are **not** one line: `ਸੁਧੁ` is the last word of
the Vaar's final printed line, and the heading is a separate centred line. The corpus record joins them,
and it does the same on Angs 323, 517 and 654 (`DECISIONS.md` A-11, reading (d)).

**The dataset today (1.2.0).** Line 23470 is credited to **Guru Arjan Dev Ji (M5)**. *[corrected]* Of the
other twelve Bhagat-run headings, eleven (`… ਬਾਣੀ ਭਗਤਾ ਕੀ`) carry the first Bhagat of their run (the table in the G3 1.4.9 pack,
section 6). This one was skipped because the attribution pass never re-credits a line that starts with
`ਸੁਧੁ`, since that word closes the composition before it.

**ShabadOS 4.8.7** puts `ਸੁਧੁ` at the end of the Vaar's last line and files the heading under **Bhagat
Kabir Ji** (`6AM`, BaniDB 2006).

**The change in this pull request.** The ledger entry `bhagat-run-heading-ang524` (`held`; no ruling yet):

| line | field | 1.2.0 | 1.3.0 |
|---|---|---|---|
| 23470 | `author` | Guru Arjan Dev Ji (M5) | **Bhagat Kabir Ji** |

**Where the choices differ.**

- (a) **The run's first Bhagat.** This pull request takes this option, which matches 11 of the other 12
  headings, and ShabadOS.
- (b) **Keep Guru Arjan Dev Ji**, because the line opens with the closing rubric of his Vaar.
- (c) **No author on any Bhagat-run heading.** This is A-11's second option. *[corrected]* It would change 13
  headings (14 counting Suhi line 33831), so it would be a separate entry.

**A twin outside the G3 list.** Line 14771 on Ang 323, `ਸੁਧੁ ਕੀਚੇ ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ`, has the same shape: the closing rubric of
Gauri ki Vaar (Mahalla 5), run into Gauri's Bhagat-run heading. It is still Guru Arjan Dev Ji's, and
ShabadOS files it under Bhagat Kabir Ji in the same way. It is recorded as `bhagat-run-heading-ang323` with
status **proposed**, so it **changes nothing** until you rule on it.

**Decision 4 (A-11, line 23470):** ☐ Approve (Bhagat Kabir Ji, as in this pull request) · ☐ Change: ______ · ☐ Reject (keep Guru Arjan Dev Ji)
**And line 14771 (Ang 323):** ☐ The same ruling as line 23470 · ☐ Leave as it is

---

## After your ruling

The reviewer replies with the form in `SIGN-OFF.md`. An engineer then records his ruling exactly as given:
the reply goes into `rulings/` in this folder, and each entry's `g3` block gets the decision, reviewer, date,
scope, evidence path and entry hash, with its status moved to `approved` or `rejected`
(`SIGN-OFF.md`, "How a ruling is recorded").

- **Change.** The entry is edited first, then the reviewer confirms the edited entry.
- **Change or Reject.** The gated rebuild runs again, and the pack is regenerated.

Only when `python3 pipeline/g3_gate.py --release-check` passes can the dataset become 1.3.0. Then
sggs-platform and gurbani-soul-ios each take one dataset bump.

## Technical section

**Mechanism.** No database is edited by hand. All changes come from the build:

- `pipeline/attribution_ledger.json`, rule E of `pipeline/attribution.py`. This existing path applies an
  entry only when `pipeline/g3_gate.py` lets it through: owner-approved, a complete G3 ruling, or `held`
  in a draft that the release check keeps from shipping.
- `pipeline/structure_ledger.json` with the new `pipeline/structure.py` (post-pass 5 of `build_corpus.py`).
  It changes `section`, `is_header`, `comp_id` and `line_no` only, and only for entries the gate lets
  through. Every
  entry states the value it expects to find, and the build stops if the corpus no longer matches. A new
  composition takes an id above every id the build has issued.

**Proofs.** `proofs.md` records the commands and their output.

- **Reconcile:** the corpus equals the PDF, character for character (1,643,385 characters).
- **Golden suite:** passes.
- **`diff_scripture.py`:** of the `lines` columns, only `author`, `section`, `is_header`, `comp_id` and
  `line_no` change, plus three columns derived from them: `source_category` (line 23470, Gurus to Bhagats)
  and `stanza_index`/`pada_total` (the three new heading lines).
- **`scripture_sha256` and `t0_sha256`:** unchanged.
- **Main `fts` and `fts_en` indexes:** unchanged. The verse-only `fts_tri` and `fts_shabad` lose the
  three label lines and regroup the split composition.
- **ShabadOS gate:** passes, and agreement rises by one line.
- **`vaars`, `vaar_units`, `banis`, translations:** content-identical (`compare_builds.py`).

**What moves downstream.** `downstream.md` lists every count that changes, for the platform and iOS
bumps. The headline numbers:

- 36 voices (was 35).
- Sarang has 10 voices (was 9).
- 4,530 compositions (was 4,527), with `max(comp_id)` 5,383 (was 5,376).
- 15 sections (was 13): `ਚਉਬੋਲੇ` drops from 815 lines to 24.
- Dhanasari `n_shabads` is 108 (was 105).
- `word_freq` loses the 3 label words.

Every changed line is listed in `changes.csv`.
