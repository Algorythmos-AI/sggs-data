# -*- coding: utf-8 -*-
"""The G3 approval gate for the editorial ledgers (attribution_ledger.json, structure_ledger.json).

A G3 decision is a Gurbani scholar's ruling. A green build, an engineer's approval and an agent's
recommendation are none of them that ruling. This module is the one place that decides which ledger
entries a build may apply; attribution.py, structure.py, the tests and CI all call it.

  python3 pipeline/g3_gate.py                    validate both ledgers (any build may run)
  python3 pipeline/g3_gate.py --release-check    also fail while any G3 ruling is outstanding
  python3 pipeline/g3_gate.py --hash ENTRY       print an entry's entry_sha256 (for recording a ruling)

Statuses (a closed set; anything else fails the build):
  proposed   recorded for review; never applied
  held       a G3 change applied ONLY so a held draft PR can prove its exact effect; its `g3`
             ruling is still blank. Never releasable: --release-check fails while one exists.
  approved   applied. If the entry is G3-governed (it has a `g3` block) the ruling must be
             complete: decision approve|change, reviewer, ISO date not in the future, scope equal
             to g3.item, evidence (a file in the review pack) and entry_sha256 (the hash of the
             entry as ruled on, so a later edit to its range or values voids the ruling).
  rejected   never applied; a G3-governed rejection records the same complete ruling, decision reject.
  keep       attribution only: a reviewed decision to keep the printed attribution; never applied.

An `approved` attribution entry with no `g3` block is allowed only for the owner-approved entries
listed in OWNER_APPROVED (decided before G3 existed). Removing a `g3` block therefore cannot turn a
scholar's item into an owner approval without a code change here. Every structure entry is G3-governed.
"""
import datetime, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGERS = {'attribution': os.path.join(ROOT, 'pipeline', 'attribution_ledger.json'),
           'structure': os.path.join(ROOT, 'pipeline', 'structure_ledger.json')}
PACK = 'validation/attribution-g3-review/'

STATUSES = {'attribution': {'proposed', 'held', 'approved', 'rejected', 'keep'},
            'structure': {'proposed', 'held', 'approved', 'rejected'}}
APPLIED = {'approved', 'held'}
DECISION_FOR = {'approved': {'approve', 'change'}, 'rejected': {'reject'}}
OWNER_APPROVED = {'attribution': {'japji', 'sadu'}, 'structure': set()}
RULING = ('decision', 'reviewer', 'date', 'scope', 'evidence', 'entry_sha256')
# Positive tests use this reviewer in temporary fixtures; the committed ledgers may never carry it.
FIXTURE_REVIEWER = 'TEST-FIXTURE-NOT-A-REVIEWER'
ISO_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


class GateError(Exception):
    pass


def read(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)['entries']


def entry_sha256(e):
    """Hash of what the scholar rules on: the entry without its status, hold note and g3 block."""
    body = {k: v for k, v in e.items() if k not in ('status', 'hold', 'g3')}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def problems(entries, kind, root=ROOT, today=None, allow_fixture=False):
    """Every reason these ledger entries may not be built, as a list of strings (empty = valid)."""
    today = today or datetime.date.today()
    out, seen = [], set()
    for e in entries:
        name = e.get('entry') or '<unnamed>'
        st, g3 = e.get('status'), e.get('g3')
        say = lambda msg: out.append(f'{kind}:{name}: {msg}')  # noqa: E731
        if name in seen:
            say('duplicate entry name')
        seen.add(name)
        if st not in STATUSES[kind]:
            say(f'unknown status {st!r} (allowed: {sorted(STATUSES[kind])})')
            continue
        if not isinstance(e.get('start_id'), int) or not isinstance(e.get('end_id'), int) \
                or e['start_id'] > e['end_id']:
            say('start_id/end_id must be integers with start_id <= end_id')
        if g3 is None:
            if kind == 'structure':
                say('every structure entry is G3-governed and needs a g3 block')
            elif st == 'held':
                say('status held is only for G3-governed entries (no g3 block)')
            elif st == 'approved' and name not in OWNER_APPROVED[kind]:
                say('approved without a g3 block, and not an owner-approved entry '
                    f'({sorted(OWNER_APPROVED[kind])}); a G3 ruling is required')
            continue
        if not isinstance(g3, dict) or not isinstance(g3.get('item'), str) or not g3['item'].strip():
            say('g3 block must be an object with a non-empty item')
            continue
        if st in ('proposed', 'held'):
            filled = [k for k in RULING if g3.get(k) not in (None, '')]
            if filled:
                say(f'status {st} but the ruling fields {filled} are filled: record the ruling by '
                    'moving the status to approved/rejected, or clear them')
            continue
        if st == 'keep':
            continue
        # approved / rejected: the ruling must be complete and bound to this exact entry
        dec = g3.get('decision')
        if dec not in DECISION_FOR[st]:
            say(f'status {st} needs g3.decision in {sorted(DECISION_FOR[st])}, not {dec!r}')
        rev = g3.get('reviewer')
        if not isinstance(rev, str) or not rev.strip():
            say('g3.reviewer is required')
        elif rev.strip() == FIXTURE_REVIEWER and not allow_fixture:
            say('g3.reviewer is the test-fixture reviewer: never valid in a real ledger')
        d = g3.get('date')
        if not isinstance(d, str) or not ISO_DATE.match(d):
            say(f'g3.date must be YYYY-MM-DD, not {d!r}')
        else:
            try:
                if datetime.date.fromisoformat(d) > today:
                    say(f'g3.date {d} is in the future')
            except ValueError:
                say(f'g3.date {d!r} is not a real date')
        if g3.get('scope') != g3['item']:
            say(f"g3.scope {g3.get('scope')!r} must equal g3.item {g3['item']!r}")
        ev = g3.get('evidence')
        if not isinstance(ev, str) or not ev.startswith(PACK) or '..' in ev \
                or not os.path.isfile(os.path.join(root, ev)):
            say(f'g3.evidence must be an existing file under {PACK}, not {ev!r}')
        if g3.get('entry_sha256') != entry_sha256(e):
            say('g3.entry_sha256 does not match the entry: the ruling was recorded for a different '
                f'version of it (expected {entry_sha256(e)})')
    return out


def check(entries, kind, **kw):
    """Raise GateError unless the entries are valid; return the ones a build applies."""
    bad = problems(entries, kind, **kw)
    if bad:
        raise GateError('ledger refused by the G3 gate:\n  ' + '\n  '.join(bad))
    return [e for e in entries if e['status'] in APPLIED]


def load(kind, path=None):
    """Read and validate a ledger. A missing ledger is an error, not an empty one."""
    path = path or LEDGERS[kind]
    entries = read(path)
    check(entries, kind)
    return entries


def outstanding(entries):
    """G3-governed entries without a recorded ruling (held, or proposed with a g3 block)."""
    return [e for e in entries if e.get('g3') and e.get('status') in ('held', 'proposed')]


def main(argv):
    if argv[:1] == ['--hash'] and len(argv) == 2:
        hits = [e for k in LEDGERS for e in read(LEDGERS[k]) if e.get('entry') == argv[1]]
        if len(hits) != 1:
            print(f'no single ledger entry named {argv[1]!r}')
            return 2
        print(entry_sha256(hits[0]))
        return 0
    release = '--release-check' in argv
    errors, pending, rows = [], [], []
    for kind, path in LEDGERS.items():
        entries = read(path)
        errors += problems(entries, kind)
        for e in entries:
            if e.get('g3'):
                g = e['g3']
                rows.append((g.get('item'), kind, e['entry'], e['status'], g.get('decision') or '-',
                             g.get('reviewer') or '-', g.get('date') or '-'))
        pending += [(kind, e['entry'], e['status']) for e in outstanding(entries)]
    print('G3-governed ledger entries:')
    print(f"  {'item':<16} {'ledger':<11} {'entry':<28} {'status':<9} {'decision':<9} {'reviewer':<12} date")
    for r in rows:
        print(f'  {r[0]:<16} {r[1]:<11} {r[2]:<28} {r[3]:<9} {r[4]:<9} {r[5]:<12} {r[6]}')
    for msg in errors:
        print(f'::error::{msg}')
    if errors:
        print(f'G3 gate: FAIL — {len(errors)} invalid ledger entr{"y" if len(errors) == 1 else "ies"}')
        return 1
    if release and pending:
        for kind, name, st in pending:
            print(f'::error::{kind}:{name} is {st}: no G3 ruling is recorded, so this dataset is not '
                  'releasable')
        print(f'G3 release check: FAIL — {len(pending)} G3 entr{"y" if len(pending) == 1 else "ies"} '
              'without a recorded scholarly ruling. A green build is not a G3 approval.')
        return 1
    print('G3 gate: ledgers valid' + (' and every G3 ruling recorded' if release else
                                      f' ({len(pending)} G3 entries await a ruling)'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
