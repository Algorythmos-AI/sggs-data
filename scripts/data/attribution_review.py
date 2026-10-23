#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write the scholar review pack for an attribution change (gate G3).

    python3 scripts/data/attribution_review.py OLD.jsonl [--shabados database.sqlite]

Replays pipeline/attribution_pass.py on OLD and writes validation/attribution-review/index.html:
one section per changed span with the verbatim lines, the rule and evidence that fired, the
author before and after, and (optionally) the ShabadOS writer for each line; then every
contested flag, unchanged. Self-contained HTML; every text is escaped.
"""
import argparse, collections, html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import attribution_pass as ap

OUT_DIR = os.path.join(ROOT, 'validation', 'attribution-review')
RULE = {'A': 'Rule A — rubric + signature agree', 'B': 'Rule B — salok scope in a Bhagat salok block',
        'C': 'Rule C — reviewed ledger decision', 'H': 'Heading adopts the body it opens'}
e = html.escape


def spans(log):
    out = []
    for lid, ang, old, new, rule, ev in log:
        if out and out[-1]['end'] == lid - 1 and out[-1]['key'] == (old, new, rule):
            out[-1]['end'] = lid
        else:
            out.append({'start': lid, 'end': lid, 'ang': ang, 'key': (old, new, rule), 'ev': ev})
    return out


def sos_writers(path, recs):
    if not path: return {}
    import crosscheck_authors as cc
    sos = cc.load_sos(path)
    by_ang = collections.defaultdict(list)
    for r in recs: by_ang[r['ang']].append(r)
    import difflib
    w = {}
    for ang, ours in by_ang.items():
        theirs = sos.get(ang, [])
        sm = difflib.SequenceMatcher(a=[cc.key_ours(r) for r in ours], b=[t[0] for t in theirs], autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): w[ours[a + k]['id']] = theirs[b + k][1]
    return w


def main():
    p = argparse.ArgumentParser(); p.add_argument('old'); p.add_argument('--shabados')
    args = p.parse_args()
    with open(args.old, encoding='utf-8') as f: old = [json.loads(l) for l in f]
    with open(os.path.join(ROOT, 'pipeline', 'attribution_decisions.json'), encoding='utf-8') as f:
        ledger = json.load(f)
    new = [dict(r) for r in old]
    log = ap.apply(new, ledger)
    by_id = {r['id']: r for r in new}
    sw = sos_writers(args.shabados, new)
    net = collections.Counter()
    for _, _, a, b, _, _ in log: net[a or '(none)'] -= 1; net[b or '(none)'] += 1

    h = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Attribution review</title><style>',
         ':root{--bg:#fbf8f1;--ink:#231f1a;--mute:#6b6257;--line:#e3dccd;--ok:#2f6b3a;--warn:#8a4b00}',
         '@media (prefers-color-scheme:dark){:root{--bg:#191612;--ink:#efe8db;--mute:#a59a8a;--line:#3a332a;--ok:#8fd19e;--warn:#f0b46a}}',
         'body{background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif;margin:0 auto;max-width:980px;padding:24px 16px}',
         'h1{font-size:24px}h2{font-size:18px;margin-top:36px}table{border-collapse:collapse;width:100%}',
         'td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}',
         '.g{font-family:"Sant Lipi","Noto Sans Gurmukhi",sans-serif;font-size:18px}.m{color:var(--mute);font-size:13px}',
         '.ok{color:var(--ok)}.warn{color:var(--warn)}section{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:14px 0}',
         '</style></head><body>',
         '<h1>Authorship review — Sri Guru Granth Sahib Ji</h1>',
         '<p>The <b>author</b> field changes; the Gurmukhi does not. Every line is shown verbatim from the '
         'corpus. Sign each section, or mark it for discussion. Nothing reaches production until this pack is signed (gate G3).</p>',
         f'<p class="m">{len(log)} lines in {len(spans(log))} spans. ShabadOS 4.8.7 column = independent cross-check, not a source.</p>',
         '<h2>Net change per author</h2><table><tr><th>Author</th><th>Lines</th></tr>']
    for k, v in sorted(net.items(), key=lambda x: x[1]):
        if v: h.append(f'<tr><td>{e(k)}</td><td>{v:+d}</td></tr>')
    h.append('</table><h2>Changed spans</h2>')
    for i, s in enumerate(spans(log), 1):
        old_a, new_a, rule = s['key']
        rows = [by_id[x] for x in range(s['start'], s['end'] + 1)]
        agree = sum(1 for r in rows if sw.get(r['id']) == new_a)
        known = sum(1 for r in rows if r['id'] in sw)
        badge = (f'<span class="ok">ShabadOS agrees {agree}/{known}</span>' if known and agree == known
                 else f'<span class="warn">ShabadOS agrees {agree}/{known}</span>' if known else '')
        h.append(f'<section id="s{i}"><b>{i}. Ang {s["ang"]}</b> · ids {s["start"]}–{s["end"]} · '
                 f'{e(old_a or "(none)")} → <b>{e(new_a)}</b> {badge}<div class="m">{e(RULE[rule])}: {e(s["ev"])}</div>')
        h.append('<table>')
        show = rows if len(rows) <= 14 else rows[:6] + [None] + rows[-6:]
        for r in show:
            if r is None:
                h.append(f'<tr><td class="m" colspan="3">… {len(rows) - 12} more lines …</td></tr>'); continue
            h.append(f'<tr><td class="m">{r["id"]}{" · heading" if r["is_header"] else ""}</td>'
                     f'<td class="g" lang="pa">{e(r["gurmukhi"])}</td><td class="m">{e(sw.get(r["id"], ""))}</td></tr>')
        h.append('</table><p class="m">Reviewer: ______ &nbsp; ☐ agree &nbsp; ☐ discuss</p></section>')
    h.append('<h2>Contested — left unchanged</h2>')
    for f in ledger['flags']:
        h.append(f'<section><b>{e(f["key"])}</b> · currently {e(f["current"])}<div>{e(f["note"])}</div>'
                 f'<p class="m">Reviewer decision: ______</p></section>')
    h.append('</body></html>')
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f: f.write('\n'.join(h) + '\n')
    print(f'review pack: {os.path.join(OUT_DIR, "index.html")} ({len(spans(log))} spans, {len(ledger["flags"])} flags)')


if __name__ == '__main__':
    main()
