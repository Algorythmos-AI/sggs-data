# -*- coding: utf-8 -*-
"""Author attribution pass -- changes the `author` field ONLY (scripture, comp_id, line_no,
is_header and markers are never touched; verify_attribution.py proves it).

Why: the header-driven context in build_corpus carries an author forward until the next
author-bearing header. Three print conventions defeat that:
  1. inflected Bhagat names in titles   ਆਸਾ ਬਾਣੀ ਭਗਤ ਧੰਨੇ ਜੀ ਕੀ   (BHAGATS knows only ਧੰਨਾ)
  2. bare-name rubric lines              ਪੀਪਾ ॥ / ਧੰਨਾ ॥ / ਸ੍ਰੀ ਸੈਣੁ ॥  (no label word, so no header)
  3. per-salok ਮਹਲਾ labels inside a Bhagat's salok block, which "stuck" to every later salok.

Three rules, applied in order, each recorded with the evidence that fired:
  A  bhagat-shabad  -- a shabad (a run closed by a ॥N॥M॥ count line, Angs < 1353) whose closing
     couplet signs Bhagat X AND whose rubric names X (its own bare-name line, its own title, or
     the nearest Bhagat-naming title in the same raag). Two independent signals, or no change.
     A shabad opened by its own ਮਹਲਾ/ਮਃ heading is never touched (the Guru's heading wins), and
     a name in the body of a verse is never evidence.
  B  salok-scope    -- inside a Bhagat salok block (ਸਲੋਕ ਭਗਤ ਕਬੀਰ ਜੀਉ ਕੇ, ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ) a ਮਹਲਾ/ਮਃ
     label covers its own salok only (through the next line closing with a number); then the
     block's author resumes.
  C  ledger         -- explicit, reviewed decisions (attribution_decisions.json) for spans with a
     single signal: applied last, by id range, each with evidence and a reviewer field.
"""
import json, re

POST_RAAG_ANG = 1353
GDIGITS = set('੦੧੨੩੪੫੬੭੮੯')

# whole-token name forms (direct + oblique/inflected) -> canonical author. Parmanand and
# Surdas are deliberately absent: ਪਰਮਾਨੰਦ is also an ordinary word ("supreme bliss", e.g. Sain's
# own ਭਜੁ ਪਰਮਾਨੰਦੇ) and Surdas's one tuk has no signature -- both are ledger decisions.
NAME_FORMS = {
    'Bhagat Kabir Ji':     ('ਕਬੀਰ', 'ਕਬੀਰੁ', 'ਕਬੀਰਾ', 'ਕੰਬੀਰੁ', 'ਕੰਬੀਰ', 'ਕਮੀਰ', 'ਕਮੀਰੁ'),
    'Bhagat Namdev Ji':    ('ਨਾਮਦੇਵ', 'ਨਾਮਦੇਉ', 'ਨਾਮਦੇਇ', 'ਨਾਮਦੇ', 'ਨਾਮਾ', 'ਨਾਮੇ', 'ਨਾਮੈ'),
    'Bhagat Ravidas Ji':   ('ਰਵਿਦਾਸ', 'ਰਵਿਦਾਸੁ', 'ਰਵਿਦਾਸਾ'),
    'Sheikh Farid Ji':     ('ਫਰੀਦ', 'ਫਰੀਦਾ', 'ਫਰੀਦੁ', 'ਫਰੀਦੈ'),
    'Bhagat Trilochan Ji': ('ਤ੍ਰਿਲੋਚਨ', 'ਤ੍ਰਿਲੋਚਨੁ', 'ਤਿਲੋਚਨੁ'),
    'Bhagat Beni Ji':      ('ਬੇਣੀ',),
    'Bhagat Dhanna Ji':    ('ਧੰਨਾ', 'ਧੰਨੇ', 'ਧੰਨੈ'),
    'Bhagat Jaidev Ji':    ('ਜੈਦੇਵ', 'ਜੈਦੇਉ'),
    'Bhagat Bhikhan Ji':   ('ਭੀਖਨ', 'ਭੀਖਨੁ'),
    'Bhagat Sain Ji':      ('ਸੈਣੁ', 'ਸੈਨੁ'),
    'Bhagat Pipa Ji':      ('ਪੀਪਾ', 'ਪੀਪੇ'),
    'Bhagat Sadhna Ji':    ('ਸਧਨਾ', 'ਸਧਨੇ'),
    'Bhagat Ramanand Ji':  ('ਰਾਮਾਨੰਦ', 'ਰਾਮਾਨੰਦੁ'),
}
FORM_TO_AUTHOR = {f: a for a, forms in NAME_FORMS.items() for f in forms}
GURU_LABEL_RE = re.compile(r'ਮਹਲਾ|ਮਹਲੇ|ਮਃ')
SALOK_BLOCK_AUTHORS = {'Bhagat Kabir Ji', 'Sheikh Farid Ji'}


def names_in(text):
    """Canonical authors named by whole tokens of `text`, in order of appearance."""
    out = []
    for t in text.split():
        a = FORM_TO_AUTHOR.get(t)
        if a and a not in out: out.append(a)
    return out


def bare_rubric(r):
    """A body line that is only a name (optionally ਸ੍ਰੀ-prefixed): ਪੀਪਾ ॥, ਸ੍ਰੀ ਸੈਣੁ ॥, ਕਬੀਰੁ ॥"""
    if r['is_header'] or r['markers']: return None
    toks = r['text'].split()
    if toks and toks[0] == 'ਸ੍ਰੀ': toks = toks[1:]
    if len(toks) == 1: return FORM_TO_AUTHOR.get(toks[0])
    return None


ANY_BHAGAT = '*'                    # a generic "Bani of the Bhagats" title: some Bhagat, not which
_GENERIC_BHAGAT_RE = re.compile(r'(^|\s)ਭਗਤ(ਾ|ਾਂ)(\s|$)')


def bhagat_title(r):
    """Author a header names: one Bhagat, ANY_BHAGAT for a generic Bhagat-bani title
    (ਜੈਤਸਰੀ ਬਾਣੀ ਭਗਤਾ ਕੀ), or None (a Guru's heading, or no attribution)."""
    if not r['is_header'] or GURU_LABEL_RE.search(r['text']): return None
    ns = names_in(r['text'])
    if ns: return ns[-1]            # ਬਾਣੀ ਭਗਤਾਂ ਕੀ ਤ੍ਰਿਲੋਚਨ -> Trilochan
    return ANY_BHAGAT if _GENERIC_BHAGAT_RE.search(r['text']) else None


def closes_shabad(r):
    nums = [m for m in r['markers'] if m and all(c in GDIGITS for c in m)]
    return len(nums) >= 2


def closes_salok(r):
    return bool(r['markers']) and all(c in GDIGITS for c in r['markers'][-1])


def shabads(records):
    """Yield (start, end) index pairs of shabad units before POST_RAAG_ANG. A unit begins at
    its opening header run / rubric line and ends at the ॥N॥M॥ count line."""
    start = None
    for i, r in enumerate(records):
        if r['ang'] >= POST_RAAG_ANG: break
        if start is None: start = i
        if r['is_header'] and i > start and not records[i - 1]['is_header'] \
                and not closes_shabad(records[i - 1]):
            start = i               # a heading interrupts an unclosed run: restart there
        if closes_shabad(r):
            yield start, i
            start = None


def signature(records, s, e):
    """Bhagat signing the closing couplet, or None if absent/ambiguous. The closing line
    counts first; the line before it only if the closing line names no one."""
    last = names_in(records[e]['text'])
    if len(last) == 1: return last[0]
    if len(last) > 1: return None
    if e - 1 >= s and not records[e - 1]['is_header']:
        prev = names_in(records[e - 1]['text'])
        if len(prev) == 1: return prev[0]
    return None


def rule_a(records):
    changes = {}
    for s, e in shabads(records):
        head = [r for r in records[s:e + 1] if r['is_header']]
        opening = []
        for r in records[s:e + 1]:
            if r['is_header'] or bare_rubric(r): opening.append(r)
            else: break
        if any(GURU_LABEL_RE.search(r['text']) for r in opening if r['is_header']):
            continue                                   # the Guru's own heading wins
        sig = signature(records, s, e)
        if not sig: continue
        rubric, how = None, None
        for r in opening:                              # the most specific opening rubric wins
            b = bare_rubric(r) or bhagat_title(r)
            if b and (rubric in (None, ANY_BHAGAT)):
                rubric, how = b, ('bare-name rubric' if bare_rubric(r) else 'own title')
        if rubric is None:                             # nearest Bhagat-naming title, same raag
            raag = records[s]['raag']
            for j in range(s - 1, -1, -1):
                q = records[j]
                if q['raag'] != raag: break
                b = bare_rubric(q) or bhagat_title(q)
                if b: rubric, how = b, f"block title id {q['id']}"; break
        if rubric == ANY_BHAGAT: how += ' (generic Bhagat-bani title)'
        if rubric not in (sig, ANY_BHAGAT): continue  # one signal only -> never auto-change
        for r in records[s:e + 1]:
            if r['author'] != sig:
                changes[r['id']] = (sig, 'A', f'{how} + signature id {records[e]["id"]}')
    return changes


def rule_b(records):
    changes, block, cur, guru_open = {}, None, None, False
    for r in records:
        t = r['text']
        if r['is_header'] and t.startswith('ਸਲੋਕ') and not GURU_LABEL_RE.search(t):
            ns = names_in(t)
            block = ns[0] if ns and ns[0] in SALOK_BLOCK_AUTHORS else None
            cur, guru_open = block, False
            continue
        if block is None: continue
        if r['is_header']:
            if GURU_LABEL_RE.search(t) and len(t.split()) <= 3:
                guru_open = True; cur = r['author']; continue
            if t.startswith('ੴ'): continue
            block = None; continue                    # any other heading ends the block
        want = cur if guru_open else block
        if r['author'] != want:
            changes[r['id']] = (want, 'B', f'salok scope in {block} block')
        if guru_open and closes_salok(r):
            guru_open, cur = False, block
    return changes


def rule_c(records, ledger):
    by_id = {r['id']: r for r in records}
    changes = {}
    for d in ledger.get('decisions', []):
        if d.get('action') != 'set_author': continue
        lo, hi = d['ids']
        for i in range(lo, hi + 1):
            r = by_id[i]
            if r['author'] == d['author']: continue    # already applied: idempotent
            if 'expect_author' in d and r['author'] not in d['expect_author']:
                raise SystemExit(f"ledger {d['key']}: id {i} author {r['author']!r} not in "
                                 f"expect_author -- corpus moved, re-review before applying")
            changes[i] = (d['author'], 'C', f"ledger {d['key']}")
    return changes


def apply(records, ledger):
    """Mutates records; returns [(id, ang, old, new, rule, evidence)]."""
    merged = {}
    for rule in (rule_a(records), rule_b(records), rule_c(records, ledger)):
        merged.update(rule)
    log = []
    for r in records:
        if r['id'] in merged:
            new, rule, ev = merged[r['id']]
            log.append((r['id'], r['ang'], r['author'], new, rule, ev))
            r['author'] = new
    # an ੴ invocation / heading run adopts the author of the body it opens
    for i in range(len(records) - 2, -1, -1):
        r, nxt = records[i], records[i + 1]
        if r['is_header'] and nxt['comp_id'] == r['comp_id'] and r['author'] != nxt['author'] \
                and not GURU_LABEL_RE.search(r['text']) and nxt['id'] in merged \
                and r['id'] not in merged:
            log.append((r['id'], r['ang'], r['author'], nxt['author'], 'H', 'heading adopts body'))
            r['author'] = nxt['author']
    return sorted(log)


if __name__ == '__main__':
    import sys
    recs = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
    led = json.load(open(sys.argv[2], encoding='utf-8')) if len(sys.argv) > 2 else {}
    for row in apply(recs, led):
        print(*row, sep='\t')
