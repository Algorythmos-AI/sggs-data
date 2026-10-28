# Evidence ledger

Each row follows one claim through: the claim, its source, the exact location, how it was checked, what
it means for the data, and the conclusion. The **label** column uses the categories defined in
`DECISIONS.md`.

**Sources and versions**

| Key | Source | Version and identity | How it was read |
|---|---|---|---|
| PRINT | The source PDF of record, *Siri Guru Granth Sahib in Gurmukhi with Index* (1,483 pages) | sha256 `294a0b99…d5175` (= `validation/reconcile-attestation.json`). Edition: typeset, run-on; the edition statement was not established. | Page images rendered with PyMuPDF and read; the PDF's own text lines read (`page.get_text('dict')`). PDF page *n* is 1-based; the Ang number printed at the head of each page was read. |
| SOS | ShabadOS database | 4.8.7, sha256 `d8e071347bd5…74c2` (= `pipeline/shabados.SHA256SUMS`) | Direct SQL (`audit-tools/extract_shabados.py`) |
| BDB | BaniDB / SikhiToTheMax shabad ids | As carried in SOS `shabads.sttm_id` | Through SOS only. **Not independent of SOS for grouping**: SOS carries BDB's ids and splits 13 of them (S9). |
| SS | Prof. Sahib Singh, *Sri Guru Granth Sahib Darpan* | **As transcribed in SOS 4.8.7** (`translations`, source 6; `additional_information.note`). The edition is not stated, and 128 notes are cut off at 1,000 characters. | SQL. No printed Darpan was consulted. |
| FK | *Faridkot Teeka* | **As transcribed in SOS 4.8.7** (source 5). Introductions sit after `☬` on the line **before** the text they introduce. | SQL. No printed Teeka was consulted. |
| EoS | *The Encyclopaedia of Sikhism*, ed. Harbans Singh, Punjabi University, Patiala | Per volume, read from each volume's own imprint page: see § EoS | archive.org page images |
| DS | This dataset | 1.2.0 `ff5e5de7…` (`main` `c36e317`); 1.3.0 `003cae57…` (`aeac8fd`) | SQL |

## The print (read by this audit as images, PDF text lines cross-checked)

| # | Claim | Location | Check | Consequence | Label |
|---|---|---|---|---|---|
| P1 | `pdf_page` is 1-based and matches the printed Ang | PDF pages 748, 1306, 577, 376, 1417, 1430 → Angs 695, 1253, 524, 323, 1364, 1377 | Ang numeral read at the head of each image | The corpus page mapping is reliable for these items | Verified fact |
| P2 | The edition runs text on: labels and `ਰਹਾਉ ॥` sit inline, and only principal headings are centred | PDF 748, 1306, 577 | Images | The layout cannot settle heading versus verse for a run-on label (A-10) | Verified fact |
| P3 | 53935 is printed on its own line, between ॥੩॥੧॥੬॥ and the centred `ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ ॥` | PDF 1306 | Image | Weighs against composition reading (b); does not choose between (a) and (c) | Verified fact |
| P4 | The Ang 1253 count runs ੬ (53934) → ੮ (53943) | PDF 1306; DS `markers` | Image + SQL | One shabad-number falls between | Verified fact |
| P5 | The Chaubole close ॥੧੧॥, then a centred `ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ` + `ੴ` | PDF 1417 | Image | A-08 boundary | Verified fact |
| P6 | Kabir's saloks close ॥੨੪੩॥, then a centred `ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ` + `ੴ` | PDF 1430 | Image | A-08 boundary | Verified fact |
| P7 | Farid's saloks end on Ang 1384 (line 59087); line 59088 on Ang 1385 opens the Swaiyye | DS `ang` of 59087 and 59088 | SQL | PR #17's "1363–1385" is off by one Ang | Verified fact |
| P8 | Ang 695: closes ॥੬॥੧॥ ॥੪॥੨॥ ॥੨॥੩॥ ॥੨॥੪॥; three labels run on inline | PDF 748 | Image | Four shabads in one series. The labels are not set as headings | Verified fact |
| P9 | `ਸੁਧੁ` ends the Vaar's last printed line; `ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ` is a separate centred line | PDF 577; text line `…॥੨੧॥੧॥੨॥ ਸੁਧੁ` | Image + PDF text lines | The corpus joins them in line 23470 (A-11 reading d) | Verified fact |
| P10 | `ਸੁਧੁ ਕੀਚੇ` ends the Vaar's last printed line; the heading is separate | PDF 376; text line `…॥੨੧॥੧॥ ਸੁਧੁ ਕੀਚੇ` | Image + PDF text lines | Same join, in line 14771 | Verified fact |
| P11 | The same join on Angs 517 and 654 | PDF 570, 707 | **PDF text lines only; the images were not read** | Lines 23136 and 28417 begin with `ਸੁਧੁ` too; 28417 is credited to Kabir and 23136 to Guru Arjan Dev Ji | Verified fact (from the text layer) |
| P12 | Every other `ਸੁਧੁ` rubric is its own record | DS: `gurmukhi = 'ਸੁਧੁ'` / `'ਸੁਧੁ ॥'` | SQL | The four joined lines are exceptions | Verified fact |

## ShabadOS 4.8.7 and BaniDB

| # | Claim | Location | Check | Consequence | Label |
|---|---|---|---|---|---|
| S1 | Line 53935 = SOS line `B8PD`, in shabad `5FC` (writer Bhagat Surdas Ji, STTM 4531), type 4 Pankti | SOS `lines`, `shabads`, `writers` | SQL | A-07 authorship | Verified fact (about SOS) |
| S2 | Parmanand's shabad is `D1T`, also STTM 4531 | SOS | SQL | BDB groups 53935 with Parmanand; SOS splits it out | Verified fact |
| S3 | Lines 53936–53943 = shabad `FHM`, writer **Bhagat Surdas Ji**, STTM 4532 | SOS | SQL | Disproves "all sources agree" (PR #18) | Verified fact |
| S4 | `5FC` and `6AM` are shabad ids; the line types are 1–4 | SOS `line_types` | SQL | Corrects PR #18 | Verified fact |
| S5 | Sections: Chaubolas 58273–58296, Salok Kabeer Jee 58297–58790, Salok Fareed Jee 58791–59087 | SOS per-line section | SQL (agent B; spot-checked) | Same as 1.3.0, line for line | Verified fact |
| S6 | Ang 695: shabads `R0X`/`LB4`/`E2C`/`37J` = STTM 2639–2642. Label types: `ਸ੍ਰੀ ਸੈਣੁ ॥` Sirlekh, `ਪੀਪਾ ॥` Pankti, `ਧੰਨਾ ॥` Sirlekh | SOS | SQL | Four shabads; label types inconsistent | Verified fact |
| S7 | `ਸੁਧੁ` (524) and `ਸੁਧੁ ਕੀਚੇ` (323) sit on the Vaar's last line, under Guru Arjan Dev Ji. The headings are `6AM`/2006 and `ALC`/1285 under Bhagat Kabir Ji, typed Pankti | SOS | SQL | Agrees with the print's placement of the rubric | Verified fact |
| S8 | SOS carries six translation/commentary sources for the Granth; Bhai Vir Singh and Jaggi are not among them | SOS `translation_sources` | SQL | Corrects PR #18's source list | Verified fact |
| S9 | 13 STTM ids are each split by SOS across two or more shabads; A-07 (4531) is one of them. Checked in one direction only: 16 STTM ids in 1–5540 are absent from SOS's Granth shabads (171, 470, 755, 1668, 1671, 1675, 2032, 2039, 2071, 3226, 3372, 3444, 3518, 3635, 4762, 4861), and these were not examined (they may be SOS merges or BaniDB gaps) | SOS `shabads.sttm_id` | SQL | SOS carries BDB's ids, so for grouping the two are treated as one source family | Verified fact for the 13 splits; **Interpretation** that they are otherwise identical |

## Commentary (as transcribed in ShabadOS 4.8.7)

Each quote below was copied from the SOS field named and compared by script. It matches the field's text
up to canonical equivalence: SOS stores ਸ਼ as U+0A36, while PR #18 had U+0A38+U+0A3C.

| # | Claim | Location (corpus line → SOS line, field) | Quote (≤ 25 words) | Consequence | Label |
|---|---|---|---|---|---|
| C1 | SS: line 53935 is Surdas's | 53935 → `B8PD`, SS note | "ਇਸ ਦਾ ਉੱਤਰ ਅਗਲੇ ਸ਼ਬਦ ਦੇ ਸ਼ੁਰੂ ਵਿਚ ਲਿਖੇ ਸਿਰ-ਲੇਖ ਤੋਂ ਮਿਲਦਾ ਹੈ; ਭਾਵ, ਇਹ ਇਕ ਤੁਕ 'ਸੂਰਦਾਸ' ਜੀ ਦੀ ਹੈ।" | Supports Surdas (A-07 author) | Verified fact (that SS says so, in this transcription) |
| C2 | SS: the line counts as a whole shabad, hence ੮ | 53943 → `8EJX`, SS note | "ਗਿਣਤੀ ਵਿਚ ਉਸ ਨੂੰ ਸਾਰੇ ਸ਼ਬਦ ਵਾਂਗ ਗਿਣਿਆ ਹੈ; ਤਾਹੀਏਂ ਹੁਣ ਤਕ ਦੀ ਗਿਣਤੀ ੮ ਬਣਦੀ ਹੈ।" | Supports composition reading (a) | Verified fact |
| C3 | SS: the following shabad is Guru Arjan Dev Ji's own | 53943 → `8EJX`, SS note | "ਇਹ ਸ਼ਬਦ ਸਤਿਗੁਰੂ ਅਰਜਨ ਸਾਹਿਬ ਜੀ ਦਾ ਆਪਣਾ ਹੈ। ਸੂਰਦਾਸ ਦਾ ਨਹੀਂ।" | One side of the 53936–53943 dispute | Verified fact; the note is cut off at 1,000 characters |
| C4 | SS: that shabad was composed to expound the line above | 53935 → `B8PD`, SS note | "ਉੱਪਰ-ਦਿੱਤੀ ਹੋਈ ਇੱਕ ਤੁਕ ਦੀ ਵਿਆਖਿਆ ਕਰਨ ਲਈ" | Supports composition reading (c). **Omitted by PR #18** | Verified fact |
| C5 | FK: Surdas's whole shabad is in Bhai Banno's Bir | 53935 → `B8PD`, FK, after `☬` | "ਤੌ ਇਹ ਸੂਰਦਾਸ ਜੀ ਕਾ ਸਾਰਾ ਸਬਦ ਭਾਈ ਬੰਨੋ ਦੀ ਬੀੜ ਮੇਂ ਹੈ।" | Supports Surdas; FK's claim about Bhai Banno's Bir is **Unverified** | Verified fact (that FK says so) |
| C6 | FK's gloss of 53943 opens with Surdas as the speaker | 53943 → `8EJX`, FK | "ਸੂਰਦਾਸ ਜੀ ਕਹਿਤੇ ਹੈਂ" | Conflicts with FK's own preface (C7) | Verified fact |
| C7 | FK's preface: Surdas uttered only the one line "out of love" and went into samadhi. The Guru then composed the shabad himself and set Surdas's name in it | 53934 → `HERV`, FK, after `☬` | "ਪੁਨਾ ਗੁਰੂ ਜੀਨੇ ਆਪ ਸਬਦ ਉਚਾਰ ਕਰ ਅੰਕ ਕੋ ਸੂਰਦਾਸ ਦਾ ਨਾਮੁ ਲਿਖ ਕਰ ਸਮਾਪਤ ਕਰ" | Supports Surdas for 53935 and Guru Arjan Dev Ji for 53936–53943. The samadhi narrative is FK's own and **Unverified** | Verified fact (that FK says so) |
| C8 | SS glosses 58273 as Guru Arjan Dev Ji's bani "ਚਉਬੋਲੇ" | 58273 → `CLQ7`, SS translation | "ਗੁਰੂ ਅਰਜਨਦੇਵ ਜੀ ਦੀ ਬਾਣੀ 'ਚਉਬੋਲੇ'" | A gloss of the heading only: thin support for a section | Verified fact |
| C9 | FK: the four named are the Chaubole's speakers | 58296 → `8KWU`, FK, after `☬` | "ਸੰਮਨ ੧, ਮੂਸਨ ੨, ਜਮਾਲ ੩, ਪਤੰਗ ੪, ਇਨ ਚਾਰੋਂ ਭਗਤੋਂ ਕੇ ਬਚਨ ਕੀਏ ਹੂਏ ਸ੍ਰੀ ਗੁਰੂ ਜੀ ਨੇ ਚਉਬੋਲੇ ਛੰਦ ਮੇਂ" | Corrects PR #18 ("addressed to") | Verified fact |
| C10 | FK: "or Bhagat Patang said this salok" | 58296 → `8KWU`, FK | "ਵਾ ਏਹ ਸਲੋਕ ਪਤੰਗ ਭਗਤ ਨੇ ਕਹਾ ਹੈ" | An authorship remark outside A-08, recorded only | Verified fact |
| C11 | SS on Pipa's shabad | 30098 → `DP2N`, SS note | "ਇਸ ਸ਼ਬਦ ਵਿਚ ਭਗਤ ਪੀਪਾ ਜੀ ਮੂਰਤੀ-ਪੂਜਾ ਦਾ ਖੰਡਨ ਕਰਦੇ ਹਨ" | Treats it as a shabad of its own | Verified fact |
| C12 | FK numbers Sain's and Pipa's shabads ੧ each (per author) | 30091, 30098 → FK | (numbering only) | Per-author numbering, unlike the print's running ੨ and ੩ | Verified fact |
| C13 | FK: `॥੨੧॥੧॥੨॥ਸੁਧੁ` | 23469 → `D19A`, FK | "॥੨੧॥੧॥੨॥ਸੁਧੁ" | FK keeps `ਸੁਧੁ` with the Vaar | Verified fact |
| C14 | SS on Ang 323: `ਸੁਧੁ ਕੀਚੇ` = "to be corrected"; in the Kartarpur Bir the words stand outside the margin and have no connection with the Bani | 14770 → `PC8G`, SS translation + note | "ਇਸ ਦਾ ਭਾਵ ਇਹ ਹੈ ਕਿ ਇਹਨਾਂ ਲਫ਼ਜ਼ਾਂ ਦਾ 'ਬਾਣੀ' ਨਾਲ ਕੋਈ ਸੰਬੰਧ ਨਹੀਂ ਹੈ।" | Bears on A-11 / Ang 323. SS's Kartarpur statement is **Unverified** here. **Omitted by PR #18** | Verified fact (that SS says so) |
| C15 | FK on Ang 323 renders `ਸੁਧੁ ਕੀਚੇ` the same way | 14770 → `PC8G`, FK | "ਸੁ~ਧ ਕਰ ਲੇਨਾ" (`~` is a transcription artefact) | As C14 | Verified fact |

## The dataset (1.2.0 → 1.3.0)

| # | Claim | Check | Label |
|---|---|---|---|
| D1 | Scripture text (every text column of `lines`) is unchanged, byte for byte and code point for code point | `audit-tools/independent_diff.py`; `diff_scripture.py`; fingerprint `scripture_sha256`/`t0_sha256` unchanged | Verified fact |
| D2 | Every changed cell is predicted by an applied ledger entry, or is a derived column of one | `independent_diff.py` (output in `audit-tools/independent_diff.out`) | Verified fact |
| D3 | 13 Bhagat-run headings (14 with Suhi 33831); 1.2.0 has two under Guru Arjan Dev Ji (14771, 23470) | `SELECT … WHERE is_header=1 AND (gurmukhi LIKE '%ਭਗਤਾ ਕੀ%' OR gurmukhi LIKE '%ਭਗਤਾਂ ਕੀ%')` in both DBs | Verified fact |
| D4 | `ਨਾਮਦੇਵ ॥` (50285) is a verse in Ravidas's composition 4426 in both versions | SQL | Verified fact |
| D5 | Composition ids: 5381–5383 are new; 5377–5380 are the new gaps; no id is reused; 2749 = Trilochan's 17 lines | SQL (both DBs) | Verified fact |
| D6 | A rebuild from the PDF reproduces the committed 1.3.0 DB byte for byte (with `SOURCE_DATE_EPOCH` of `8bad6f5`) | `make rebuild` twice (`AUDIT-REPORT.md` § 3) | Verified fact |

## EoS

### The volumes

*The Encyclopaedia of Sikhism*, editor-in-chief Harbans Singh, Punjabi University, Patiala. Copies
are on archive.org (uploader DiscoverSikhism.com) as
`TheEncyclopediaOfSikhism-VolumeIA-d`, `-VolumeIiE-l`, `-VolumeIiiM-r` and `-VolumeIvS-z`.

**Each volume's edition differs. It was read from that volume's own imprint page, by the lead auditor,
on the image:**

| Vol. | Imprint leaf | Edition as printed | ISBN as printed | Printer |
|---|---|---|---|---|
| I (A–D) | n3 | **Fourth Edition: 2002** (also lists 1992, 1995 and 1998) | 81-7380-100-2 | Anand Sons, Delhi |
| II (E–L) | n1 | **Third Edition: 2011** | 81-7380-204-**I** as printed. The ISBN-10 check digit computes to **1**. | M/s Anand Sons, Delhi |
| III (M–R) | n2 | **Third Edition: 2011** | 81-7380-349-8 | M/s Anand Sons, Delhi |
| IV (S–Z) | n2 | **Second Edition: 2004** | 81-7380-530-X | Ram Printograph (India), New Delhi |

**The brief's "Third edition, 2011" is correct only for vols. II and III.**

- **The leaf/page mapping** is that leaf `n` is the archive.org page index.
- **The printed page** is read from the page head of each image.
- **Who read each row.** In the next table, **L** means the lead auditor read the image. **A** means the
  image was read by audit agent A only, and not re-read by the lead auditor; treat an A row as
  agent-checked.

### Entries

| # | Topic | Vol. / printed page / leaf / entry | Quote (verbatim, at most 15 words) | Read | Bears on | Label |
|---|---|---|---|---|---|---|
| E1 | Surdas's single line | IV / 288 / n305 / SŪRDĀS | "In fact, it is not a complete hymn but a single line" | L | A-07 author: Surdas | Verified fact (that EoS says so) |
| E2 | Who composed the following hymn | IV / 288 / n305 / SŪRDĀS | "He therefore composed a hymn to explain and supplement the single line of Sūrdās." ("He" = Guru Arjan, from the sentence before) | L | 53936–53943: Guru Arjan Dev Ji. Supports composition reading (c) as a relationship | Verified fact |
| E3 | The line as a refrain | IV / 288 / n305 | "It is believed to be the refrain of a complete hymn composed by Sūrdās" | L | Context: EoS reports a *belief*, which it does not source | Verified fact (that EoS reports it) |
| E4 | Which Surdas | IV / 288 / n305 | "to be differentiated from the blind poet of the same name" | L | The "two Surdases" remark (Sahib Singh) | Verified fact |
| E5 | Surdas in the Bhagat Bani entry | I / 314 / n331 / BHAGAT (BHAKTA) BĀṆĪ | "there is only one line and a hymn from Sūr Dās." | L | **Contradicts E2**: credits the hymn to Surdas | **Disputed** (EoS against EoS) |
| E6 | Dhanna's hymns | I / 314 / n331 | "Dhannā has only two hymns, one in Rāga Āsā and the other in Dhanāsarī" | L | Count only | **Disputed** with E7 |
| E7 | Dhanna's hymns | I / 567 / n584 / DHANNĀ, BHAGAT | "Totally, there are three hymns by Dhannā in the Gurū Granth Sāhib." | L | Count only. Neither E6 nor E7 speaks to Ang 695's structure | Disputed with E6 |
| E8 | Sain | I / 314 / n331 | "Saiṇu has only one hymn" | L | One shabad by Sain: consistent with A-10's separate composition. It does not name the Ang | Verified fact |
| E9 | Kabir's saloks | I / 314 / n331 | "296 of his hymns in different rāgas and 239 ślokas" | L | The print's last number is ॥੨੪੩॥. EoS's count is not the printed numbering | Verified fact (that EoS says so) |
| E10 | Divisions and their Angs | IV / 240 / n257 / SRĪ GURŪ GRANTH SĀHIB | "Salok Kabīr (1364-1377), Salok Farīd (1377-1384)" | L | **A-08: separate divisions; Farid ends on Ang 1384** | Verified fact |
| E11 | The Chaubole | II / 335 / n353 / JAMĀL, MĪĀṄ | "Gurū Arjan's composition Chaubole, addressed to four devotees" | L | **Contradicts Faridkot C9** (words *of* the four, against verses *addressed to* them). Not an A-08 boundary question | **Disputed** (EoS against FK) |
| E12 | Sain's entry | IV / 25 / n42 / SAIṆ | "whose one hymn has been included" | A | As E8 | Agent-checked |
| E13 | Pipa's entry | III / 342 / n358 / PĪPĀ | "one of whose hymns is incorporated" | A | One shabad by Pipa | Agent-checked |
| E14 | Trilochan's entry | IV / 365 / n380 / TRILOCHAN | cites "(GG,695)"; saloks "212 and 213" interposed among Kabir's | A | A-10 context; Kabir's collection (`kabir-saloks-signed-by-others`) | Agent-checked |
| E15 | Kabir's own entry | II / 403 (the page prints no number; inferred by sequence) / n417 | "237 ślokas" | A | Disputed with E9 (239) | Agent-checked; Disputed |
| E16 | Farid's own entry | II / 13 / n27 | "four śabdas (hymns) and 112 ślokas" | A | Count | Agent-checked |
| E17 | Slokas entry | IV / 220 / n237 | "120 ślokas covering pages 1377 to 1384" | A | Ang 1384 end, as E10; the count is disputed with E16 | Agent-checked; Disputed |
| E18 | Bhagat-run headings | I / 313 / n330 | "Bhagtāṅ kī Bāṇī appears… for the first time on page 323" | A | Ang 323 is the first such heading | Agent-checked |
| E19 | A Chaubole headword | — | No CHAUBOLE / CHAUBOLAS headword in any volume (OCR search) | A | — | Unverified (an OCR search, not a page check) |

**What EoS does and does not settle.**

- **It supports:**
  - Surdas for line 53935 (E1);
  - the A-08 divisions ending on Ang 1384 (E10).
- **It does not settle:**
  - **who composed lines 53936–53943**: the EoS contradicts itself (E2 against E5);
  - **whether the Chaubole are addressed to the four or speak in their voice** (E11 against Faridkot
    C9);
  - **A-10**: no entry addresses whether the Ang 695 labels are headings;
  - **A-11**: no entry addresses the authorship of a Bhagat-run heading.
- **Its counts** (E6/E7, E9/E15, E16/E17) are mutually inconsistent and are not printed numbering.
  They are not used as evidence for any item.

## Identifiers

An identifier is defined here only where the companion material defines it.

| Id | Meaning, as defined | Where defined | Note |
|---|---|---|---|
| A-07, A-08, A-10, A-11 | "Bhagat attribution findings", rows of § 6 of the G3 1.4.9 pack | gurbani-soul-ios `docs/review/g3-1.4.9/README.md` lines 851–877, blob `fa37988…`, commit `200cf10` (2026-10-25). Its own status is "unreviewed". | That pack gives A-08 as **Angs 1363–1384**, which is correct. PR #17 says 1385. |
| A-11 / Ang 323 | PR #17's ledger label for line 14771; PR #18 calls it "A-11b" | `pipeline/attribution_ledger.json` (`bhagat-run-heading-ang323`) | **Not in the G3 1.4.9 list**. The ledger says so itself. |
| R-21 | Roster note "Bhagat Surdas Ji", status draft | the same iOS file, line 629 | Cited by PR #17 for A-07 |
| L-05a | Timeline item "1604 · The Adi Granth is compiled" | the same iOS file, line 350 | **Not used by any item in this pack** |
| M-P09 | Map place "Bhagat Trilochan Ji · Barsi (one of two traditions)" | the same iOS file, line 397 | **Not used by any item in this pack** |
| R1–R4 | **Editorial text-repair rules** of `fix_text` (Unicode repairs), not review items | sggs-data `audit/editorial-ledger.jsonl` lines 11–14 | **Unrelated to the G3 attribution items.** Do not confuse them with the risk ids in `RISKS.md` (G-, D-, C-, P-) |
| G3 | The human scholarly review gate (a Granthi or Gurbani scholar) | the G3 1.4.9 pack header; `RECOMMENDATIONS.md` | — |
| G-1…, D-1…, C-1…, P-1… | Risk ids | `RISKS.md` (this pack) | Defined here |
