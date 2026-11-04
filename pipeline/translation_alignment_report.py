# -*- coding: utf-8 -*-
"""Compare the English layer of two DBs line by line and write the alignment ledger + audit.

Usage: python3 pipeline/translation_alignment_report.py <pre.sqlite> <post.sqlite> [--out validation]

Ledger: every line whose English row was added, removed or changed, with old/new quality.
Audit:  lines still without English, per Ang and per raag, and every span.
Exit 1 when a row that was exact or skeleton before now carries different English
(those were never in question) unless it became part of a span or is listed, with its reason,
in validation/translation-alignment-reviewed.json.
"""
import sys, json, sqlite3, collections, os, hashlib

pre, post = sys.argv[1], sys.argv[2]
out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'validation'


def en(db):
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    rows = {r[0]: (r[1], r[2], r[3]) for r in con.execute(
        "SELECT line_id, text, match_quality, source FROM translations WHERE lang='en'")}
    spans = []
    if con.execute("SELECT 1 FROM sqlite_master WHERE name='translation_spans'").fetchone():
        spans = con.execute("SELECT first_line_id, last_line_id, source FROM translation_spans "
                            "WHERE lang='en' ORDER BY first_line_id").fetchall()
    lines = con.execute('SELECT id, ang, raag, is_header, text FROM lines ORDER BY id').fetchall()
    con.close()
    return rows, spans, lines


a, _, lines = en(pre)
b, spans, lines_b = en(post)
assert [l[:2] for l in lines] == [l[:2] for l in lines_b], 'lines differ between the two DBs'
member = {}
for first, last, _ in spans:
    for i in range(first, last + 1):
        member[i] = (first, last)

reviewed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'validation',
                             'translation-alignment-reviewed.json')
reviewed = json.load(open(reviewed_path, encoding='utf-8')) if os.path.exists(reviewed_path) else {}
ledger, bad = [], []
for lid, ang, raag, hdr, text in lines:
    o, n = a.get(lid), b.get(lid)
    if o == n or (o and n and o[0] == n[0] and o[1] == n[1]):
        continue
    kind = 'added' if not o else 'removed' if not n else 'changed'
    e = {'line_id': lid, 'ang': ang, 'kind': kind, 'header': bool(hdr),
         'old_quality': o[1] if o else None, 'new_quality': n[1] if n else None,
         'span': list(member[lid]) if lid in member else None}
    # the English itself stays in the DB; the ledger records which string by a short hash
    h = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]
    if o and o[0] != (n[0] if n else None):
        e['old_en_sha'] = h(o[0])
    if n and (not o or o[0] != n[0]):
        e['new_en_sha'] = h(n[0])
    ledger.append(e)
    if o and o[1] in ('exact', 'skeleton') and (not n or n[0] != o[0]) and lid not in member \
            and str(lid) not in reviewed:
        bad.append(e)

missing = [(lid, ang, raag, hdr, text) for lid, ang, raag, hdr, text in lines
           if lid not in b and lid not in member]
audit = {
    'lines': len(lines),
    'with_english_or_in_span': len(lines) - len(missing),
    'missing_verse': sum(1 for m in missing if not m[3]),
    'missing_headings': sum(1 for m in missing if m[3]),
    'spans': len(spans),
    'span_sizes': dict(sorted(collections.Counter(l - f + 1 for f, l, _ in spans).items())),
    'quality': dict(sorted(collections.Counter(v[1] for v in b.values()).items())),
    'missing_verse_per_ang': dict(sorted(collections.Counter(m[1] for m in missing if not m[3]).items())),
    'missing_verse_per_raag': dict(sorted(collections.Counter(m[2] or '-' for m in missing if not m[3]).items())),
    'missing': [{'line_id': m[0], 'ang': m[1], 'header': bool(m[3]), 'text': m[4]} for m in missing],
    'spans_list': [{'first_line_id': f, 'last_line_id': l, 'source': s} for f, l, s in spans],
}
summary = collections.Counter((e['kind'], e['old_quality'], e['new_quality']) for e in ledger)
os.makedirs(out, exist_ok=True)
json.dump({'pre_missing': len(lines) - len(a), 'changes': len(ledger),
           'summary': {f'{k[0]}:{k[1]}->{k[2]}': v for k, v in sorted(summary.items(), key=str)},
           'entries': ledger}, open(f'{out}/translation-alignment-ledger.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(audit, open(f'{out}/translation-alignment-audit.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in audit.items() if k in
                  ('lines', 'missing_verse', 'missing_headings', 'spans', 'span_sizes', 'quality')}, ensure_ascii=False))
for k, v in sorted(summary.items(), key=str): print(f'  {k}: {v}')
if bad:
    print(f'FAIL: {len(bad)} previously exact/skeleton rows changed outside a span')
    for e in bad[:20]: print('  ', e)
    sys.exit(1)
print(f'PASS: no exact/skeleton row changed outside a span ({len(reviewed) - 1} reviewed exceptions)')
