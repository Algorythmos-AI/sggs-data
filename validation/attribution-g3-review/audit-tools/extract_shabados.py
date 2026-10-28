# -*- coding: utf-8 -*-
"""Independent evidence extraction for the G3 audit (auditor B). Read-only on every database.

usage: python3 extract.py <sggs-data repo> <baseline 1.2.0 sqlite> <out dir>

- ShabadOS 4.8.7 is read from <repo>/database.sqlite (sha256 checked against pipeline/shabados.SHA256SUMS).
- Corpus lines (1.3.0 held = <repo>/db/sggs.sqlite) are aligned to ShabadOS lines Ang by Ang with the
  repository's own first-letter aligner (pipeline/crosscheck_authors.py: key_ours/key_sos + difflib).
- ShabadOS Gurmukhi is GurbaniAkhar ASCII; it is converted with gurmukhiutils (if installed) only for display.
  ShabadOS Punjabi commentary (Prof. Sahib Singh = translation_source 6, Faridkot Teeka = 5) is stored in
  Unicode already and is compared codepoint-for-codepoint with the quotes in PR #18.
Outputs: extract.json (every requested line, its ShabadOS record and both commentaries in full),
quotes.json (each PR #18 quote: found where, exact or not), headings.json, sections.json.
Stdlib only (+ optional gurmukhiutils for display).
"""
import collections, difflib, hashlib, json, os, sqlite3, sys, unicodedata

REPO, BASE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(REPO, 'pipeline'))
from crosscheck_authors import key_ours, key_sos  # noqa: E402  (repo's own aligner keys)

try:
    from gurmukhiutils.unicode import unicode as g_uni
except Exception:  # display only
    g_uni = lambda s: s

SOS = os.path.join(REPO, 'database.sqlite')
NEW = os.path.join(REPO, 'db', 'sggs.sqlite')
pinned = open(os.path.join(REPO, 'pipeline', 'shabados.SHA256SUMS')).read().split()[0]
actual = hashlib.sha256(open(SOS, 'rb').read()).hexdigest()

RANGES = [(53930, 53943), (58270, 58300), (58788, 58792), (59085, 59090),
          (30078, 30100), (23466, 23473), (14765, 14773)]
WANT = sorted({i for a, b in RANGES for i in range(a, b + 1)})


def ro(p):
    c = sqlite3.connect(f'file:{p}?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    return c


sos, new, base = ro(SOS), ro(NEW), ro(BASE)
corpus = {r['id']: dict(r) for r in new.execute(
    'SELECT id, ang, author, is_header, comp_id, line_no, section, gurmukhi, text, fl_g FROM lines')}
base_rows = {r['id']: dict(r) for r in base.execute(
    'SELECT id, author, is_header, comp_id, line_no, section FROM lines')}

SQL_SOS = """SELECT l.id, l.shabad_id, s.sttm_id, l.type_id, lt.name_english AS line_type, w.name_english AS writer,
  c.name_english AS section, ss.name_english AS subsection, l.source_page, l.source_line, l.order_id,
  l.first_letters, l.gurmukhi
  FROM lines l JOIN shabads s ON s.id = l.shabad_id JOIN writers w ON w.id = s.writer_id
  JOIN sections c ON c.id = s.section_id LEFT JOIN subsections ss ON ss.id = s.subsection_id
  LEFT JOIN line_types lt ON lt.id = l.type_id
  WHERE s.source_id = 1 AND l.source_page = ? ORDER BY l.order_id"""


def sos_page(ang):
    return [dict(r) for r in sos.execute(SQL_SOS, (ang,))]


def commentary(line_id):
    out = {}
    for r in sos.execute('SELECT translation_source_id, translation, additional_information FROM translations '
                         'WHERE line_id = ? AND translation_source_id IN (5, 6)', (line_id,)):
        out[{5: 'faridkot', 6: 'sahib_singh'}[r[0]]] = {
            'translation': r[1], 'additional_information': json.loads(r[2] or '{}')}
    return out


# --- align Ang by Ang (same method as crosscheck_authors.compare) -------------------------------
HEAD_IDS = [r[0] for r in new.execute(
    "SELECT id FROM lines WHERE is_header = 1 AND gurmukhi LIKE '%ਬਾਣੀ%' AND (gurmukhi LIKE '%ਭਗਤਾ ਕੀ%' OR "
    "gurmukhi LIKE '%ਭਗਤਾਂ ਕੀ%' OR gurmukhi LIKE '%ਬਾਣੀ ਭਗਤਾ%' OR gurmukhi LIKE '%ਬਾਣੀ ਭਗਤਾਂ%')")]
align = {}
for ang in sorted({corpus[i]['ang'] for i in WANT + HEAD_IDS}):
    ours = [r for r in sorted(corpus.values(), key=lambda r: r['id']) if r['ang'] == ang]
    theirs = sos_page(ang)
    sm = difflib.SequenceMatcher(a=[key_ours(r) for r in ours], b=[key_sos(t['first_letters'] or '') for t in theirs],
                                 autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            align[ours[a + k]['id']] = theirs[b + k]

rows = []
for i in WANT:
    r, b = corpus[i], base_rows[i]
    t = align.get(i)
    rec = {'corpus_id': i, 'ang': r['ang'], 'gurmukhi': r['gurmukhi'],
           'v1_2_0': {k: b[k] for k in ('author', 'is_header', 'comp_id', 'line_no', 'section')},
           'v1_3_0': {k: r[k] for k in ('author', 'is_header', 'comp_id', 'line_no', 'section')},
           'shabados': None}
    if t:
        rec['shabados'] = {**{k: t[k] for k in ('id', 'shabad_id', 'sttm_id', 'type_id', 'line_type', 'writer',
                                                'section', 'subsection', 'source_page', 'source_line', 'order_id')},
                           'gurmukhi_ascii': t['gurmukhi'], 'gurmukhi_unicode': g_uni(t['gurmukhi']),
                           'commentary': commentary(t['id'])}
    rows.append(rec)

# unaligned lines: dump the raw ShabadOS page neighbourhood so nothing is hidden
raw_pages = {}
for ang in (323, 524):
    raw_pages[ang] = [{**{k: t[k] for k in ('id', 'shabad_id', 'sttm_id', 'line_type', 'writer', 'section',
                                            'source_line', 'order_id')},
                       'gurmukhi_unicode': g_uni(t['gurmukhi']), 'commentary': commentary(t['id'])}
                      for t in sos_page(ang)]

# --- quote verification ----------------------------------------------------------------------------
QUOTES = [  # (label, quote as printed in PR #18 RECOMMENDATIONS.md, claimed corpus line, claimed source)
    ('A07-SS-53935', 'ਇਸ ਦਾ ਉੱਤਰ ਅਗਲੇ ਸ਼ਬਦ ਦੇ ਸ਼ੁਰੂ ਵਿਚ ਲਿਖੇ ਸਿਰ-ਲੇਖ ਤੋਂ ਮਿਲਦਾ ਹੈ; ਭਾਵ, ਇਹ ਇਕ ਤੁਕ \'ਸੂਰਦਾਸ\' ਜੀ ਦੀ ਹੈ।', 53935, 'sahib_singh'),
    ('A07-SS-53943a', 'ਭਾਵੇਂ ਭਗਤ ਸੂਰਦਾਸ ਜੀ ਦੀ ਇਕੋ ਹੀ ਤੁਕ ਦਰਜ ਕੀਤੀ ਹੈ, ਪਰ ਗਿਣਤੀ ਵਿਚ ਉਸ ਨੂੰ ਸਾਰੇ ਸ਼ਬਦ ਵਾਂਗ ਗਿਣਿਆ ਹੈ; ਤਾਹੀਏਂ ਹੁਣ ਤਕ ਦੀ ਗਿਣਤੀ ੮ ਬਣਦੀ ਹੈ।', 53943, 'sahib_singh'),
    ('A07-SS-53943b', 'ਇਹ ਸ਼ਬਦ ਸਤਿਗੁਰੂ ਅਰਜਨ ਸਾਹਿਬ ਜੀ ਦਾ ਆਪਣਾ ਹੈ। ਸੂਰਦਾਸ ਦਾ ਨਹੀਂ।', 53943, 'sahib_singh'),
    ('A07-FK-53935', 'ਤੌ ਇਹ ਸੂਰਦਾਸ ਜੀ ਕਾ ਸਾਰਾ ਸਬਦ ਭਾਈ ਬੰਨੋ ਦੀ ਬੀੜ ਮੇਂ ਹੈ।', 53935, 'faridkot'),
    ('A08-SS-58273', "ਗੁਰੂ ਅਰਜਨਦੇਵ ਜੀ ਦੀ ਬਾਣੀ 'ਚਉਬੋਲੇ'", 58273, 'sahib_singh'),
    ('A08-SS-58297', 'ਭਗਤ ਕਬੀਰ ਜੀ ਦੇ ਸਲੋਕ', 58297, 'sahib_singh'),
    ('A10-SS-pipa', 'ਇਸ ਸ਼ਬਦ ਵਿਚ ਭਗਤ ਪੀਪਾ ਜੀ ਮੂਰਤੀ-ਪੂਜਾ ਦਾ ਖੰਡਨ ਕਰਦੇ ਹਨ', 30098, 'sahib_singh'),
    ('A10-FK-30080', 'ਸ੍ਰੀ ਸੈਣ ਭਗਤ ਜੀ ਸ੍ਰੀ ਅਕਾਲ ਪੁਰਖ ਜੀ ਕੇ ਸਨਮੁਖ ਆਰਤੀ ਕਰ ਕੇ ਬੇਨਤੀ ਕਰਤੇ ਹੈਂ', 30080, 'faridkot'),
    ('A11-FK-23469', '॥੨੧॥੧॥੨॥ਸੁਧੁ', 23469, 'faridkot'),
]


def all_text(c):
    if not c: return ''
    return c['translation'] + '\n' + json.dumps(c['additional_information'], ensure_ascii=False)


def fold(s):  # loose comparison: drop punctuation/space, NFC
    s = unicodedata.normalize('NFC', s)
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] in 'LM' or ch.isdigit())


qres = []
by_cid = {r['corpus_id']: r for r in rows}
for label, q, cid, src in QUOTES:
    hits = []
    for r in rows:
        s = r['shabados']
        if not s: continue
        for name, c in s['commentary'].items():
            txt = all_text(c)
            if q in txt:
                hits.append({'corpus_id': r['corpus_id'], 'sos_line': s['id'], 'source': name, 'match': 'exact'})
            elif fold(q) in fold(txt):
                hits.append({'corpus_id': r['corpus_id'], 'sos_line': s['id'], 'source': name, 'match': 'loose (punctuation/space differs)'})
    qres.append({'label': label, 'quote': q, 'claimed_line': cid, 'claimed_source': src, 'hits': hits})

# --- Bhagat-run headings in 1.2.0 and 1.3.0 ------------------------------------------------------
HSQL = ("SELECT id, ang, author, gurmukhi FROM lines WHERE is_header = 1 AND gurmukhi LIKE '%ਬਾਣੀ%' AND "
        "(gurmukhi LIKE '%ਭਗਤਾ ਕੀ%' OR gurmukhi LIKE '%ਭਗਤਾਂ ਕੀ%' OR gurmukhi LIKE '%ਬਾਣੀ ਭਗਤਾ%' OR gurmukhi LIKE '%ਬਾਣੀ ਭਗਤਾਂ%') ORDER BY id")
heads = []
for r in new.execute(HSQL):
    first = new.execute('SELECT author FROM lines WHERE id > ? AND is_header = 0 ORDER BY id LIMIT 1', (r['id'],)).fetchone()[0]
    heads.append({'id': r['id'], 'ang': r['ang'], 'gurmukhi': r['gurmukhi'], 'author_1_2_0': base_rows[r['id']]['author'],
                  'author_1_3_0': r['author'], 'first_verse_author': first,
                  'shabados': ({k: align[r['id']][k] for k in ('id', 'shabad_id', 'sttm_id', 'line_type', 'writer')}
                               | {'gurmukhi_unicode': g_uni(align[r['id']]['gurmukhi'])}) if r['id'] in align else None})

# --- ShabadOS section boundaries for Angs 1363-1385 ---------------------------------------------
sec = [dict(r) for r in sos.execute(
    """SELECT c.name_english AS section, min(l.order_id) AS first_order, max(l.order_id) AS last_order,
       min(l.source_page) AS first_ang, max(l.source_page) AS last_ang, count(*) AS n
       FROM lines l JOIN shabads s ON s.id = l.shabad_id JOIN sections c ON c.id = s.section_id
       WHERE s.source_id = 1 AND l.source_page BETWEEN 1362 AND 1386 GROUP BY c.id ORDER BY min(l.order_id)""")]
for s in sec:
    for k in ('first', 'last'):
        t = sos.execute('SELECT id, gurmukhi FROM lines WHERE order_id = ?', (s[f'{k}_order'],)).fetchone()
        s[f'{k}_line'] = {'id': t[0], 'gurmukhi_unicode': g_uni(t[1])}
        inv = [cid for cid, tt in align.items() if tt['id'] == t[0]]
        s[f'{k}_corpus_id'] = inv[0] if inv else None

os.makedirs(OUT, exist_ok=True)
meta = {'shabados_sha256_pinned': pinned, 'shabados_sha256_actual': actual, 'match': pinned == actual,
        'aligned': sum(1 for r in rows if r['shabados']), 'requested': len(rows)}
for name, obj in (('extract.json', {'meta': meta, 'rows': rows, 'raw_pages': raw_pages}), ('quotes.json', qres),
                  ('headings.json', heads), ('sections.json', sec)):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
print(json.dumps(meta))
for q in qres: print(q['label'], q['claimed_line'], q['claimed_source'], '->', q['hits'] or 'NOT FOUND in requested lines')
for h in heads: print(h)
for s in sec: print({k: s[k] for k in ('section', 'first_ang', 'last_ang', 'n', 'first_corpus_id', 'last_corpus_id')})
