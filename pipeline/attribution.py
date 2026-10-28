# -*- coding: utf-8 -*-
"""Attribution post-pass: who composed each line, from evidence PRINTED in the Granth.

build_corpus.py carries the last header's author forward until the next header that
names one. Four kinds of printed evidence were not read, so authorship "bled" from one
composition into the next (audit 2026-10-23: 46 runs, ~1,000 lines, e.g. Baba Farid's
saloks tagged as Guru Amar Das Ji's; Bhagats Dhanna, Sain, Pipa, Sadhna, Parmanand and
Baba Sundar absent altogether). This pass reads that evidence and changes the `author`
field ONLY -- never text, comp_id, line_no or is_header (verify_attribution.py proves it).

Rules, each tied to what the print shows:
  H  a heading names a Bhagat in an inflected form the header detector does not know
     ("ਆਸਾ ਬਾਣੀ ਭਗਤ ਧੰਨੇ ਜੀ ਕੀ", "ਬਾਣੀ ਸਧਨੇ ਕੀ ਰਾਗੁ ਬਿਲਾਵਲੁ", "ਸਿਰੀਰਾਗੁ ਤ੍ਰਿਲੋਚਨ ਕਾ ॥")
  L  a bare name label opens a shabad ("ਧੰਨਾ ॥", "ਪੀਪਾ ॥", "ਸ੍ਰੀ ਸੈਣੁ ॥", "ਨਾਮਦੇਵ ॥")
  P  a numbered pauri label names its Mahalla ("ਪਉੜੀ ੫ ॥" inside Guru Ram Das Ji's Gauri Vaar)
  C  a composition whose heading names nobody (under "ਬਾਣੀ ਭਗਤਾਂ ਕੀ", a bare "ਸਲੋਕੁ ॥")
     is signed in its own verse with exactly one Bhagat's pen-name and never "ਨਾਨਕ"
  S  in a Bhagat's salok collection ("ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ"), a "ਮਃ ੫ ॥" label covers ONE
     salok -- up to its numbered close -- and the collection's author resumes after it
  E  editorial decisions from attribution_ledger.json, e.g. Japji: only entries g3_gate.py lets
     through (owner-approved, a complete G3 ruling, or `held` in a draft that cannot release)

A heading that names a Mahalla always wins over C (Ang 326: "ਗਉੜੀ ਕਬੀਰ ਜੀ ਕੀ ਨਾਲਿ ਰਲਾਇ
ਲਿਖਿਆ ਮਹਲਾ ੫" stays Guru Arjan Dev Ji's although the verse names Kabir).
"""
import re
import g3_gate

M = {'੧': 'Guru Nanak Dev Ji (M1)', '੨': 'Guru Angad Dev Ji (M2)', '੩': 'Guru Amar Das Ji (M3)',
     '੪': 'Guru Ram Das Ji (M4)', '੫': 'Guru Arjan Dev Ji (M5)', '੯': 'Guru Tegh Bahadur Ji (M9)'}
MAHALA = re.compile(r'ਮਹਲ[ਾੇ]?\s+([੧੨੩੪੫੯])|ਮਃ\s*([੧੨੩੪੫੯])|ਮਹਲ[ਾੇ]\s+(ਪਹਿਲ|ਦੂਜ|ਤੀਜ|ਚਉਥ|ਪੰਜਵ)')

# Every printed form of each Bhagat's name: heading inflections (ਧੰਨੇ ਜੀ ਕੀ, ਨਾਮਦੇ ਜੀ ਕੀ)
# and the pen-name forms of their verses (ਕਹੈ ਧੰਨਾ, ਧੰਨੈ ਧਨੁ ਪਾਇਆ, ਨਾਮੇ ਕਾ ਸੁਆਮੀ).
NAMES = {
    'Bhagat Kabir Ji': ['ਕਬੀਰ', 'ਕਬੀਰਾ', 'ਕਬੀਰੁ', 'ਕਬੀਰਿ'],
    'Bhagat Namdev Ji': ['ਨਾਮਦੇਵ', 'ਨਾਮਦੇਉ', 'ਨਾਮਦੇ', 'ਨਾਮਾ', 'ਨਾਮੇ', 'ਨਾਮੈ'],
    'Bhagat Ravidas Ji': ['ਰਵਿਦਾਸ', 'ਰਵਿਦਾਸੁ', 'ਰਵਿਦਾਸਾ'],
    'Sheikh Farid Ji': ['ਫਰੀਦ', 'ਫਰੀਦਾ', 'ਫਰੀਦੁ', 'ਫਰੀਦੈ'],
    'Bhagat Trilochan Ji': ['ਤ੍ਰਿਲੋਚਨ', 'ਤ੍ਰਿਲੋਚਨੁ'],
    'Bhagat Beni Ji': ['ਬੇਣੀ'],
    'Bhagat Dhanna Ji': ['ਧੰਨਾ', 'ਧੰਨੇ', 'ਧੰਨੈ'],
    'Bhagat Jaidev Ji': ['ਜੈਦੇਵ', 'ਜੈਦੇਉ'],
    'Bhagat Bhikhan Ji': ['ਭੀਖਨ', 'ਭੀਖਨੁ'],
    'Bhagat Sain Ji': ['ਸੈਣੁ', 'ਸੈਣ', 'ਸੈਨੁ'],
    'Bhagat Pipa Ji': ['ਪੀਪਾ'],
    'Bhagat Sadhna Ji': ['ਸਧਨਾ', 'ਸਧਨੇ'],
    'Bhagat Ramanand Ji': ['ਰਾਮਾਨੰਦ', 'ਰਾਮਾਨੰਦੁ'],
    'Bhagat Parmanand Ji': ['ਪਰਮਾਨੰਦ'],
    'Bhagat Surdas Ji': ['ਸੂਰਦਾਸ'],
    'Baba Sundar Ji': ['ਸੁੰਦਰੁ'],
}
FORM = {f: a for a, fs in NAMES.items() for f in fs}

# Name forms that are also ordinary words (ਨਾਮੇ "in the Name", ਸੈਣੁ "friend", ਧੰਨਾ
# "blessed", ਪਰਮਾਨੰਦ "supreme bliss", ਸੁੰਦਰੁ "beautiful", ਬੇਣੀ "braid") count as a
# signature only in a strict signing position.
AMBIGUOUS = {'ਨਾਮਾ', 'ਨਾਮੇ', 'ਨਾਮੈ', 'ਸੈਣ', 'ਸੈਣੁ', 'ਸੈਨੁ', 'ਧੰਨਾ', 'ਧੰਨੇ', 'ਧੰਨੈ',
             'ਪਰਮਾਨੰਦ', 'ਸੁੰਦਰੁ', 'ਬੇਣੀ'}
STRICT_BEFORE = {'ਕਹੁ', 'ਕਹਿ', 'ਕਹਤ', 'ਕਹਤੁ', 'ਕਹੈ', 'ਭਨਿ', 'ਭਨੈ', 'ਭਣਤਿ', 'ਬਦਤਿ', 'ਭਾਖੈ',
                 'ਪ੍ਰਣਵੈ', 'ਜਨੁ', 'ਦਾਸੁ'}
STRICT_AFTER = {'ਕਹੈ', 'ਭਣੈ', 'ਭਨੈ', 'ਪ੍ਰਣਵੈ', 'ਬਿਨਵੈ'}
LOOSE_AFTER = STRICT_AFTER | {'ਕਾ', 'ਕੀ', 'ਕੇ', 'ਕਉ'}
LABEL_PREFIX = {'ਸ੍ਰੀ'}
LABEL_WORDS = {'ਮਹਲਾ', 'ਮਃ'}
PAURI_N = re.compile(r'^ਪਉੜੀ\s+([੧੨੩੪੫੯])$')
GDIGIT = re.compile('[੦-੯]')
RAAG_WORDS = {'ਸਿਰੀਰਾਗੁ', 'ਮਾਝ', 'ਗਉੜੀ', 'ਆਸਾਵਰੀ', 'ਆਸਾ', 'ਗੂਜਰੀ', 'ਦੇਵਗੰਧਾਰੀ', 'ਬਿਹਾਗੜਾ',
              'ਵਡਹੰਸੁ', 'ਵਡਹੰਸ', 'ਸੋਰਠਿ', 'ਧਨਾਸਰੀ', 'ਜੈਤਸਰੀ', 'ਟੋਡੀ', 'ਬੈਰਾੜੀ', 'ਤਿਲੰਗ', 'ਸੂਹੀ',
              'ਬਿਲਾਵਲੁ', 'ਬਿਲਾਵਲ', 'ਗੋਂਡ', 'ਗੋਡ', 'ਰਾਮਕਲੀ', 'ਨਟ', 'ਮਾਰੂ', 'ਤੁਖਾਰੀ', 'ਕੇਦਾਰਾ',
              'ਭੈਰਉ', 'ਬਸੰਤੁ', 'ਬਸੰਤ', 'ਸਾਰਗ', 'ਸਾਰੰਗ', 'ਮਲਾਰ', 'ਕਾਨੜਾ', 'ਕਲਿਆਨੁ', 'ਕਲਿਆਨ',
              'ਪ੍ਰਭਾਤੀ', 'ਜੈਜਾਵੰਤੀ'}


def _words(text):
    return [w for w in re.split(r'[\s॥।]+', text) if w]


def mahalla(text):
    m = MAHALA.search(text)
    if not m:
        return None
    if m.group(3):
        return M[{'ਪਹਿਲ': '੧', 'ਦੂਜ': '੨', 'ਤੀਜ': '੩', 'ਚਉਥ': '੪', 'ਪੰਜਵ': '੫'}[m.group(3)]]
    return M[m.group(1) or m.group(2)]


def heading_bhagat(text):
    """The Bhagat a heading line names, or None. When a line names two (a closing
    rubric run into the next heading: "ਕਬੀਰ ਕਾ ਸਬਦੁ ਰਾਗੁ ਮਾਰੂ ਬਾਣੀ ਨਾਮਦੇਉ ਜੀ ਕੀ"),
    the one qualified as "<name> ਜੀ/ਜੀਉ" or "ਬਾਣੀ/ਭਗਤ <name>" wins."""
    w = _words(text)
    strong, weak = [], []
    for i, t in enumerate(w):
        a = FORM.get(t)
        if not a:
            continue
        nxt = w[i + 1] if i + 1 < len(w) else ''
        prv = w[i - 1] if i else ''
        if nxt in ('ਜੀ', 'ਜੀਉ') or prv in ('ਬਾਣੀ', 'ਭਗਤ'):
            strong.append(a)
        elif nxt in ('ਕਾ', 'ਕੀ', 'ਕੇ') or prv in RAAG_WORDS or i == len(w) - 1 or 'ਸਲੋਕ' in w:
            weak.append(a)
    return (strong or weak or [None])[-1]


def bare_label(text):
    """"ਧੰਨਾ ॥" / "ਸ੍ਰੀ ਸੈਣੁ ॥" / "ਨਾਮਦੇਵ ॥" -> author; anything else -> None."""
    w = [t for t in _words(text) if t not in LABEL_PREFIX]
    return FORM.get(w[0]) if len(w) == 1 else None


def is_label(text):
    """A short attribution label that covers ONE following shabad/salok: "ਮਃ ੫ ॥",
    "ਮਹਲਾ ੫ ॥", "ਭੈਰਉ ਮਹਲਾ ੫ ॥", "ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ ॥" -- nothing but a raag name, the
    Mahalla, its number and at most a Bhagat's name."""
    w = _words(text)
    return bool(w) and mahalla(text) is not None and all(
        t in LABEL_WORDS or t in RAAG_WORDS or t in FORM or all(GDIGIT.match(c) for c in t)
        for t in w)


def signer(lines, salok=False):
    """The Bhagat who signs this shabad/salok: the LAST pen-name in a signing position
    within its final stanza (whole salok for saloks). None when "ਨਾਨਕ" signs it."""
    tail = lines if salok else lines[-4:]
    found = None
    for r in tail:
        w = _words(r['text'])
        for i, t in enumerate(w):
            if t.startswith('ਨਾਨਕ'):
                return None
            a = FORM.get(t)
            if not a:
                continue
            prv = w[i - 1] if i else ''
            nxt = w[i + 1] if i + 1 < len(w) else ''
            if t in AMBIGUOUS:
                ok = prv in STRICT_BEFORE or nxt in STRICT_AFTER or \
                     (i == 0 and r is lines[-1] and not salok)
            else:
                ok = i == 0 or prv in STRICT_BEFORE | {'ਦੇਖੁ', 'ਜਨ', 'ਦਾਸ'} or nxt in LOOSE_AFTER
            if ok:
                found = a
    return found


def _ends(r, salok):
    nums = [m for m in (r.get('markers') or []) if GDIGIT.search(m)]
    return len(nums) >= (1 if salok else 2)


def apply(records, ledger=None, gate=None):
    """Mutates records' `author` in place; returns the change log. `gate`: keyword arguments for
    g3_gate.check (tests only)."""
    log, flags = [], []

    def setauthor(r, a, rule, evidence):
        if a and r['author'] != a:
            log.append({'id': r['id'], 'ang': r['ang'], 'comp_id': r['comp_id'],
                        'from': r['author'], 'to': a, 'rule': rule, 'evidence': evidence})
            r['author'] = a

    # ---- P: "ਪਉੜੀ ੫ ॥" -- a numbered pauri names its Mahalla ----------------
    comps = {}
    for r in records:
        comps.setdefault(r['comp_id'], []).append(r)
    for rows in comps.values():
        pn = next((PAURI_N.match(r['text']) for r in rows if r['is_header'] and PAURI_N.match(r['text'])), None)
        if pn:
            for r in rows:
                setauthor(r, M[pn.group(1)], 'P', 'heading ' + pn.group(0))

    # ---- sections of Bhagat Bani, shabad by shabad ------------------------------
    # Phase 1: cut each section into segments (one shabad / one salok each).
    segs, sec, sec_no = [], None, 0
    cur = {'rows': [], 'label': None, 'lab_ev': ''}

    def close():
        nonlocal cur
        if sec is not None and any(not r['is_header'] for r in cur['rows']):
            segs.append(dict(cur, sec=sec_no, sec_author=sec['author'], salok=sec['salok'],
                             sec_ev=sec['ev']))
        cur = {'rows': [], 'label': None, 'lab_ev': ''}

    for r in records:
        t = r['text']
        if r['is_header']:
            if any(not x['is_header'] for x in cur['rows']):
                close()
            words = _words(t)
            mh, nm = mahalla(t), heading_bhagat(t)
            if t.startswith('ੴ'):
                pass
            elif sec is not None and mh and is_label(t):
                cur['label'], cur['lab_ev'] = mh, t        # ONE shabad/salok by a Guru
            elif mh:
                cur = {'rows': [], 'label': None, 'lab_ev': ''}
                sec = None                                  # a Guru's own heading ends the section
            elif nm:
                sec_no += 1
                sec = {'author': nm, 'salok': 'ਸਲੋਕ' in words, 'ev': t}
                cur['label'], cur['lab_ev'] = nm, t
            elif any(x in ('ਭਗਤਾ', 'ਭਗਤਾਂ') for x in words):
                sec_no += 1
                sec = {'author': None, 'salok': False, 'ev': t}
            elif sec is not None and not (words[0] in RAAG_WORDS or words in (['ਸਲੋਕੁ'], ['ਸਲੋਕ'])):
                cur = {'rows': [], 'label': None, 'lab_ev': ''}
                sec = None                                  # any other heading ends it
            cur['rows'].append(r)
            continue
        lab = bare_label(t)
        if lab and sec is not None:
            if any(not x['is_header'] for x in cur['rows']):
                close()
            cur['label'], cur['lab_ev'] = lab, t
        cur['rows'].append(r)
        if sec is not None and _ends(r, sec['salok']):
            close()
    close()

    # Phase 2: resolve each segment from evidence, strongest first.
    def last_num(seg):
        for r in reversed(seg['rows']):
            nums = [m for m in (r.get('markers') or []) if GDIGIT.search(m)]
            if nums:
                return int(''.join(str('੦੧੨੩੪੫੬੭੮੯'.index(c)) for c in nums[-1] if c in '੦੧੨੩੪੫੬੭੮੯'))
        return None

    for s in segs:
        body = [r for r in s['rows'] if not r['is_header']]
        s['signer'] = None if s['salok'] else signer(body)
        s['num'] = last_num(s)
        if s['label']:
            s['who'], s['rule'], s['ev'] = s['label'], 'L', s['lab_ev']
        elif s['salok']:
            s['who'], s['rule'], s['ev'] = s['sec_author'], 'S', s['sec_ev']
            other = signer(body, salok=True)
            if other and other != s['sec_author']:
                flags.append({'id': body[0]['id'], 'ang': body[0]['ang'], 'kind': 'salok-signed-by-another',
                              'collection': s['sec_author'], 'signed': other, 'text': body[-1]['text']})
        elif s['signer']:
            s['who'], s['rule'], s['ev'] = s['signer'], 'C', 'signed: ' + body[-1]['text']
        else:
            s['who'] = None

    # N: an unsigned shabad takes the signer of its numbered series -- the running
    # count (॥੨॥੧॥, ॥੨॥੨॥, ॥੪॥੩॥ ...) continues with no heading between.
    i = 0
    while i < len(segs):
        j = i
        while (j + 1 < len(segs) and segs[j + 1]['sec'] == segs[i]['sec']
               and not segs[j + 1]['label'] and segs[j]['num'] is not None
               and segs[j + 1]['num'] == segs[j]['num'] + 1):
            j += 1
        run = [s for s in segs[i:j + 1] if not s['salok']]
        signed = {s['who'] for s in run if s.get('rule') in ('C', 'L') and s['who']}
        if len(signed) == 1:
            who = signed.pop()
            for s in run:
                if s['who'] is None:
                    s['who'], s['rule'], s['ev'] = who, 'N', 'numbered series signed by ' + who
        i = j + 1

    for s in segs:
        if s['who'] is None and s['sec_author']:
            s['who'], s['rule'], s['ev'] = s['sec_author'], 'H', s['sec_ev']
        if not s['who']:
            continue
        for r in s['rows']:
            was = r['author']
            # positive evidence (label, signature, series) may correct anyone; the bare
            # section fallback only repairs bleed from a Guru's heading or a missing tag
            if s['rule'] == 'H' and was and not was.startswith('Guru '):
                continue
            # a closing rubric (ਸੁਧੁ, ਸੁਧੁ ਕੀਚੇ) belongs to the composition it closes
            if r['is_header'] and r['text'].startswith('ਸੁਧੁ'):
                continue
            setauthor(r, s['who'], s['rule'], s['ev'])

    # ---- V: a bare "ਸਲੋਕੁ ॥" in a Guru's Vaar that opens with a Bhagat's name ----
    for rows in comps.values():
        heads = [r for r in rows if r['is_header']]
        body = [r for r in rows if not r['is_header']]
        if body and heads and all(_words(h['text']) in (['ਸਲੋਕੁ'], ['ਸਲੋਕ']) for h in heads):
            first = _words(body[0]['text'])
            a = FORM.get(first[0]) if first else None
            if a and first[0] not in AMBIGUOUS and not any('ਨਾਨਕ' in b['text'] for b in body):
                for r in rows:
                    setauthor(r, a, 'V', 'opens: ' + body[0]['text'])

    # ---- E: editorial decisions the G3 gate lets through ----------------------
    by_id = {r['id']: r for r in records}
    for e in g3_gate.check(ledger or [], 'attribution', **(gate or {})):
        missing = [i for i in range(e['start_id'], e['end_id'] + 1) if i not in by_id]
        if missing:
            raise g3_gate.GateError(f"attribution:{e['entry']}: ids {missing[:5]} are not in the corpus")
        for lid in range(e['start_id'], e['end_id'] + 1):
            r = by_id[lid]
            if e['to'] is None and r['author'] is not None:
                # a G3 ruling that the line carries no author (a heading shared by several Bhagats)
                log.append({'id': r['id'], 'ang': r['ang'], 'comp_id': r['comp_id'],
                            'from': r['author'], 'to': None, 'rule': 'E', 'evidence': e['reason']})
                r['author'] = None
            else:
                setauthor(r, e['to'], 'E', e['reason'])
    return log, flags


def load_ledger(path):
    return g3_gate.load('attribution', path)
