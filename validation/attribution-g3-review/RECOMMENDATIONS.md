# G3 attribution fixes: editorial recommendations for the reviewer

**Status: recommendations only. Nothing here is a ruling.** This page sits beside the held pack
(`README.md` in this folder; pull request #17). For each of the four decisions it collects the
scholarly evidence and gives an editorial recommendation. The G3 reviewer (a Granthi or Gurbani scholar)
makes every decision. They do it by ticking the boxes in the pull request that adds this page, or by
replying to the review email with the item numbers.

- No box in `README.md` is ticked.
- No ledger entry changes, and no `g3` field is filled in.
- Recorded on 2026-10-27 · Algorythmos · Gurbani Soul editorial.

> **Corrections, 28 October 2026.** The audit in sggs-data #19 (`AUDIT-REPORT.md` §2.2) found errors in
> the evidence on this page. Each was re-checked against the dataset and ShabadOS 4.8.7 and corrected
> below. **None of the four recommended rulings changes.** The earlier wording is kept in this page's
> git history.
>
> 1. **A-07.** Not every source agrees that the shabad after line 53935 is Guru Arjan Dev Ji's. ShabadOS
>    files it under Bhagat Surdas Ji, and the Faridkot gloss of its last line names Surdas as the speaker.
> 2. **A-07.** `5FC` is ShabadOS's id for the *shabad*, not a line type. The line itself is a Pankti.
> 3. **A-08.** Farid's saloks end on Ang 1384 (line 59087), not Ang 1385.
> 4. **A-08.** Faridkot names the four Bhagats of the Chaubole as their *speakers*, not as the people
>    they are addressed to.
> 5. **A-08.** Sahib Singh's running summary of Kabir's saloks is in his note on line 58298, not 58297.
> 6. **A-10.** The dataset does not already treat `ਨਾਮਦੇਵ ॥` as a heading. Line 50285 has the same defect
>    that A-10 fixes.
> 7. **A-11.** There are 13 Bhagat-run headings, not 12; the count reads "11 of 13".
> 8. **Sources.** In ShabadOS, Bhai Vir Singh and Dr. Rattan Singh Jaggi are not commentaries on the
>    Granth. They are removed from the source list.
> 9. **Confidence.** A-07 and A-11 are lowered to Medium (see the note under the table).

## How the evidence was gathered

- **The text.** Each quoted line was read from `db/sggs.sqlite` on this branch (`fix/attribution-g3-held`,
  the held 1.3.0 build), by line id. None was typed by hand.
- **The commentaries.** These were read from the ShabadOS 4.8.7 database. It is the same release that
  `pipeline/shabados.SHA256SUMS` pins, and its sha256 `d8e07134…` was verified. That database carries,
  line by line:
  - Prof. Sahib Singh, *Sri Guru Granth Sahib Darpan*: the arth and his own notes (*ਨੋਟ*);
  - the *Faridkot Teeka*;
  - Bhai Manmohan Singh (English and Punjabi), Dr. Sant Singh Khalsa and SikhNet;
  - the BaniDB / SikhiToTheMax shabad id.

  These are the six translation sources ShabadOS carries for the Granth. All the commentary on this page
  therefore comes through one transcription.

  The corpus lines were aligned Ang by Ang with the repository's own aligner
  (`pipeline/crosscheck_authors.py`), and the Gurmukhi was converted from GurbaniAkhar with `gurmukhiutils`.
- Short excerpts from the commentaries are quoted verbatim, each followed by an English gist. A gist is
  editorial and is labelled as such.
- **No web page is cited that was not read.** The online editions of the Darpan, the Mahan Kosh and the
  *Encyclopaedia of Sikhism* could not be opened when this page was prepared. They are not quoted here.

| # | Item | Recommendation | Confidence |
|---|---|---|---|
| 1 | A-07 · Ang 1253, line 53935 | **Approve.** Credit Bhagat Surdas Ji, author only. Record a follow-up on composition (a). | Medium |
| 2 | A-08 · Angs 1363–1384 | **Approve.** Split into three sections, as in this pull request. | High |
| 3 | A-10 · Ang 695 | **Approve.** The three labels become headings, giving four compositions. | High |
| 4 | A-11 · Ang 524, line 23470 | **Approve.** Credit Bhagat Kabir Ji. **Line 14771: the same ruling.** | Medium |

*Confidence.* **High** means the printed text decides the item: its headings, ੴ and numbering. **Medium**
means the item rests on commentary, which reaches this page through one transcription (ShabadOS), and
where the sources differ on a neighbouring point.

---

## 1 · A-07 · The single line on Ang 1253

> ਛਾਡਿ ਮਨ ਹਰਿ ਬਿਮੁਖਨ ਕੋ ਸੰਗੁ ॥ *(line 53935)*
> ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ ॥ *(line 53936)*
> ਸੂਰਦਾਸ ਮਨੁ ਪ੍ਰਭਿ ਹਥਿ ਲੀਨੋ ਦੀਨੋ ਇਹੁ ਪਰਲੋਕ ॥੨॥੧॥੮॥ *(line 53943)*
>
> — Sri Guru Granth Sahib Ji · Ang 1253

**Evidence.**

- **Prof. Sahib Singh, Darpan, note on line 53935.** He observes that a Bhagat's name is normally
  written before their bani. This line has neither a name nor a whole shabad. He answers the question
  from the heading of the next shabad:

  > ਇਸ ਦਾ ਉੱਤਰ ਅਗਲੇ ਸ਼ਬਦ ਦੇ ਸ਼ੁਰੂ ਵਿਚ ਲਿਖੇ ਸਿਰ-ਲੇਖ ਤੋਂ ਮਿਲਦਾ ਹੈ; ਭਾਵ, ਇਹ ਇਕ ਤੁਕ 'ਸੂਰਦਾਸ' ਜੀ ਦੀ ਹੈ।

  *Gist:* the heading of the next shabad answers this. The line is Surdas's.
- **Prof. Sahib Singh, Darpan, note on line 53943.** This bears on the printed count and on question 2:

  > ਭਾਵੇਂ ਭਗਤ ਸੂਰਦਾਸ ਜੀ ਦੀ ਇਕੋ ਹੀ ਤੁਕ ਦਰਜ ਕੀਤੀ ਹੈ, ਪਰ ਗਿਣਤੀ ਵਿਚ ਉਸ ਨੂੰ ਸਾਰੇ ਸ਼ਬਦ ਵਾਂਗ ਗਿਣਿਆ ਹੈ; ਤਾਹੀਏਂ ਹੁਣ ਤਕ ਦੀ ਗਿਣਤੀ ੮ ਬਣਦੀ ਹੈ।

  *Gist:* only one line of Surdas's is recorded, but the count treats it as a whole shabad, which is
  why the running count reaches ੮. The same note says that the following shabad is Guru Arjan Dev Ji's own:

  > ਇਹ ਸ਼ਬਦ ਸਤਿਗੁਰੂ ਅਰਜਨ ਸਾਹਿਬ ਜੀ ਦਾ ਆਪਣਾ ਹੈ। ਸੂਰਦਾਸ ਦਾ ਨਹੀਂ।

  It also says the shabad was uttered in relation to Surdas's line. It records that some scholars hold
  there were two Surdases.
- ***Faridkot Teeka*, on line 53935:**

  > ਤੌ ਇਹ ਸੂਰਦਾਸ ਜੀ ਕਾ ਸਾਰਾ ਸਬਦ ਭਾਈ ਬੰਨੋ ਦੀ ਬੀੜ ਮੇਂ ਹੈ।

  *Gist:* Surdas's whole shabad is in Bhai Banno's Bir. Its preface (in its note on line 53934) explains
  that the Guru composed the next shabad himself and set Surdas's name in it.
- **ShabadOS 4.8.7.** It credits the line to Bhagat Surdas Ji, as a Pankti (line `B8PD`, in its
  shabad `5FC`). It shares BaniDB id 4531 with Parmanand's shabad.

**Where sources differ.** None of the sources read credits the line to Bhagat Namdev Ji. On the
*composition* (question 2), Sahib Singh's count note supports option (a): the line counts as a shabad
of its own. BaniDB's grouping, and the dataset's placement today, support (b). **The sources differ on
question 3** (whose is the following shabad, lines 53936–53943). Sahib Singh's note, and the Faridkot
preface on line 53934, give it to Guru Arjan Dev Ji, as its `ਮਹਲਾ ੫` heading does. ShabadOS files the
same shabad (STTM 4532) under Bhagat Surdas Ji, and Faridkot's gloss of its last line (53943) opens
`ਸੂਰਦਾਸ ਜੀ ਕਹਿਤੇ ਹੈਂ` ("Surdas Ji says"). This does not touch the ruling on line 53935 itself.

**Recommended ruling.** **Approve:** Bhagat Surdas Ji, author only, as in this pull request. Then
record a follow-up for composition (a), its own composition, citing Sahib Singh's count note. That
follow-up needs the new ledger kind that the pack describes. It is a separate decision and need not
hold up this one.

---

## 2 · A-08 · Salok Bhagat Kabir Ji and Salok Sheikh Farid Ji

> ਚਉਬੋਲੇ ਮਹਲਾ ੫ *(line 58273, Ang 1363)*
> ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ *(line 58297, Ang 1364)*
> ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ *(line 58791, Ang 1377)*
> ਸਵਯੇ ਸ੍ਰੀ ਮੁਖਬਾਕ੍ਯ੍ਯ ਮਹਲਾ ੫ ॥ *(line 59089, Ang 1385: the next bani, shown for the boundary)*
>
> — Sri Guru Granth Sahib Ji · Angs 1363–1385

**Evidence.**

- **The print.** Each collection opens with its own heading and its own ੴ, and numbers its own
  saloks. Kabir's run to ॥੨੪੩॥ (line 58790), Farid's to ॥੧੩੦॥ (line 59087, Ang 1384).
- **Prof. Sahib Singh, Darpan.** He treats the Chaubole as a bani of their own
  ("ਗੁਰੂ ਅਰਜਨਦੇਵ ਜੀ ਦੀ ਬਾਣੀ 'ਚਉਬੋਲੇ'", on line 58273). He opens Kabir's saloks with their own
  heading ("ਭਗਤ ਕਬੀਰ ਜੀ ਦੇ ਸਲੋਕ", on line 58297) and give them their own running summary
  (*ਲੜੀ-ਵਾਰ ਭਾਵ*, in his note on line 58298).
- ***Faridkot Teeka*, on line 58296.** Its note ends the Chaubole with the eleventh stanza. It names the
  four Bhagats as their speakers: the Guru uttered "ਇਨ ਚਾਰੋਂ ਭਗਤੋਂ ਕੇ ਬਚਨ" (the words of these four
  Bhagats: ਸੰਮਨ · ਮੂਸਨ · ਜਮਾਲ · ਪਤੰਗ) in the Chaubola metre. The Chaubole therefore close on Ang 1364.
- **ShabadOS 4.8.7** has three sections: *Chaubolas Fifth Mehl*, *Salok Kabeer Jee* and *Salok Fareed
  Jee*, with the same boundaries as this pull request.

**Where sources differ.** None found on the boundaries. The section names are a presentation choice:
the short canonical form (`ਸਲੋਕ ਭਗਤ ਕਬੀਰ`, `ਸਲੋਕ ਸੇਖ ਫਰੀਦ`) or the full printed heading.

**Recommended ruling.** **Approve:** split as in this pull request, with the short canonical names, to
match `ਚਉਬੋਲੇ`. The Gurus' saloks inside each collection stay in that collection, as printed.

---

## 3 · A-10 · Four shabads on Ang 695

> ਬਦਤਿ ਤ੍ਰਿਲੋਚਨ ਰਾਮ ਜੀ ॥੬॥੧॥ *(line 30080)*
> ਸ੍ਰੀ ਸੈਣੁ ॥ *(line 30081)* … ਸੈਨੁ ਭਣੈ ਭਜੁ ਪਰਮਾਨੰਦੇ ॥੪॥੨॥ *(line 30091)*
> ਪੀਪਾ ॥ *(line 30092)* … ਪੀਪਾ ਪ੍ਰਣਵੈ ਪਰਮ ਤਤੁ ਹੈ ਸਤਿਗੁਰੁ ਹੋਇ ਲਖਾਵੈ ॥੨॥੩॥ *(line 30098)*
> ਧੰਨਾ ॥ *(line 30099)* … ਜਨੁ ਧੰਨਾ ਲੇਵੈ ਮੰਗੀ ॥੨॥੪॥ *(line 30109)*
>
> — Sri Guru Granth Sahib Ji · Ang 695

**Evidence.**

- **The print.** Each shabad closes with its own number in one running series (੧ to ੪) and carries its
  own pen-name (ਤ੍ਰਿਲੋਚਨ · ਸੈਨੁ · ਪੀਪਾ · ਧੰਨਾ).
- **Prof. Sahib Singh, Darpan.** He writes a separate closing note for each shabad. On Pipa's, for
  example:

  > ਇਸ ਸ਼ਬਦ ਵਿਚ ਭਗਤ ਪੀਪਾ ਜੀ ਮੂਰਤੀ-ਪੂਜਾ ਦਾ ਖੰਡਨ ਕਰਦੇ ਹਨ

  *Gist:* in this shabad Bhagat Pipa Ji refutes idol-worship. He comments on Sain's and Dhanna's
  shabads in the same separate way.
- ***Faridkot Teeka*** opens each new shabad with its own introduction. Examples are
  "ਸ੍ਰੀ ਸੈਣ ਭਗਤ ਜੀ ਸ੍ਰੀ ਅਕਾਲ ਪੁਰਖ ਜੀ ਕੇ ਸਨਮੁਖ ਆਰਤੀ ਕਰ ਕੇ ਬੇਨਤੀ ਕਰਤੇ ਹੈਂ" (on line 30080) and the
  matching openings for Pipa (line 30091) and Dhanna (line 30098).
- **ShabadOS 4.8.7** has four shabads: BaniDB 2639 Trilochan, 2640 Sain, 2641 Pipa and 2642 Dhanna. It
  types `ਸ੍ਰੀ ਸੈਣੁ ॥` and `ਧੰਨਾ ॥` as headings, and `ਪੀਪਾ ॥` as a verse.

**Where sources differ.** Only on how ShabadOS types the label `ਪੀਪਾ ॥`. Every source read treats the
four as four shabads.

**Recommended ruling.** **Approve:** fix as in this pull request. Each label becomes the heading of its
own composition (5381, 5382, 5383).

**A related case, outside this pull request.** The same defect exists elsewhere. Line 50285 `ਨਾਮਦੇਵ ॥`
(Ang 1167) is a bare label that the dataset keeps as an ordinary line inside Bhagat Ravidas Ji's
composition 4426. Line 47529 `ਕਬੀਰੁ ॥` (Ang 1106) may be another. These are follow-ups for engineering
and the reviewer, not part of A-10.

---

## 4 · A-11 · `ਸੁਧੁ` and the Bhagat-run heading (Ang 524, and its twin on Ang 323)

> ਗੁਰ ਪ੍ਰਸਾਦਿ ਨਾਨਕ ਸਚਿ ਸਮਾਇਆ ॥੨੧॥੧॥੨॥ *(line 23469)*
> ਸੁਧੁ ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ *(line 23470)*
>
> — Sri Guru Granth Sahib Ji · Ang 524

> ਨਾਨਕ ਮਨਿ ਤਨਿ ਚਾਉ ਏਹੁ ਨਿਤ ਪ੍ਰਭ ਕਉ ਲੋੜੇ ॥੨੧॥੧॥ *(line 14770)*
> ਸੁਧੁ ਕੀਚੇ ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ *(line 14771)*
>
> — Sri Guru Granth Sahib Ji · Ang 323

**Evidence.**

- ***Faridkot Teeka*.** It reads `ਸੁਧੁ` as the close of the Vaar. Its explanation of line 23469 ends
  "॥੨੧॥੧॥੨॥ਸੁਧੁ".
- **ShabadOS 4.8.7.** It ends the Vaar's last line with `ਸੁਧੁ` (Ang 524) and with `ਸੁਧੁ ਕੀਚੇ`
  (Ang 323), both under Guru Arjan Dev Ji. It files the remaining heading, `ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ ॥`
  or `ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ ॥`, under **Bhagat Kabir Ji** (BaniDB 2006 and 1285).
- **Prof. Sahib Singh, Darpan, note on line 23469.** It explains the closing numbers of Gujri ki Vaar
  (21 pauris; this Vaar; the two Vaars of the raag). So the Vaar is complete at ॥੨੧॥੧॥੨॥, and the
  heading that follows opens the Bhagat Bani.
- **The dataset.** There are 13 Bhagat-run headings (14 if the Suhi heading, line 33831, is counted). In
  1.2.0, 11 of the 13 already carried the run's first Bhagat. Lines 23470 and 14771 were the two
  exceptions.

**Where sources differ.** None on substance. `ਸੁਧੁ` belongs with the Vaar, and the rest of the line opens
the Bhagat Bani. The difficulty is that the corpus holds `ਸੁਧੁ` and the heading as one line, so one
`author` has to stand for both. The audit in #19 reports, from the page images of Angs 323 and 524, that
in the print `ਸੁਧੁ` ends the Vaar's last line and the heading is a separate line. This page has not
re-checked those images.

**Recommended ruling.** **Approve (a):** credit line 23470 to Bhagat Kabir Ji, as in this pull
request. Then the heading follows the other 11 and the sources. **Line 14771 (Ang 323): the same
ruling as line 23470**, so the two twins are treated alike. A note on the line can record that its
first word closes the Vaar.

---

## For the reviewer

Each item has three options in the pull request: **Approve as recommended**, **Change** (write what you
want) or **Reject** (leave the dataset as it is). After your ruling, an engineer records your initials
and the date in each entry's `g3` field, as `README.md` describes under *After your ruling*. Nothing
merges before that.
