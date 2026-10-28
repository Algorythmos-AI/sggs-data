# G3 decision records: dataset 1.3.0

There is one record for each item awaiting Kanwaljit Singh's ruling. **No item has been ruled on.**
The recommendations in `RECOMMENDATIONS.md` (PR #18) are an agent's recommendations, not rulings.

Each record keeps four questions apart, because a ruling on one must not quietly settle another:

- **Q-author:** who composed the line or lines.
- **Q-composition:** which composition (`comp_id`) the lines belong to.
- **Q-section:** which part of the Granth they are filed under (`section`).
- **Q-heading:** whether a printed line is a heading (`is_header`) or a verse.

Every conclusion carries exactly one label:

- **Verified fact:** directly inspected; the location is given.
- **Corroborated:** supported by sources that are genuinely independent of each other.
- **Interpretation:** a reasoned reading, not a fact.
- **Disputed:** the sources conflict.
- **Unverified:** not inspected or not reproduced.
- **Pending scholarly decision:** only the reviewer can settle it.

**About the sources.**

- **The print** is the source PDF the corpus is proven against, read as page images.
  - Its page *n* (1-based) carries the printed Ang number at its head. This was checked on each page
    used: PDF 748 → Ang 695, 1306 → 1253, 577 → 524, 376 → 323, 1417 → 1364, 1430 → 1377.
  - The edition is typeset and runs text on: only principal headings are set as centred lines. Labels
    such as `ਰਹਾਉ ॥` and the bare Bhagat names run on inside the verse. **Layout in this source therefore
    cannot by itself decide whether a run-on label is a heading.**
- **ShabadOS 4.8.7 and BaniDB.** ShabadOS carries the BaniDB/STTM shabad ids. It splits 13 of them,
  and the reverse direction was not fully checked. For grouping they are **one source family**, not two.
- **Sahib Singh and Faridkot.** The Darpan and the Faridkot Teeka are quoted **as transcribed in ShabadOS
  4.8.7**, which does not state their edition. Some Darpan notes are cut off at 1,000 characters there.
  No printed copy of either was consulted.
- **The Encyclopaedia of Sikhism** is cited only where a page image was read (`EVIDENCE-LEDGER.md` §
  EoS). Its four volumes are different editions: I 4th ed. 2002; II and III 3rd ed. 2011; IV 2nd ed. 2004.
  It contradicts itself on several points.

---

## A-07 · Ang 1253, line 53935: `ਛਾਡਿ ਮਨ ਹਰਿ ਬਿਮੁਖਨ ਕੋ ਸੰਗੁ ॥` *(line 53935)*

**Ledger:** `surdas-line` (`held`). This changes `author` only, from Bhagat Namdev Ji to Bhagat Surdas Ji.

**What the print shows** (PDF page 1306, read as an image): **Verified fact**

1. Parmanand's shabad closes `ਪਰਮਾਨੰਦ ਸਾਧਸੰਗਤਿ ਮਿਲਿ ਕਥਾ ਪੁਨੀਤ ਨ ਚਾਲੀ ॥੩॥੧॥੬॥` *(line 53934)*, and the
   printed line breaks there.
2. Line 53935 is printed **on a line of its own**, flush left, with no name or heading.
3. Then comes the centred heading `ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ ॥` *(line 53936)* with `ੴ`. That shabad closes
   `ਸੂਰਦਾਸ ਮਨੁ ਪ੍ਰਭਿ ਹਥਿ ਲੀਨੋ ਦੀਨੋ ਇਹੁ ਪਰਲੋਕ ॥੨॥੧॥੮॥` *(line 53943)*.
4. The running count goes ੬ → ੮. One number falls between Parmanand's shabad and the `ਮਹਲਾ ੫` shabad.

**Q-author: who composed line 53935?**

| Reading | What supports it | What weighs against it | Label |
|---|---|---|---|
| Bhagat Surdas Ji | EoS IV p. 288 (SŪRDĀS): "it is not a complete hymn but a single line". Sahib Singh's note on 53935 (ShabadOS transcription): "ਇਹ ਇਕ ਤੁਕ 'ਸੂਰਦਾਸ' ਜੀ ਦੀ ਹੈ". Faridkot on 53935 speaks of "Surdas Ji's whole shabad" in Bhai Banno's Bir. ShabadOS files the line as its own shabad `5FC`, under Bhagat Surdas Ji. The next printed heading names ਸੂਰਦਾਸ. | The line carries no name in the print. | Interpretation, with strong agreement among the sources read. **Not "corroborated"**: the commentaries are read through the ShabadOS transcription, and ShabadOS is not independent of BaniDB. |
| Unattributed | The print gives no name. | Every source read names Surdas. | Interpretation |
| Bhagat Namdev Ji (1.2.0) | Nothing. Namdev's last shabad closes earlier on the Ang and Parmanand's stands between. The tag is carried forward by the pipeline. | Everything above. | Verified fact that no source read supports it |

**Q-composition** (a separate question; this PR does not change it):

- (a) **Its own composition.** The print's own line, the count's empty slot, Sahib Singh's count note
  ("ਗਿਣਤੀ ਵਿਚ ਉਸ ਨੂੰ ਸਾਰੇ ਸ਼ਬਦ ਵਾਂਗ ਗਿਣਿਆ ਹੈ") and ShabadOS's separate shabad `5FC` all point this way.
  Against it: there is no heading, and the dataset's rule is that every composition opens with one.
- (b) **With Parmanand's shabad, as now.** Only BaniDB's id 4531 supports this, and ShabadOS splits it
  out. The print's line break and the count both weigh against it.
- (c) **With the following `ਮਹਲਾ ੫` shabad.** Sahib Singh says that shabad was composed to expound this
  line ("ਉੱਪਰ-ਦਿੱਤੀ ਹੋਈ ਇੱਕ ਤੁਕ ਦੀ ਵਿਆਖਿਆ ਕਰਨ ਲਈ"), and so does EoS IV p. 288 ("to explain and supplement the
  single line"). PR #18 left out Sahib Singh's remark. Against it: the line is printed
  *before* that shabad's heading and `ੴ`, and no data source groups them.
- **Label: Pending scholarly decision.** The print's line break is a **Verified fact** that counts against
  (b). It does not choose between (a) and (c).

**A question outside this item:** who composed lines 53936–53943? It is listed so that it is not lost.

- The print says `ਮਹਲਾ ੫`, and Sahib Singh says Guru Arjan Dev Ji.
- **ShabadOS files the shabad (`FHM`) under Bhagat Surdas Ji.**
- Faridkot's preface on 53934 says the Guru composed it, while its gloss of 53943 opens "ਸੂਰਦਾਸ ਜੀ
  ਕਹਿਤੇ ਹੈਂ".
- **The EoS contradicts itself.** Vol. IV p. 288 says Guru Arjan "composed a hymn to explain and
  supplement the single line". Vol. I p. 314 speaks of "one line and a hymn from Sūr Dās".
- **Disputed.** PR #18's statement that "all the sources read agree" on this question is **incorrect**
  (`AUDIT-REPORT.md` § 2).

**For the reviewer:** rule on Q-author for line 53935. Optionally rule on Q-composition (a, b or c). The
question about 53936–53943 stays with the existing `keep-ang1253-surdas-shabad` entry.

---

## A-08 · Angs 1363–1384: `ਚਉਬੋਲੇ`, Salok Bhagat Kabir Ji, Salok Sheikh Farid Ji

**Ledger:** `section-salok-kabir` (lines 58297–58790) and `section-salok-farid` (58791–59087), both
`held`. They change `section` only.

**What the print shows** (PDF pages 1417 and 1430): **Verified fact**

- The Chaubole close ॥੧੧॥.
- A centred heading `ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ` *(line 58297)* follows, with `ੴ`. Kabir's saloks then run to
  ॥੨੪੩॥ *(line 58790)*.
- A centred heading `ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ` *(line 58791)* follows, with `ੴ`. Farid's saloks close ॥੧੩੦॥ on
  **Ang 1384** *(line 59087)*.

  PR #17 writes "Angs 1363–1385". The last line of the range is on Ang 1384, and line 59088 on Ang 1385
  opens the Swaiyye.
- Inside Kabir's collection, saloks ॥੨੪੧॥ and ॥੨੪੨॥ are signed `ਕਹਿ ਨਾਮਾ` and `ਰਵਿਦਾਸ`. This is the
  existing proposed entry `kabir-saloks-signed-by-others`, and it is not part of A-08.

**Q-section.** Three sections, as in this PR. The print gives each collection its own heading, `ੴ` and
numbering. ShabadOS's sections match the 1.3.0 boundaries line for line: 24, 494 and 297 lines. EoS IV p. 240
lists "Salok Kabīr (1364-1377), Salok Farīd (1377-1384)" as separate divisions. No source read supports
one section. **Interpretation**, well supported. The boundaries themselves are a **Verified
fact** of the print.

**Q-section names: a choice for the reviewer.**

- The pipeline's names are `ਸਲੋਕ ਭਗਤ ਕਬੀਰ` and `ਸਲੋਕ ਸੇਖ ਫਰੀਦ`.
- The printed headings are `ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ` and `ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ`.
- The apps already key on the printed forms: iOS `GranthNames.swift:40` (`RISKS.md` C-2).

**Pending scholarly decision.**

**Q-author** is unchanged by this item. The Gurus' saloks inside each collection keep their `ਮਃ`
attribution. **Verified fact** (ShabadOS agrees line for line).

**A correction to PR #18, and a dispute between sources.** PR #18 says Faridkot "names the four Bhagats
they are addressed to". The Faridkot text on line 58296 (ShabadOS transcription) says something else: the
Guru set the **words (ਬਚਨ)** of ਸੰਮਨ, ਮੂਸਨ, ਜਮਾਲ and ਪਤੰਗ in the Chaubole metre. EoS II p. 335 (JAMĀL)
says the Chaubole are "addressed to four devotees". **Disputed:** the four are speakers in Faridkot's
reading and addressees in the EoS. This bears on how the Chaubole are described, not on the A-08
boundaries. The same gloss
adds "ਵਾ ਏਹ ਸਲੋਕ ਪਤੰਗ ਭਗਤ ਨੇ ਕਹਾ ਹੈ" ("or Bhagat Patang said this salok"). That is an authorship remark on
the 11th Chauboli, outside A-08, recorded so that it is not lost.

**For the reviewer:** approve, change or reject the split, and choose the section names.

---

## A-10 · Ang 695: `ਸ੍ਰੀ ਸੈਣੁ ॥`, `ਪੀਪਾ ॥`, `ਧੰਨਾ ॥` and composition 2749

**Ledger:** `ang695-sain-opens`, `ang695-pipa-opens` and `ang695-dhanna-opens` (all `held`).

- Each label line becomes a heading (`is_header` 0 → 1).
- Lines 30081–30091, 30092–30098 and 30099–30109 move from composition 2749 to new compositions 5381,
  5382 and 5383.
- 2749 keeps Bhagat Trilochan Ji's 17 lines.

**What the print shows** (PDF page 748): **Verified fact**

- The centred heading is `ਧਨਾਸਰੀ ਬਾਣੀ ਭਗਤਾਂ ਕੀ ਤ੍ਰਿਲੋਚਨ`.
- The four shabads close ॥੬॥੧॥, ॥੪॥੨॥, ॥੨॥੩॥ and ॥੨॥੪॥: one running series, each signed (ਤ੍ਰਿਲੋਚਨ,
  ਸੈਨੁ, ਪੀਪਾ, ਧੰਨਾ).
- **The three labels are printed inline**, run on after the previous shabad's closing number, exactly as
  `ਰਹਾਉ ॥` is. They are not set as centred headings.

**Q-composition** (are these four shabads?): every source read treats them as four.

- The print's numbering and signatures.
- ShabadOS's four shabads (BaniDB 2639–2642, one lineage).
- Sahib Singh's separate closing note on each (ShabadOS transcription).
- Faridkot's separate introduction to each. It stores each introduction on the line *before* the
  shabad it introduces, so the anchors 30080, 30091 and 30098 are right. It numbers Sain's and Pipa's
  as ੧ each, per author, where the print has ੨ and ੩.

**Interpretation**, very well supported.

**Q-heading** (is each label a heading?):

- The print's layout cannot decide it, because the labels are run on.
- ShabadOS types `ਸ੍ਰੀ ਸੈਣੁ ॥` and `ਧੰਨਾ ॥` as headings (Sirlekh) and `ਪੀਪਾ ॥` as a verse (Pankti). Its
  line types are inconsistent elsewhere too, so this is weak evidence.
- In the dataset, a composition must open with a heading. Making the label the heading is therefore what
  allows four compositions.

**Interpretation; Pending scholarly decision.**

**A correction to PR #18.** It says the fix "matches how the dataset already treats bare labels such as
`ਨਾਮਦੇਵ ॥`". The only `ਨਾਮਦੇਵ ॥` line, `ਨਾਮਦੇਵ ॥` *(line 50285)* on Ang 1167, is stored as a **verse inside
Bhagat Ravidas Ji's composition 4426**. That is the same defect A-10 fixes, and it is not fixed. Another
possible instance, not analysed here: `ਕਬੀਰੁ ॥` *(line 47529)*. A ruling on A-10 does not cover these;
each needs its own entry.

**What the change does downstream** (`RISKS.md` C-1):

- A saved line, widget or link that stores composition 2749 for a Sain, Pipa or Dhanna line opens
  Trilochan's shabad after the change.
- New ids 5381–5383 lie above every id ever issued, so no existing id moves.

**For the reviewer:** approve, change or reject the three labels as headings of their own compositions.

---

## A-11 · Ang 524, line 23470: `ਸੁਧੁ ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ` *(line 23470)*

**Ledger:** `bhagat-run-heading-ang524` (`held`). This changes `author` from Guru Arjan Dev Ji to
Bhagat Kabir Ji.

**What the print shows** (PDF page 577; image and the PDF's own text lines): **Verified fact**

- `ਸੁਧੁ` is the **last word of the Vaar's final printed line**: `…ਸਚਿ ਸਮਾਇਆ ॥੨੧॥੧॥੨॥ ਸੁਧੁ`.
- `ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ` is a **separate, centred heading line**, with `ੴ`.

**The corpus joins the two.**

- Line 23470 begins with `ਸੁਧੁ` and continues with the heading.
- PR #17 says the line "holds two things" because "the corpus never splits a printed line". In the
  print, `ਸੁਧੁ` and the heading are **not** on one printed line.
- The same join happens at four places:
  - `ਸੁਧੁ ਕੀਚੇ ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ` *(line 14771)*
  - `ਸੁਧੁ ਰਾਗੁ ਗੂਜਰੀ ਵਾਰ ਮਹਲਾ ੫` *(line 23136)*
  - line 23470
  - `ਸੁਧੁ ਰਾਗੁ ਸੋਰਠਿ ਬਾਣੀ ਭਗਤ ਕਬੀਰ ਜੀ ਕੀ ਘਰੁ ੧` *(line 28417)*
- At every other place in the Granth, `ਸੁਧੁ` is a record of its own that closes its Vaar (e.g.
  `ਸੁਧੁ` *(line 6270)*).
- **The dataset already attributes the join both ways.** Verified fact:
  - Line 28417 carries **Bhagat Kabir Ji**, although its `ਸੁਧੁ` closes Sorath ki Vaar. The line
    before it, 28416, is Guru Ram Das Ji's.
  - Line 23136 carries **Guru Arjan Dev Ji**. Its `ਸੁਧੁ` closes the Gujri Vaar of Mahalla 3 (23135 is
    Guru Amar Das Ji's), while the rest of the line heads Guru Arjan Dev Ji's own Vaar.
  - In neither case does the rubric take its Vaar's author. That bears on readings (a) and (c) below:
    no single convention is applied consistently today.

**Verified fact** for the print. Why the extractor joins them is an engineering question, recorded in
`AUDIT-REPORT.md`.

**What this means for A-11.** The attribution question exists **because of this join**. A ruling can
take one of these routes:

| Reading | What supports it | What weighs against it | Label |
|---|---|---|---|
| (a) Bhagat Kabir Ji (this PR) | The heading opens the Bhagat Bani, whose first shabad is Kabir's. 11 of the other 12 such headings in 1.2.0 carry their run's first Bhagat. ShabadOS files the heading line (`6AM`) under Kabir. | The heading names a collection ("ਭਗਤਾ", plural), not one person. ShabadOS can file it under Kabir only because it keeps `ਸੁਧੁ` on the Vaar's line, as the print does. | Interpretation |
| (b) No author for the heading | It names the Bhagats collectively. For Ang 323, Sahib Singh (ShabadOS transcription) says that in the Kartarpur Bir these rubric words stand outside the margin and have no connection with the Bani. | It breaks the convention, and would need a decision across 13 headings (14 if Suhi line 33831 is counted). | Interpretation |
| (c) Guru Arjan Dev Ji (1.2.0) | `ਸੁਧੁ` closes his Vaar (Faridkot reads ॥੨੧॥੧॥੨॥ਸੁਧੁ; ShabadOS keeps it on his line). | It applies the Vaar's author to the Bhagats' heading only because of the join. | Interpretation |
| (d) Not considered by PR #17 or PR #18 | The `ਸੁਧੁ` / heading join is a segmentation question that comes before any attribution. If `ਸੁਧੁ` were its own record, as elsewhere, it would close the Vaar and the heading would be attributed on its own merits. | Changing record boundaries changes the `gurmukhi` field of these lines. That is a scripture-record change: it needs its own logged entry, the reconcile proof and a scholar's review. **Nothing here proposes making it.** | Pending scholarly decision |

**On the count.** PR #17 and PR #18 say "eleven of the twelve" headings carry the run's first Bhagat.
Counting the pattern directly (`…ਬਾਣੀ ਭਗਤਾ(ਂ) ਕੀ` / `…ਭਗਤਾ(ਂ) ਕੀ ਬਾਣੀ`) gives **13** headings:

- in 1.2.0, **11 of 13** carry the first Bhagat, and **two** carry Guru Arjan Dev Ji (23470 and 14771);
- 14 if Suhi line 33831 is counted;
- "eleven of twelve" holds only if Ang 323 is left out.

**Verified fact** (query in `EVIDENCE-LEDGER.md`).

**For the reviewer:** rule on the author of line 23470, and, if you wish, say whether the segmentation
question (d) should be opened as its own item.

## Related · Ang 323, line 14771: `ਸੁਧੁ ਕੀਚੇ ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ` *(line 14771)*

**Ledger:** `bhagat-run-heading-ang323` (`proposed`; it changes nothing until ruled on).

**Examined on its own, not by analogy:**

- **What the print shows** (PDF page 376): `ਸੁਧੁ ਕੀਚੇ` ends the Vaar's last printed line
  (`…ਪ੍ਰਭ ਕਉ ਲੋੜੇ ॥੨੧॥੧॥ ਸੁਧੁ ਕੀਚੇ`). The heading `ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ` is a separate centred line,
  with `ੴ ਸਤਿਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਗੁਰ ਪ੍ਰਸਾਦਿ ॥`. **Verified fact**
- **How it differs from Ang 524:**
  - the rubric is `ਸੁਧੁ ਕੀਚੇ`, not `ਸੁਧੁ`;
  - `ਭਗਤਾਂ` carries a bindi, where Ang 524 has `ਭਗਤਾ`;
  - the Vaar closes ॥੨੧॥੧॥, against ॥੨੧॥੧॥੨॥ at Ang 524.

  **Verified fact**
- **The commentary.** Both commentaries render `ਸੁਧੁ ਕੀਚੇ` as "to be corrected" ("ਸੁੱਧ ਕਰ ਲੈਣਾ"). Sahib
  Singh notes that in the Kartarpur Bir the words stand outside the margin and have no connection with
  the Bani, and that `ਸੁਧੁ ਕੀਚੇ` occurs only with this Vaar. **His statement about the Kartarpur Bir is
  his testimony; it is Unverified here.**
- **ShabadOS** keeps `ਸੁਧੁ ਕੀਚੇ` on the Vaar's last line under Guru Arjan Dev Ji. It files the heading
  (`ALC`) under Bhagat Kabir Ji and types it as a verse (Pankti).

**For the reviewer:** "Same ruling as A-11", "Separate ruling required" or "Leave unchanged". The
evidence for treating the rubric as not part of the Bani is **stronger here than at Ang 524**, because
Sahib Singh's note is specific to this Vaar.

---

## Engineering recommendations: NOT rulings (2026-10-28)

**These are not rulings and they record no decision.** They are the audit engineer's reading of the
evidence above, written down so that the reviewer can see a reasoned starting point and argue with it.
They were made at the owner's request after the PR #19 CI run (`AUDIT-TRAIL.md`, 2026-10-28). Nothing
in any ledger changes because of them. A ruling exists only when Kanwaljit Singh gives one himself, in
his own words, signed with his own key (`SIGN-OFF.md`).

**How to read them.** The print is the primary evidence, but it is evidence, not authority. It settles
what is printed and where (layout, line breaks, numbering, headings). It does **not** settle authorship
of an unsigned line, composition boundaries or section naming. Those are editorial judgements, and the
recommendations below say so. "Confidence" is the engineer's confidence that the recommendation matches
the weight of the evidence read. It is not a probability of scholarly approval.

| Item | Recommendation (engineering, not a ruling) | Confidence | Strongest alternative |
|---|---|---|---|
| A-07, Q-author (line 53935) | **Approve** `surdas-line`: credit Bhagat Surdas Ji. | Moderate–high | Unattributed (the print names no one). |
| A-07, Q-composition | **No change in this release.** Keep the current grouping and open it as its own item if the reviewer prefers (a). | Low | (a) its own composition. |
| A-08, split | **Approve** both entries: three sections. | High | none supported by any source read |
| A-08, names | The **short names**, as the ledger has them. | Moderate | The printed headings. |
| A-10 | **Approve** all three entries. Fix the saved-link consequence (C-1) before any release that carries it. | High (four shabads); moderate (heading) | Keep one composition and record the four shabads another way (no mechanism exists today). |
| A-11 / Ang 524 | **Approve** `bhagat-run-heading-ang524` (Bhagat Kabir Ji) for consistency, **and** open the `ਸੁਧੁ` segmentation question (d) as its own item. | Low–moderate | (b) no author for the heading. |
| Ang 323 | **Same ruling as A-11.** | Moderate | Separate ruling. |

### A-07: reasons

- **Author.** Every source read that names an author for line 53935 names Surdas: EoS IV p. 288, Sahib
  Singh's note, Faridkot's gloss and ShabadOS. No source read supports Bhagat Namdev Ji, the 1.2.0 tag;
  that tag is a pipeline carry-over, and is a Verified fact of the dataset, not of any source. The
  print's own evidence (a separate printed line, and the empty slot in the running count ੬ → ੮) agrees
  with the line standing apart from Parmanand's shabad.
- **Why not "high".** The commentaries were read only as transcribed in ShabadOS, which shares a lineage
  with BaniDB, so this is one source family plus the EoS, not several independent witnesses (P-2, P-3).
  A printed Darpan or Faridkot would raise the confidence.
- **Composition.** Option (a) matches the print and the count best, but the dataset's rule that every
  composition opens with a heading would have to bend. Option (c) has commentary support but is printed
  against. This needs a scholar's judgement and a design change, so it is recommended as a separate item,
  not as part of this release.

### A-08: reasons

- **Split.** The boundaries are printed facts: each collection has its own centred heading, its own `ੴ`
  and its own numbering. ShabadOS matches line for line (24 / 494 / 297), and EoS IV p. 240 lists them
  as separate divisions. No source read supports one section.
- **Names.** The neighbouring post-raag sections drop the author designation from their printed
  headings: `ਸਲੋਕ ਸਹਸਕ੍ਰਿਤੀ` (printed with `ਮਹਲਾ ੧`), and `ਫੁਨਹੇ` and `ਚਉਬੋਲੇ` (each printed with `ਮਹਲਾ ੫`);
  verified in the DB, 2026-10-28. Dropping `ਜੀਉ ਕੇ` / `ਕੇ` is the closest parallel, not an identical
  rule, because those words are possessives, not a Mahalla. The printed forms are equally defensible.
  Whichever is chosen, iOS `GranthNames` must match it (C-2).

### A-10: reasons

- **Four shabads.** The print numbers them as one running series and each is signed. Every source read
  treats them as four. This is the best-supported conclusion in the pack.
- **Heading.** The print runs the labels on, so layout cannot decide it, and ShabadOS is inconsistent.
  The dataset can represent four compositions only by making each label its composition's heading, so
  approving the split means approving that. Confidence is therefore lower for the heading question than
  for the four-shabad question.
- **Before release.** A saved Sain, Pipa or Dhanna line would reopen Trilochan's shabad (C-1). Line
  50285 (`ਨਾਮਦੇਵ ॥` inside Ravidas's composition 4426) is the same defect and needs its own entry.

### A-11 / Ang 524 and Ang 323: reasons

- **The question exists only because of the join.** In the print, `ਸੁਧੁ` (Ang 524) and `ਸੁਧੁ ਕੀਚੇ`
  (Ang 323) end the Vaar's last printed line, and the heading is a separate centred line. The corpus
  joins them into one record. Splitting the record would change the `gurmukhi` field and therefore needs
  its own logged scripture-record entry and a scholar's review. It is not proposed here.
- **Why Kabir, for now.** All 11 other Bhagat-run headings (13 in all; 14 with Suhi line 33831) carry their run's first Bhagat, and
  ShabadOS files both heading lines under Kabir. Approving makes the dataset consistent with its own
  convention, which is what readers and the apps' "voices" filters rely on. It does not claim that Kabir
  wrote the heading.
- **Why the confidence is low.** The heading names the Bhagats collectively. Option (b), no author, is
  the more literal reading, and Sahib Singh's note that these rubrics stand outside the Kartarpur Bir's
  margin supports treating the rubric as no part of the Bani. If the reviewer prefers (b), it should be
  applied to all 13 (or 14) headings together, not to one.
- **Ang 323.** Same structure, same heading type, so the same ruling keeps the dataset consistent. The
  evidence that the rubric is not Bani is stronger here, because Sahib Singh's note is specific to this
  Vaar. Approving it would move the entry from `proposed` to `approved` and requires the gated rebuild.

**Unresolved after these recommendations:** every item. Each still needs the reviewer's signed ruling.
