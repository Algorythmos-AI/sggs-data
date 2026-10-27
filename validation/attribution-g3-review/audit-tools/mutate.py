import subprocess, sys, os, re
ROOT = sys.argv[1]
G = os.path.join(ROOT, 'pipeline', 'g3_gate.py')
orig = open(G, encoding='utf-8').read()
MUTANTS = [
 ('reviewer check removed', "        if not isinstance(rev, str) or not rev.strip():\n            say('g3.reviewer is required')\n        elif", "        if False:\n            pass\n        elif"),
 ('future-date check removed', "                if datetime.date.fromisoformat(d) > today:", "                if False:"),
 ('decision check removed', "        if dec not in DECISION_FOR[st]:", "        if False:"),
 ('scope check removed', "        if g3.get('scope') != g3['item']:", "        if False:"),
 ('evidence check removed', "        if not isinstance(ev, str) or not ev.startswith(PACK) or '..' in ev \\\n                or not os.path.isfile(os.path.join(root, ev)):", "        if False:"),
 ('entry_sha256 binding removed', "        if g3.get('entry_sha256') != entry_sha256(e):", "        if False:"),
 ('fixture-reviewer refusal removed', "        elif rev.strip() == FIXTURE_REVIEWER and not allow_fixture:", "        elif False:"),
 ('unknown status accepted', "        if st not in STATUSES[kind]:", "        if False:"),
 ('owner allowlist bypassed', "            elif st == 'approved' and name not in OWNER_APPROVED[kind]:", "            elif False:"),
 ('held with filled ruling accepted', "            if filled:", "            if False:"),
 ('held counted as released', "    return [e for e in entries if e.get('g3') and e.get('status') in ('held', 'proposed')]", "    return [e for e in entries if e.get('g3') and e.get('status') in ('proposed',)]"),
 ('APPLIED includes proposed', "APPLIED = {'approved', 'held'}", "APPLIED = {'approved', 'held', 'proposed'}"),
 ('structure needs no g3', "            if kind == 'structure':\n                say(", "            if False:\n                say("),
]
res = []
for name, a, b in MUTANTS:
    assert orig.count(a) == 1, name
    open(G, 'w', encoding='utf-8').write(orig.replace(a, b))
    p = subprocess.run([sys.executable, '-m', 'unittest', 'tests.test_g3_gate', 'tests.test_structure', 'tests.test_attribution'],
                       cwd=os.path.join(ROOT, 'pipeline'), capture_output=True, text=True)
    m = re.search(r'FAILED \((.*)\)', p.stderr)
    res.append((name, 'KILLED' if p.returncode else 'SURVIVED', m.group(1) if m else 'all pass'))
open(G, 'w', encoding='utf-8').write(orig)
for r in res: print(f'{r[1]:<9} {r[0]:<36} {r[2]}')
