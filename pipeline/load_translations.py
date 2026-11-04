# -*- coding: utf-8 -*-
"""Align fetched translation pairs (gurmukhi -> english) to corpus line_ids and
load them into the translations table. Translations are NEVER scripture: stored
in a separate table with source attribution, displayed labeled and subordinate.

Usage: python3 load_translations.py <db_path> <pairs.jsonl ...>
Pair format per line: {"ang": N, "gurmukhi": "...", "en": "..."}
"""
import sys, json, sqlite3, glob
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from build_clock import stamp

DB = sys.argv[1]
SOURCE_ID = 'ssk-banidb'
args = sys.argv[2:]
if args and args[0].startswith('--source='):
    SOURCE_ID = args[0].split('=', 1)[1]; args = args[1:]
files = []
for pat in args:
    files += glob.glob(pat)

con = sqlite3.connect(DB)
cur = con.cursor()
cur.executescript(('''
CREATE TABLE IF NOT EXISTS translations(
  line_id INT, lang TEXT, source TEXT, text TEXT, match_quality TEXT,
  PRIMARY KEY(line_id, lang));
CREATE TABLE IF NOT EXISTS sources(
  source_id TEXT PRIMARY KEY, kind TEXT, attribution TEXT, license TEXT, ingest_date TEXT);
INSERT OR REPLACE INTO sources VALUES(
  'ssk-banidb', 'translation-en',
  'English translation by Dr. Sant Singh Khalsa, sourced via BaniDB (banidb.com)',
  'Personal, local, non-commercial use with attribution', '@BUILD_DATE@');
INSERT OR REPLACE INTO sources VALUES(
  'ssk-shabados', 'translation-en',
  'English translation by Dr. Sant Singh Khalsa, via the ShabadOS open database (github.com/shabados/database, release 4.8.7)',
  'Open data with attribution; translation author attribution required', '@BUILD_DATE@');
''').replace('@BUILD_DATE@', stamp('%Y-%m-%d')))   # build clock, not wall clock

from translation_align import Line, Rec, align

cur.execute('''CREATE TABLE IF NOT EXISTS translation_spans(
  first_line_id INT, last_line_id INT, lang TEXT, source TEXT,
  PRIMARY KEY(first_line_id, lang))''')

# Corpus lines in Granth order; records in source order (file order = ShabadOS order_id).
lines = [Line(*r) for r in cur.execute(
    'SELECT id, ang, comp_id, is_header, text FROM lines ORDER BY id')]
recs, stats = [], {'exact': 0, 'skeleton': 0, 'fuzzy': 0, 'span': 0, 'unplaced': 0, 'empty': 0}
for f in files:
    for raw in open(f, encoding='utf-8'):
        raw = raw.strip()
        if not raw: continue
        try: p = json.loads(raw)
        except json.JSONDecodeError: continue
        g, en, ang = p.get('gurmukhi', ''), (p.get('en') or '').strip(), p.get('ang')
        if not g or not en or ang is None: stats['empty'] += 1; continue
        recs.append(Rec(len(recs), ang, g, en))

placements, ambiguous = align(recs, lines)
stats['unplaced'] = len(recs) - len(placements)

# A later pass (BaniDB repair files) may replace a single-line row as v1 did, but it never
# touches a span: not its row, not any line inside it.
span_members = set()
for first, last in cur.execute("SELECT first_line_id, last_line_id FROM translation_spans WHERE lang='en'").fetchall():
    span_members.update(range(first, last + 1))
rows, spans = [], []
for rec, run, quality in placements:
    ids = [x.id for x in run]
    if span_members.intersection(ids): stats['unplaced'] += 1; continue
    if quality == 'span':
        if cur.execute("SELECT 1 FROM translations WHERE lang='en' AND line_id BETWEEN ? AND ? LIMIT 1",
                       (ids[0], ids[-1])).fetchone():
            # an earlier pass already gave a member line its own English: a joined record must
            # not replace it (BaniDB's Ang 13 record joins two lines but translates only one)
            stats['unplaced'] += 1; continue
        spans.append((ids[0], ids[-1], 'en', SOURCE_ID))
    stats[quality] += 1
    rows.append((ids[-1], 'en', SOURCE_ID, rec.en, quality))   # a span's English sits under its last line

cur.executemany('INSERT OR REPLACE INTO translation_spans VALUES(?,?,?,?)', spans)
cur.executemany('INSERT OR REPLACE INTO translations VALUES(?,?,?,?,?)', rows)
# Record the TOTAL en rows in the table, not just this batch — rebuild_all.sh calls
# load_translations twice, and writing len(rows) made the 2nd (small) call clobber the
# count via INSERT OR REPLACE. Derive from the table so the count is always the true total.
total_en = cur.execute("SELECT count(*) FROM translations WHERE lang='en'").fetchone()[0]
cur.execute("INSERT OR REPLACE INTO meta VALUES('translations_en', ?)", (str(total_en),))
con.commit(); con.close()
print(f'loaded {len(rows)} translations | match quality: {stats}')
for r, why in ambiguous[:10]: print('  not placed (%s): Ang %s %s' % (why, r.ang, r.g[:50]))
