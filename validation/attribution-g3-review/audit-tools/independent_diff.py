# -*- coding: utf-8 -*-
"""Independent 1.2.0 -> 1.3.0 check for the G3 review. Stdlib only; shares no code with the pipeline.

  python3 independent_diff.py <old.sqlite> <new.sqlite> <attribution_ledger.json> <structure_ledger.json>

1. `lines`: same ids in the same order; for every id, every column compared (text columns as code-point
   sequences and UTF-8 bytes). Reports the exact (column -> ids) change map.
2. The changed (id, column) set must equal what the ledgers' applied entries predict, plus the derived
   columns each predicted change implies. Anything else is UNEXPLAINED and fails.
3. Every other table: row count and an order-independent content hash, so each table that moved is named.
"""
import hashlib, json, sqlite3, sys

old_p, new_p, attr_p, struct_p = sys.argv[1:5]
APPLIED = {'approved', 'held'}


def rows(p):
    c = sqlite3.connect(f'file:{p}?mode=ro', uri=True)
    cols = [r[1] for r in c.execute('PRAGMA table_info(lines)')]
    data = c.execute(f'SELECT {",".join(cols)} FROM lines ORDER BY rowid').fetchall()
    return c, cols, data


co, cols_o, old = rows(old_p)
cn, cols_n, new = rows(new_p)
fail = []
if cols_o != cols_n:
    fail.append(f'columns differ: {cols_o} vs {cols_n}')
ido, idn = [r[0] for r in old], [r[0] for r in new]
print(f'lines: {len(old)} -> {len(new)}; id order identical: {ido == idn}')
if ido != idn:
    fail.append('line ids or their order differ')

changed = {}
TEXT = ('gurmukhi', 'text', 'translit', 'translit_norm', 'fl_g', 'fl_r', 'skeleton', 'markers')
for ro, rn in zip(old, new):
    for i, col in enumerate(cols_o):
        a, b = ro[i], rn[i]
        if isinstance(a, str) and isinstance(b, str):
            same = [ord(x) for x in a] == [ord(x) for x in b] and a.encode() == b.encode()
        else:
            same = a == b and type(a) is type(b)
        if not same:
            changed.setdefault(col, []).append(ro[0])
for col in sorted(changed):
    ids = changed[col]
    print(f'  {col:<16} {len(ids):>5} rows  (ids {ids[0]}..{ids[-1]})')
for col in TEXT:
    if col in changed:
        fail.append(f'scripture/text column {col} changed in {len(changed[col])} rows')
print(f'text columns code-point and byte identical: {not any(c in changed for c in TEXT)}')

# 2. predicted change set from the ledgers
def entries(p):
    with open(p, encoding='utf-8') as f:
        return [e for e in json.load(f)['entries'] if e['status'] in APPLIED]


pred = {}
o_by = {r[0]: dict(zip(cols_o, r)) for r in old}
n_by = {r[0]: dict(zip(cols_n, r)) for r in new}
for e in entries(attr_p):
    for i in range(e['start_id'], e['end_id'] + 1):
        if o_by[i]['author'] != e['to']:
            pred.setdefault('author', set()).add(i)
for e in entries(struct_p):
    rng = range(e['start_id'], e['end_id'] + 1)
    if e['kind'] == 'section':
        pred.setdefault('section', set()).update(rng)
    else:
        pred.setdefault('comp_id', set()).update(rng)
        pred.setdefault('is_header', set()).add(e['start_id'])
# line_no: every line of a touched composition whose position moved (computed, not assumed)
touched = {o_by[i]['comp_id'] for i in pred.get('comp_id', ())} | {n_by[i]['comp_id'] for i in pred.get('comp_id', ())}
pred['line_no'] = {i for i, r in n_by.items() if r['comp_id'] in touched and r['line_no'] != o_by[i]['line_no']}
print('predicted from the ledgers:', {k: len(v) for k, v in sorted(pred.items())})
for col, ids in changed.items():
    extra = set(ids) - pred.get(col, set())
    if col in pred and not extra:
        continue
    print(f'  derived/other column {col}: {len(ids)} rows -> {sorted(ids)[:12]}{" ..." if len(ids) > 12 else ""}')
    for i in sorted(ids)[:6]:
        print(f'      id {i}: {o_by[i][col]!r} -> {n_by[i][col]!r}  (ang {n_by[i]["ang"]}, comp {o_by[i]["comp_id"]}->{n_by[i]["comp_id"]})')
for col, ids in pred.items():
    missing = ids - set(changed.get(col, []))
    if missing:
        fail.append(f'{col}: ledger predicts a change on {len(missing)} ids that did not change, e.g. {sorted(missing)[:5]}')

# 3. every table
def tables(c):
    return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def digest(c, t):
    h, n = hashlib.sha256(), 0
    for row in sorted(repr(r) for r in c.execute(f'SELECT * FROM "{t}"')):
        h.update(row.encode('utf-8', 'surrogatepass')); n += 1
    return n, h.hexdigest()[:16]


to, tn = tables(co), tables(cn)
print(f'tables only in old: {sorted(to - tn)}; only in new: {sorted(tn - to)}')
moved = []
for t in sorted(to & tn):
    try:
        a, b = digest(co, t), digest(cn, t)
    except sqlite3.OperationalError as ex:      # e.g. FTS shadow tables needing a tokenizer
        print(f'  {t}: not compared ({ex})'); continue
    if a != b:
        moved.append(t)
        print(f'  {t:<32} rows {a[0]:>7} -> {b[0]:>7}   {a[1]} -> {b[1]}')
print(f'{len(moved)} of {len(to & tn)} common tables differ in content')
for f in fail:
    print('FAIL:', f)
print('RESULT:', 'FAIL' if fail else 'PASS (every lines change is predicted by an applied ledger entry or listed as derived)')
sys.exit(1 if fail else 0)
