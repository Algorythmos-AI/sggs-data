# -*- coding: utf-8 -*-
"""Gate for the English layer's line alignment. Fails closed.

Usage: python3 pipeline/translation_alignment_gate.py <db> [--sources pipeline/translations]

Always (CI, no private sources needed):
  - every span covers 2-4 consecutive lines of ONE composition, none of them a heading;
  - spans never overlap; the English of a span sits on its last line (quality 'span'),
    and no other line of the span carries English;
  - every 'span' row has its span, and every English string is non-empty.
When the source files are present (local rebuilds), also, written independently of the loader:
  - every English string is byte-identical to a source record whose Gurmukhi equals the line
    (or, for a span, the span's lines joined) by exact or skeleton comparison, or fuzzy >= 0.92;
  - the placed records are in source order (monotonic), so no repeat took another's English;
  - no source record is used twice.
"""
import sys, os, re, json, glob, sqlite3, unicodedata, difflib, collections

db = sys.argv[1]
src_dir = sys.argv[sys.argv.index('--sources') + 1] if '--sources' in sys.argv else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
problems = []
con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
lines = {r[0]: r[1:] for r in con.execute('SELECT id, ang, comp_id, is_header, text FROM lines')}
en = {r[0]: r[1:] for r in con.execute(
    "SELECT line_id, text, match_quality, source FROM translations WHERE lang='en'")}
has_spans = con.execute("SELECT 1 FROM sqlite_master WHERE name='translation_spans'").fetchone()
spans = con.execute("SELECT first_line_id, last_line_id, source FROM translation_spans WHERE lang='en' "
                    "ORDER BY first_line_id").fetchall() if has_spans else []
con.close()

# --- structure (always) ------------------------------------------------------------------
covered = {}
prev_last = 0
for first, last, source in spans:
    ids = list(range(first, last + 1))
    if not 2 <= len(ids) <= 4: problems.append(f'span {first}-{last}: length {len(ids)}')
    if first <= prev_last: problems.append(f'span {first}-{last} overlaps the previous span')
    prev_last = last
    if any(i not in lines for i in ids): problems.append(f'span {first}-{last}: missing line'); continue
    if len({lines[i][1] for i in ids}) != 1: problems.append(f'span {first}-{last}: crosses compositions')
    if any(lines[i][2] for i in ids): problems.append(f'span {first}-{last}: includes a heading')
    if en.get(last, (None, None))[1] != 'span': problems.append(f'span {first}-{last}: last line has no span row')
    if en.get(last, (None, None, None))[2] != source: problems.append(f'span {first}-{last}: source differs')
    for i in ids[:-1]:
        if i in en: problems.append(f'span {first}-{last}: member {i} has its own English')
    for i in ids: covered[i] = (first, last)
for lid, (text, q, _) in en.items():
    if not (text or '').strip(): problems.append(f'line {lid}: empty English')
    if q == 'span' and covered.get(lid, (0, 0))[1] != lid: problems.append(f'line {lid}: span row without a span')

# --- against the sources (when present) --------------------------------------------------
MATRAS = 'ਾਿੀੁੂੇੈੋੌ੍ੰਂਃ਼ੱੑੵ'
def n(s):
    s = re.sub(r'[॥।|੦-੯\s]+', ' ', unicodedata.normalize('NFC', s)).strip()
    return ' '.join(w for w in s.split() if w not in ('ਰਹਾਉ', 'ਦੂਜਾ'))   # comparison only
def sk(s): return re.sub('[' + MATRAS + ' ]', '', n(s))

files = {'ssk-shabados': [os.path.join(src_dir, 'en_full_shabados.jsonl')],
         'ssk-banidb': sorted(glob.glob(os.path.join(src_dir, 'en_0*.jsonl')) + glob.glob(os.path.join(src_dir, 'en_9*.jsonl')))}
checked = 0
if all(os.path.exists(f) for fs in files.values() for f in fs) and files['ssk-banidb']:
    for source, fs in files.items():
        recs = []
        for f in fs:
            for raw in open(f, encoding='utf-8'):
                if raw.strip():
                    p = json.loads(raw); recs.append((len(recs), p['ang'], p['gurmukhi'], (p.get('en') or '').strip()))
        by_en = collections.defaultdict(list)
        for r in recs: by_en[r[3]].append(r)
        used, order = collections.Counter(), []
        for lid in sorted(l for l, v in en.items() if v[2] == source):
            text, q, _ = en[lid]
            first = covered.get(lid, (lid, lid))[0]
            g = ' '.join(n(lines[i][3]) for i in range(first, lid + 1))
            ok = [r for r in by_en.get(text, []) if abs(r[1] - lines[lid][0]) <= 1 and (
                n(r[2]) == g or sk(r[2]) == sk(' '.join(lines[i][3] for i in range(first, lid + 1))) or
                difflib.SequenceMatcher(None, n(r[2]), g).ratio() >= 0.92)]
            if not ok:
                problems.append(f'line {lid} ({source}): English matches no source record for this Gurmukhi'); continue
            # pick the earliest record at or after the previous one (order proof)
            after = [r for r in ok if not order or r[0] > order[-1]]
            r = after[0] if after else ok[0]
            if after: order.append(r[0])
            else: problems.append(f'line {lid} ({source}): placed out of source order')
            used[r[0]] += 1
            checked += 1
        problems += [f'{source}: record {k} used {c} times' for k, c in used.items() if c > 1]
    mode = f'sources checked ({checked} rows)'
else:
    mode = 'sources absent: structure only'

print(f'translation alignment: {len(en)} English rows, {len(spans)} spans; {mode}')
if problems:
    for p in problems[:40]: print('  FAIL', p)
    print(f'FAIL: {len(problems)} problem(s)'); sys.exit(1)
print('PASS')
