#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Proof for an attribution change: OLD.jsonl -> NEW.jsonl differ in `author` ONLY, every
changed line is explained by attribution_pass.py, and the change set equals the pinned golden
(validation/attribution-golden.json) -- so any unreviewed author change fails the build.

usage: verify_attribution.py OLD.jsonl NEW.jsonl [--golden PATH] [--write-golden]
Exit 0 = PASS. --write-golden records the current change set (only after human review).
"""
import argparse, collections, hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attribution_pass as ap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(ROOT, 'validation', 'attribution-golden.json')
LEDGER = os.path.join(ROOT, 'pipeline', 'attribution_decisions.json')


def load(path):
    return [json.loads(l) for l in open(path, encoding='utf-8')]


def change_set(old, new):
    return sorted((o['id'], o['author'], n['author']) for o, n in zip(old, new)
                  if o['author'] != n['author'])


def summary(changes):
    net = collections.Counter()
    for _, a, b in changes:
        net[a or '(none)'] -= 1; net[b or '(none)'] += 1
    digest = hashlib.sha256(json.dumps(changes, ensure_ascii=False).encode('utf-8')).hexdigest()
    return {'lines_changed': len(changes), 'change_set_sha256': digest,
            'net_by_author': dict(sorted((k, v) for k, v in net.items() if v))}


def main():
    a = argparse.ArgumentParser()
    a.add_argument('old'); a.add_argument('new')
    a.add_argument('--golden', default=GOLDEN)
    a.add_argument('--write-golden', action='store_true')
    args = a.parse_args()
    old, new = load(args.old), load(args.new)
    fails = []

    # 1. same records, same order; every field but author byte-identical
    if [r['id'] for r in old] != [r['id'] for r in new]:
        fails.append('record ids/order differ')
    else:
        other = collections.Counter()
        for o, n in zip(old, new):
            for k in set(o) | set(n):
                if k != 'author' and o.get(k) != n.get(k): other[k] += 1
        for k, c in sorted(other.items()):
            fails.append(f'field {k!r} changed in {c} records (only author may change)')

    # 2. every change is what the pass produces from OLD (no hand edits)
    changes = change_set(old, new)
    replay = [dict(r) for r in old]
    ap.apply(replay, json.load(open(LEDGER, encoding='utf-8')))
    if change_set(old, replay) != changes:
        fails.append('NEW is not exactly attribution_pass(OLD): an author change has no rule behind it')

    # 3. the change set equals the reviewed golden
    s = summary(changes)
    print(f"author changes: {s['lines_changed']} lines  sha256 {s['change_set_sha256'][:16]}…")
    for k, v in s['net_by_author'].items(): print(f'  {v:+6d}  {k}')
    if args.write_golden:
        json.dump(s, open(args.golden, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        open(args.golden, 'a', encoding='utf-8').write('\n')
        print(f'golden written: {args.golden}')
    elif s != json.load(open(args.golden, encoding='utf-8')):
        fails.append(f'change set differs from the reviewed golden {args.golden}')

    if fails:
        print('RESULT: FAIL — ' + '; '.join(fails)); return 1
    print('RESULT: PASS — author-only, rule-explained, equal to the reviewed golden'); return 0


if __name__ == '__main__':
    sys.exit(main())
