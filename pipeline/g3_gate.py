# -*- coding: utf-8 -*-
"""The G3 approval gate for the editorial ledgers (attribution_ledger.json, structure_ledger.json).

A G3 decision is a Gurbani scholar's ruling. A green build, an engineer's approval and an agent's
recommendation are none of them that ruling. This module is the one place that decides which ledger
entries a build may apply; attribution.py, structure.py, the tests and CI all call it.

  python3 pipeline/g3_gate.py                    validate both ledgers and the committed corpus
  python3 pipeline/g3_gate.py --release-check    also fail while any G3 ruling is outstanding
  python3 pipeline/g3_gate.py --hash ENTRY       print an entry's entry_sha256 (for recording a ruling)
  python3 base/pipeline/g3_gate.py --release-check --tree pr
                                                 judge another checkout's ledgers, corpus and rulings
                                                 with THIS copy's code and trust anchors (CI runs the
                                                 base branch's gate on a pull request's tree)

Statuses (a closed set; anything else fails the build):
  proposed   recorded for review; never applied
  held       a G3 change applied ONLY so a held draft PR can prove its exact effect; its `g3`
             ruling is still blank. Never releasable: --release-check fails while one exists.
  approved   applied. A G3 entry needs a complete ruling (RULING): decision approve|change, a reviewer
             of record (REVIEWERS), a date from MIN_RULING_DATE to today, scope equal to g3.item, the
             reviewer's own reply as a regular, non-symlinked file under RULINGS with its sha256, and
             entry_sha256 -- the hash of what the entry does (ACTING fields), so a ruling never carries
             over to an entry whose range or values were edited after it. The reply must carry the
             reviewer's own SSH signature (<reply>.sig, namespace SIG_NAMESPACE) that verifies against his
             key in SIGNERS: editing a ledger, or committing a reply file, cannot forge a ruling.
             A RELAYED ruling (the reviewer replied on a channel that cannot carry his signature, e.g.
             WhatsApp from a phone) names g3.relayed_by, a relayer of record (RELAYERS), and g3.channel
             (CHANNELS); the evidence is then the unedited channel export and the signature is the
             RELAYER's, attesting that it is the reviewer's reply as received. It is recorded and shown
             as relayed, never as the reviewer's own signature.
  rejected   never applied; a G3 rejection records the same complete ruling, decision reject.
  keep       attribution only, never applied, and never for a G3 item (a G3 item is approved or
             rejected by a ruling, or stays proposed/held).

Ledger-wide rules (enforced wherever a ledger is loaded, and by the CLI):
  - every entry in G3_ENTRIES exists, carries a `g3` block naming its item, and no other entry does --
    a G3 item cannot be renamed, stripped of its block or dropped without a code change here;
  - an `approved` attribution entry without `g3` is one of OWNER_APPROVED, decided before G3 existed,
    and still has exactly the content (entry_sha256) it was approved with;
  - the committed corpus shows every applied entry's `to` and every unapplied G3 entry's `from`.

Trust anchors -- G3_ENTRIES, OWNER_APPROVED, REVIEWERS, RELAYERS and the SIGNERS key file -- are read from
the copy of the repository this module lives in, never from a --tree under judgement.
"""
import datetime, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGERS = {'attribution': os.path.join(ROOT, 'pipeline', 'attribution_ledger.json'),
           'structure': os.path.join(ROOT, 'pipeline', 'structure_ledger.json')}
CORPUS = os.path.join(ROOT, 'corpus', 'sggs.jsonl')
PACK = 'validation/attribution-g3-review/'
RULINGS = PACK + 'rulings/'

STATUSES = {'attribution': {'proposed', 'held', 'approved', 'rejected', 'keep'},
            'structure': {'proposed', 'held', 'approved', 'rejected'}}
APPLIED = {'approved', 'held'}
DECISION_FOR = {'approved': {'approve', 'change'}, 'rejected': {'reject'}}
ACTING = ('entry', 'kind', 'start_id', 'end_id', 'from', 'to')
RULING = ('decision', 'reviewer', 'date', 'scope', 'evidence', 'evidence_sha256', 'entry_sha256')
RELAY = ('relayed_by', 'channel')                      # optional; both or neither

# The G3 items of dataset 1.3.0 (gurbani-soul-ios docs/review/g3-1.4.9, section 6; Ang 323 added by
# pull request #17). Adding, renaming or removing one is a reviewed code change.
G3_ENTRIES = {
    'attribution': {'surdas-line': 'A-07', 'bhagat-run-heading-ang524': 'A-11 / Ang 524',
                    'bhagat-run-heading-ang323': 'A-11 / Ang 323'},
    'structure': {'section-salok-kabir': 'A-08', 'section-salok-farid': 'A-08',
                  'ang695-sain-opens': 'A-10', 'ang695-pipa-opens': 'A-10', 'ang695-dhanna-opens': 'A-10'},
}
# Approved by the owner before G3 existed (Lineage v2, 2026-10-23), pinned to their content.
OWNER_APPROVED = {
    'attribution': {'japji': '805ba0c09d70009ce5f6a3b146f671f5222cd959b5e199d4b29245c31f8ffba4',
                    'sadu': 'f22cc92b19f2acbf34bdf797abea015dbac31d06d8500edac91ae19ae88b3657'},
    'structure': {},
}
# The G3 reviewer of record and his signing principal in SIGNERS. Adding a reviewer, or registering
# his public key in SIGNERS, is a reviewed change to the base branch.
PRINCIPALS = {'Kanwaljit Singh': 'kanwaljit-singh'}
REVIEWERS = set(PRINCIPALS)
SIGNERS = os.path.join(ROOT, PACK, 'allowed_signers')   # ssh-keygen allowed_signers format
SIG_NAMESPACE = 'sggs-g3-ruling'
# Who may relay a reviewer's unsigned reply, and their signing principal in SIGNERS. The owner chose
# this path on 2026-10-28 because the reviewer replies by WhatsApp from a phone. A relayed ruling rests
# on the relayer's attestation, not the reviewer's key (validation/attribution-g3-review/RISKS.md G-14).
RELAYERS = {'Sam Kalaliya': 'sam-kalaliya'}
CHANNELS = {'whatsapp'}
# No G3 ruling on these entries can predate the held pull request that proposed them.
MIN_RULING_DATE = datetime.date(2026, 10, 26)
# Positive tests use this reviewer in temporary fixtures; the committed ledgers may never carry it.
FIXTURE_REVIEWER = 'TEST-FIXTURE-NOT-A-REVIEWER'
FIXTURE_PRINCIPAL = 'test-fixture-not-a-reviewer'
FIXTURE_RELAYER = 'TEST-FIXTURE-NOT-A-RELAYER'
FIXTURE_RELAYER_PRINCIPAL = 'test-fixture-not-a-relayer'
REQUIRED = {'attribution': ('entry', 'start_id', 'end_id', 'from', 'to', 'status'),
            'structure': ('entry', 'kind', 'start_id', 'end_id', 'to', 'status')}
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class GateError(Exception):
    pass


def read(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)['entries']


def entry_sha256(e):
    """Hash of what an entry does: its name, kind, range and values (ACTING), never its prose."""
    body = {k: e[k] for k in ACTING if k in e}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 16), b''):
            h.update(ch)
    return h.hexdigest()


def _today():
    # UTC date + 1: a ruling dated today anywhere east of UTC is not "in the future"
    return datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=1)


def _evidence_problem(ev, root):
    if not isinstance(ev, str) or not ev.startswith(RULINGS) or '..' in ev.split('/') or '\\' in ev:
        return f'g3.evidence must be the reviewer\'s reply under {RULINGS}, not {ev!r}'
    path = os.path.join(root, ev)
    rdir = os.path.realpath(os.path.join(root, RULINGS))
    if os.path.islink(path) or not os.path.isfile(path) or \
            os.path.dirname(os.path.realpath(path)) != rdir:
        return f'g3.evidence {ev!r} must be a regular file (not a symlink) directly in {RULINGS}'
    return None


def _signature_problem(path, principal, signers):
    """None if <path>.sig is the principal's SSH signature over path, verified against signers."""
    sig = path + '.sig'
    if os.path.islink(sig) or not os.path.isfile(sig):
        return f'the ruling is not signed: {os.path.basename(sig)} must sit next to it, a regular file'
    if not os.path.isfile(signers):
        return (f'no reviewer key is registered ({os.path.relpath(signers, ROOT)} is missing), so no ruling '
                'can be verified')
    try:
        with open(path, 'rb') as f:
            r = subprocess.run(['ssh-keygen', '-Y', 'verify', '-f', signers, '-I', principal,
                                '-n', SIG_NAMESPACE, '-s', sig], stdin=f, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as ex:
        return f'the ruling signature could not be checked ({type(ex).__name__}): fail closed'
    if r.returncode != 0:
        return f'the ruling signature does not verify as {principal!r} against the registered key'
    return None


def _signer(g3, rev, allow_fixture):
    """(principal whose signature the ruling must carry, None) or (None, why it has none)."""
    relayer, channel = g3.get('relayed_by'), g3.get('channel')
    if relayer in (None, '') and channel in (None, ''):
        p = FIXTURE_PRINCIPAL if (allow_fixture and rev == FIXTURE_REVIEWER) else PRINCIPALS.get(rev)
        return (p, None) if p else (None, 'no signing principal for this reviewer')
    if channel not in CHANNELS:
        return None, f'a relayed ruling needs g3.channel in {sorted(CHANNELS)}, not {channel!r}'
    if allow_fixture and relayer == FIXTURE_RELAYER:
        return FIXTURE_RELAYER_PRINCIPAL, None
    if relayer not in RELAYERS:
        return None, f'g3.relayed_by {relayer!r} is not a relayer of record ({sorted(RELAYERS)})'
    return RELAYERS[relayer], None


def problems(entries, kind, root=ROOT, today=None, allow_fixture=False, signers=SIGNERS):
    """Every reason these entries may not be built, entry by entry (empty = valid)."""
    today = today or _today()
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
        # what an applied or G3 entry acts with must be there; a proposed or kept note may leave its
        # values open (raagmala, bhatt-splits, ...), but still names itself and its line range
        need = REQUIRED[kind] if (st in APPLIED or g3 is not None) else ('entry', 'start_id', 'end_id', 'status')
        missing = [k for k in need if e.get(k) in (None, '')]
        if kind == 'attribution' and 'from' in missing and e.get('from', 0) is None:
            missing.remove('from')                 # an unattributed line legitimately comes `from` null
        if missing:
            say(f'missing required field(s) {missing}')
            continue
        if type(e.get('start_id')) is not int or type(e.get('end_id')) is not int \
                or e['start_id'] > e['end_id']:
            say('start_id/end_id must be integers with start_id <= end_id')
        if g3 is None:
            if kind == 'structure':
                say('every structure entry is G3-governed and needs a g3 block')
            elif name in G3_ENTRIES[kind]:
                say(f'is G3 item {G3_ENTRIES[kind][name]} and needs its g3 block')
            elif st == 'held':
                say('status held is only for G3-governed entries (no g3 block)')
            elif st == 'approved' and name not in OWNER_APPROVED[kind]:
                say('approved without a g3 block, and not an owner-approved entry '
                    f'({sorted(OWNER_APPROVED[kind])}); a G3 ruling is required')
            continue
        if not isinstance(g3, dict) or not isinstance(g3.get('item'), str) or not g3['item'].strip():
            say('g3 block must be an object with a non-empty item')
            continue
        if st == 'keep':
            say('a G3 item cannot be `keep`: it is approved or rejected by a ruling, or stays proposed/held')
            continue
        if st in ('proposed', 'held'):
            filled = [k for k in RULING + RELAY if g3.get(k) not in (None, '')]
            if filled:
                say(f'status {st} but the ruling fields {filled} are filled: record the ruling by '
                    'moving the status to approved/rejected, or clear them')
            continue
        # approved / rejected: the ruling must be complete, from the reviewer, and bound to this entry
        dec = g3.get('decision')
        if dec not in DECISION_FOR[st]:
            say(f'status {st} needs g3.decision in {sorted(DECISION_FOR[st])}, not {dec!r}')
        rev = g3.get('reviewer')
        if not (rev in REVIEWERS or (allow_fixture and rev == FIXTURE_REVIEWER)):
            say(f'g3.reviewer {rev!r} is not a G3 reviewer of record ({sorted(REVIEWERS)})')
        d = g3.get('date')
        if not isinstance(d, str) or not ISO_DATE.fullmatch(d):
            say(f'g3.date must be YYYY-MM-DD, not {d!r}')
        else:
            try:
                dd = datetime.date.fromisoformat(d)
                if dd > today:
                    say(f'g3.date {d} is in the future')
                elif dd < MIN_RULING_DATE:
                    say(f'g3.date {d} predates the held pull request ({MIN_RULING_DATE})')
            except ValueError:
                say(f'g3.date {d!r} is not a real date')
        if g3.get('scope') != g3['item']:
            say(f"g3.scope {g3.get('scope')!r} must equal g3.item {g3['item']!r}")
        why = _evidence_problem(g3.get('evidence'), root)
        if why:
            say(why)
        elif g3.get('evidence_sha256') != file_sha256(os.path.join(root, g3['evidence'])):
            say('g3.evidence_sha256 does not match the ruling file')
        else:
            principal, why = _signer(g3, rev, allow_fixture)
            why = why or _signature_problem(os.path.join(root, g3['evidence']), principal, signers)
            if why:
                say(why)
        if g3.get('entry_sha256') != entry_sha256(e):
            say('g3.entry_sha256 does not match the entry: the ruling was recorded for a different '
                f'version of it (expected {entry_sha256(e)})')
    return out


def ledger_problems(entries, kind):
    """Rules over a whole ledger: the G3 registry and the owner-approved pins."""
    out, names = [], {e.get('entry'): e for e in entries}
    for name, item in G3_ENTRIES[kind].items():
        e = names.get(name)
        if e is None:
            out.append(f'{kind}:{name}: G3 item {item} is missing from the ledger')
        elif (e.get('g3') or {}).get('item') != item:
            out.append(f"{kind}:{name}: must carry g3.item {item!r}, not {(e.get('g3') or {}).get('item')!r}")
    for e in entries:
        name = e.get('entry')
        if e.get('g3') and name not in G3_ENTRIES[kind]:
            out.append(f'{kind}:{name}: has a g3 block but is not a registered G3 item (G3_ENTRIES)')
        if name in OWNER_APPROVED[kind] and e.get('status') == 'approved' and not e.get('g3') \
                and entry_sha256(e) != OWNER_APPROVED[kind][name]:
            out.append(f'{kind}:{name}: owner-approved entry was edited after its approval '
                       f'(entry_sha256 {entry_sha256(e)})')
    return out


def check(entries, kind, **kw):
    """Raise GateError unless the entries are valid; return the ones a build applies."""
    bad = problems(entries, kind, **kw)
    if bad:
        raise GateError('ledger refused by the G3 gate:\n  ' + '\n  '.join(bad))
    return [e for e in entries if e['status'] in APPLIED]


def load(kind, path=None):
    """Read and validate a whole ledger. A missing ledger is an error, not an empty one."""
    entries = read(path or LEDGERS[kind])
    bad = ledger_problems(entries, kind)
    if bad:
        raise GateError('ledger refused by the G3 gate:\n  ' + '\n  '.join(bad))
    check(entries, kind)
    return entries


def outstanding(entries):
    """G3-governed entries without a recorded ruling (held, or proposed with a g3 block)."""
    return [e for e in entries if e.get('g3') and e.get('status') in ('held', 'proposed')]


def artifact_problems(ledgers, corpus_path):
    """The committed corpus must be what the statuses say: an applied entry's `to` on every line it
    covers, an unapplied G3 entry's `from` (owner-approved and G3 entries; others are informational)."""
    by_id = {}
    with open(corpus_path, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            by_id[r['id']] = r
    out = []
    for kind, entries in ledgers.items():
        for e in entries:
            if not (e.get('g3') or e.get('entry') in OWNER_APPROVED[kind]):
                continue
            field = 'author' if kind == 'attribution' else ('section' if e['kind'] == 'section' else 'comp_id')
            want = e['to'] if e['status'] in APPLIED else e['from']
            got = {by_id[i][field] for i in range(e['start_id'], e['end_id'] + 1) if i in by_id}
            if got != {want}:
                out.append(f"{kind}:{e['entry']}: status {e['status']} means {field} {want!r} on ids "
                           f"{e['start_id']}-{e['end_id']}, but the committed corpus has {sorted(map(str, got))}")
    return out


def main(argv, ledger_paths=None, root=ROOT, corpus=None):
    if '--tree' in argv:
        # judge another checkout's data with this copy's code and anchors (see the module docstring)
        i = argv.index('--tree')
        if i + 1 >= len(argv):
            print('--tree needs a directory')
            return 2
        tree = os.path.realpath(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
        ledger_paths = {k: os.path.join(tree, os.path.relpath(p, ROOT)) for k, p in LEDGERS.items()}
        root, corpus = tree, os.path.join(tree, os.path.relpath(CORPUS, ROOT))
    if argv[:1] == ['--hash'] and len(argv) == 2:
        hits = [e for k in LEDGERS for e in read(LEDGERS[k]) if e.get('entry') == argv[1]]
        if len(hits) != 1:
            print(f'no single ledger entry named {argv[1]!r}')
            return 2
        print(entry_sha256(hits[0]))
        return 0
    release = '--release-check' in argv
    paths = ledger_paths or LEDGERS
    ledgers = {kind: read(p) for kind, p in paths.items()}
    errors, pending, rows = [], [], []
    for kind, entries in ledgers.items():
        # signers is always this copy's key file, never one inside a --tree under judgement
        errors += ledger_problems(entries, kind) + problems(entries, kind, root=root, signers=SIGNERS)
        for e in entries:
            if e.get('g3'):
                g = e['g3']
                who = g.get('reviewer') or '-'
                if g.get('relayed_by'):
                    who += f" (relayed by {g['relayed_by']} via {g.get('channel')}, not signed by the reviewer)"
                rows.append((g.get('item'), kind, e['entry'], e['status'], g.get('decision') or '-',
                             who, g.get('date') or '-'))
        pending += [(kind, e['entry'], e['status']) for e in outstanding(entries)]
    if not errors:
        errors += artifact_problems(ledgers, corpus or CORPUS)
    print('G3-governed ledger entries:')
    print(f"  {'item':<16} {'ledger':<11} {'entry':<28} {'status':<9} {'decision':<9} {'date':<10} reviewer")
    for r in rows:
        print(f'  {r[0]:<16} {r[1]:<11} {r[2]:<28} {r[3]:<9} {r[4]:<9} {r[6]:<10} {r[5]}')
    for msg in errors:
        print(f'::error::{msg}')
    if errors:
        print(f'G3 gate: FAIL — {len(errors)} problem{"" if len(errors) == 1 else "s"} in the ledgers or '
              'the committed corpus')
        return 1
    if release and pending:
        for kind, name, st in pending:
            print(f'::error::{kind}:{name} is {st}: no G3 ruling is recorded, so this dataset is not '
                  'releasable')
        held = sum(st == 'held' for _, _, st in pending)
        print(f'G3 release check: FAIL — {len(pending)} G3 entr{"y" if len(pending) == 1 else "ies"} '
              f'without a recorded scholarly ruling ({held} held: applied only in this draft build; '
              f'{len(pending) - held} proposed: not applied). A green build is not a G3 approval.')
        return 1
    print('G3 gate: ledgers and corpus agree' + (' and every G3 ruling is recorded' if release else
                                                f' ({len(pending)} G3 entries await a ruling)'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
