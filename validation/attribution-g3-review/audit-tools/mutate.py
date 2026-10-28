# -*- coding: utf-8 -*-
"""Mutation and negative tests for the G3 gate, the pack checks and the scripture gates.

    python3 mutate.py <repo-root> [<scratch-dir>]

Clones the repo (APFS copy-on-write where available) into a scratch directory, applies each deliberate
break in turn, runs the relevant tests, and reports KILLED (a test failed, as it should) or SURVIVED
(no test noticed: a gap). The repo itself is never modified. Prints one line per mutant; exits 1 if any
mutant survived.
"""
import os, re, shutil, sqlite3, subprocess, sys, tempfile

REPO = os.path.abspath(sys.argv[1])
WORK = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else tempfile.mkdtemp(prefix='g3-mutate-')
COPY = os.path.join(WORK, 'repo')
TESTS = ['tests.test_g3_gate', 'tests.test_g3_pack', 'tests.test_structure', 'tests.test_attribution']
G, ATT, STR = 'pipeline/g3_gate.py', 'pipeline/attribution.py', 'pipeline/structure.py'
AL = 'pipeline/attribution_ledger.json'
PACK = 'validation/attribution-g3-review/'

MUTANTS = [  # (number, what is broken, file, exact text, replacement)
    (1, 'reviewer-of-record check removed', G,
     "        if not (rev in REVIEWERS or (allow_fixture and rev == FIXTURE_REVIEWER)):", "        if False:"),
    (2, 'future-date check removed', G, "                if dd > today:", "                if False:"),
    (3, 'minimum-date check removed', G, "                elif dd < MIN_RULING_DATE:", "                elif False:"),
    (4, 'decision check removed', G, "        if dec not in DECISION_FOR[st]:", "        if False:"),
    (5, 'scope check removed', G, "        if g3.get('scope') != g3['item']:", "        if False:"),
    (6, 'evidence location check removed', G,
     "        why = _evidence_problem(g3.get('evidence'), root)\n        if why:",
     "        why = None\n        if why:"),
    (7, 'symlink refusal removed', G, "    if os.path.islink(path) or not os.path.isfile(path) or \\",
     "    if not os.path.isfile(path) or \\"),
    (8, 'ruling-file hash check removed', G, "        elif g3.get('evidence_sha256') != file_sha256(",
     "        elif False and g3.get('evidence_sha256') != file_sha256("),
    (9, 'entry_sha256 binding removed', G, "        if g3.get('entry_sha256') != entry_sha256(e):", "        if False:"),
    (10, 'unknown statuses accepted', G, "        if st not in STATUSES[kind]:", "        if False:"),
    (11, 'owner-approval allowlist bypassed', G,
     "            elif st == 'approved' and name not in OWNER_APPROVED[kind]:", "            elif False:"),
    (12, 'G3 item may be `keep`', G, "        if st == 'keep':\n            say('a G3 item",
     "        if False:\n            say('a G3 item"),
    (13, 'held/proposed with a filled ruling accepted', G, "            if filled:", "            if False:"),
    (14, 'held not counted as outstanding', G,
     "e.get('status') in ('held', 'proposed')]", "e.get('status') in ('proposed',)]"),
    (15, '`proposed` treated as applied', G, "APPLIED = {'approved', 'held'}", "APPLIED = {'approved', 'held', 'proposed'}"),
    (16, 'structure entries allowed without g3', G, "            if kind == 'structure':\n                say(",
     "            if False:\n                say("),
    (17, 'registered G3 entry may lose its g3 block', G, "            elif name in G3_ENTRIES[kind]:",
     "            elif False:"),
    (18, 'registered G3 entry may be missing', G, "        if e is None:\n            out.append(f'{kind}:{name}: G3 item",
     "        if False:\n            out.append(f'{kind}:{name}: G3 item"),
    (19, 'owner-approved pin not checked', G, "                and entry_sha256(e) != OWNER_APPROVED[kind][name]:",
     "                and False:"),
    (20, 'unregistered g3 entries accepted', G, "        if e.get('g3') and name not in G3_ENTRIES[kind]:",
     "        if False:"),
    (21, 'release check skips the corpus', G, "        errors += artifact_problems(ledgers, corpus or CORPUS)",
     "        pass"),
    (22, 'non-integer ids accepted', G, "        if type(e.get('start_id')) is not int or type(e.get('end_id')) is not int \\\n                or e['start_id'] > e['end_id']:",
     "        if False:"),
    (23, 'rule E bypasses the gate', ATT, "g3_gate.check(ledger or [], 'attribution', **(gate or {}))",
     "[e for e in (ledger or []) if e.get('status') in ('approved', 'held')]"),
    (24, 'structure pass bypasses the gate', STR, "g3_gate.check(ledger, 'structure', **(gate or {}))",
     "[e for e in ledger if e.get('status') in ('approved', 'held')]"),
    (25, 'attribution.load_ledger unvalidated', ATT, "    return g3_gate.load('attribution', path)",
     "    return g3_gate.read(path)"),
    (26, 'structure.load_ledger unvalidated', STR, "    return g3_gate.load('structure', path)",
     "    return g3_gate.read(path)"),
    (27, 'held entry flipped to proposed, corpus not rebuilt', AL, '"status": "held"', '"status": "proposed"'),
    (28, 'G3 entry edited without regenerating the pack', AL, '"from": "Bhagat Namdev Ji"',
     '"from": "Bhagat Namdev Ji (edited)"'),
    (29, 'DB rebuilt without regenerating the pack', 'MANIFEST.json', '"db_sha256": "003cae57', '"db_sha256": "003cae58'),
    (30, 'a pack quote misquoted by one matra', PACK + 'DECISIONS.md',
     '`ਛਾਡਿ ਮਨ ਹਰਿ ਬਿਮੁਖਨ ਕੋ ਸੰਗੁ ॥` *(line 53935)*', '`ਛਾਡਿ ਮਨ ਹਰਿ ਬਿਮੁਖਨ ਕੋ ਸੰਗ ॥` *(line 53935)*'),
    (31, 'README.md hand-edited (stale against its template)', PACK + 'README.md',
     '# Held for G3', '# Held for G3 (hand edit)'),
    # added 2026-10-28 (signed rulings, base-branch gate, required fields, release summary)
    (32, 'ruling signature not checked', G, "            if why:\n                say(why)\n        if g3.get('entry_sha256')",
     "            if False:\n                say(why)\n        if g3.get('entry_sha256')"),
    (33, 'signature verifier ignores its exit code', G, "    if r.returncode != 0:", "    if False:"),
    (34, 'missing signer file accepted', G, "    if not os.path.isfile(signers):\n        return (",
     "    if False:\n        return ("),
    (35, '--tree reads its keys from the tree under judgement', G,
     "problems(entries, kind, root=root, signers=SIGNERS)",
     "problems(entries, kind, root=root, signers=os.path.join(root, PACK, 'allowed_signers'))"),
    (36, 'required-field check removed', G, "        if missing:\n            say(", "        if False:\n            say("),
    (37, 'release summary hides held vs proposed', G, "without a recorded scholarly ruling ({held} held",
     "without a recorded scholarly ruling. ({held} held"),
    (38, 'base-branch workflow judges with the PR\'s own gate', '.github/workflows/g3-gate.yml',
     'python3 -I base/pipeline/g3_gate.py', 'python3 -I pr/pipeline/g3_gate.py'),
    (39, 'base-branch workflow switched to pull_request', '.github/workflows/g3-gate.yml',
     '  pull_request_target:', '  pull_request:'),
    (40, 'any relayer accepted', G, "    if relayer not in RELAYERS:", "    if False:"),
    (41, 'any relay channel accepted', G, "    if channel not in CHANNELS:", "    if False:"),
    (42, 'relayed ruling verified as the reviewer, not the relayer', G,
     "    return RELAYERS[relayer], None", "    return PRINCIPALS.get(rev), None"),
    (43, 'relay fields allowed on an unruled entry', G,
     "for k in RULING + RELAY if g3.get(k)", "for k in RULING if g3.get(k)"),
    (44, 'gate report hides that a ruling was relayed', G,
     "                if g.get('relayed_by'):", "                if False:"),
]


def run_tests():
    p = subprocess.run([sys.executable, '-m', 'unittest', *TESTS], cwd=os.path.join(COPY, 'pipeline'),
                       capture_output=True, text=True)
    m = re.search(r'FAILED \((.*)\)', p.stderr)
    return p.returncode != 0, (m.group(1) if m else 'all pass')


def main():
    shutil.rmtree(COPY, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    if sys.platform == 'darwin':
        subprocess.run(['cp', '-Rc', REPO, COPY], check=False)
    if not os.path.isdir(COPY):
        shutil.copytree(REPO, COPY, symlinks=True)
    failing, why = run_tests()
    print('baseline: ' + ('FAILING, fix before mutating: ' + why if failing else 'tests pass'))
    survived = 0
    for n, name, rel, old, new in MUTANTS:
        p = os.path.join(COPY, rel)
        with open(p, encoding='utf-8') as f:
            orig = f.read()
        if old not in orig:
            print(f'{n:>2} NOT APPLIED  {name}: text not found')
            survived += 1
            continue
        with open(p, 'w', encoding='utf-8') as f:
            f.write(orig.replace(old, new, 1))
        try:
            killed, why = run_tests()
        finally:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(orig)
        survived += not killed
        print(f'{n:>2} {"KILLED  " if killed else "SURVIVED"}  {name:<52} {why}')
    # N1: one scripture code point flipped in a DB copy must fail both scripture gates
    db = os.path.join(WORK, 'flip.sqlite')
    shutil.copy(os.path.join(REPO, 'db', 'sggs.sqlite'), db)
    c = sqlite3.connect(db)
    g = c.execute('SELECT gurmukhi FROM lines WHERE id = 30081').fetchone()[0]
    c.execute('UPDATE lines SET gurmukhi = ? WHERE id = 30081', (g.replace('ਸ', 'ਸ਼', 1),))
    c.commit()
    c.close()
    r1 = subprocess.run([sys.executable, 'scripts/data/diff_scripture.py', 'db/sggs.sqlite', db], cwd=REPO,
                        capture_output=True, text=True).returncode
    r2 = subprocess.run([sys.executable, 'pipeline/sggs_integrity.py', db, '--compare',
                         'audit/dataset-fingerprint.json'], cwd=REPO, capture_output=True, text=True).returncode
    print(f'N1 {"KILLED  " if r1 and r2 else "SURVIVED"}  one scripture code point flipped (U+0A38->U+0A36, '
          f'line 30081)   diff_scripture exit {r1}, fingerprint exit {r2}')
    survived += not (r1 and r2)
    print(f'{survived} survived')
    return 1 if survived else 0


if __name__ == '__main__':
    sys.exit(main())
