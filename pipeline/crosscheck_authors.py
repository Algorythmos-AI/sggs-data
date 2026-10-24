# -*- coding: utf-8 -*-
"""Independent cross-check of per-line authorship against the ShabadOS database (v4.8.7,
sha256 d8e07134…, archived in Algorythmos-AI/sggs-source). Read-only; never feeds the corpus.

Lines are aligned Ang by Ang on first letters (ShabadOS stores GurbaniAkhar ASCII; only the
consonant/vowel-carrier map below is needed), then the line's author is compared with the
ShabadOS writer of the shabad that line belongs to.
Gate: every aligned VERSE line (is_header = 0) whose author differs from ShabadOS must be covered by a reviewed
entry in pipeline/shabados_crosscheck_flags.json (by id range or Ang range). An uncovered
disagreement fails the build -- a new attribution error, or a flag nobody reviewed.
Headings are reported but not gated: they follow a structural convention (a heading carries
the author of what it opens or names -- e.g. ਸਿਰੀਰਾਗ ਕੀ ਵਾਰ ਮਹਲਾ ੪ is M4 here, while ShabadOS
files a Vaar's title under the writer of its first salok).

usage: crosscheck_authors.py corpus.jsonl shabados.sqlite [--flags PATH]
"""
import json, sqlite3, sys, difflib, collections

ASCII = {'k': 'ਕ', 'K': 'ਖ', 'g': 'ਗ', 'G': 'ਘ', '|': 'ਙ', 'c': 'ਚ', 'C': 'ਛ', 'j': 'ਜ', 'J': 'ਝ',
         '\\': 'ਞ', 't': 'ਟ', 'T': 'ਠ', 'f': 'ਡ', 'F': 'ਢ', 'x': 'ਣ', 'q': 'ਤ', 'Q': 'ਥ', 'd': 'ਦ',
         'D': 'ਧ', 'n': 'ਨ', 'p': 'ਪ', 'P': 'ਫ', 'b': 'ਬ', 'B': 'ਭ', 'm': 'ਮ', 'X': 'ਯ', 'r': 'ਰ',
         'l': 'ਲ', 'v': 'ਵ', 'V': 'ੜ', 's': 'ਸ', 'h': 'ਹ', 'S': 'ਸ਼', 'z': 'ਜ਼', 'Z': 'ਗ਼', '^': 'ਖ਼',
         '&': 'ਫ਼', 'L': 'ਲ਼', 'A': 'ਅ', 'e': 'ੲ', 'a': 'ੳ', '<': 'ੴ', 'E': 'ਓ', 'H': 'ੑ'}
CARRIER = {}
for ch in 'ਅਆਐਔ': CARRIER[ch] = 'ਅ'
for ch in 'ੲਇਈਏ': CARRIER[ch] = 'ੲ'
for ch in 'ੳਉਊਓ': CARRIER[ch] = 'ੳ'
NUKTA = {'ਸ਼': 'ਸ', 'ਜ਼': 'ਜ', 'ਗ਼': 'ਗ', 'ਖ਼': 'ਖ', 'ਫ਼': 'ਫ', 'ਲ਼': 'ਲ'}

WRITER = {'Guru Nanak Dev Ji': 'Guru Nanak Dev Ji (M1)', 'Guru Angad Dev Ji': 'Guru Angad Dev Ji (M2)',
          'Guru Amardas Ji': 'Guru Amar Das Ji (M3)', 'Guru Ramdas Ji': 'Guru Ram Das Ji (M4)',
          'Guru Arjan Dev Ji': 'Guru Arjan Dev Ji (M5)', 'Guru Tegh Bahadur Ji': 'Guru Tegh Bahadur Ji (M9)',
          'Bhagat Bheekhan Ji': 'Bhagat Bhikhan Ji', 'Satta and Balwand': 'Satta & Balwand',
          'Baba Sundar': 'Baba Sundar Ji', 'Bhatt Balh': 'Bhatt Bal (ਭਟ)', 'Bhatt Bhalh': 'Bhatt Bhal (ਭਟ)',
          'Bhatt Bhikha': 'Bhatt Bhikha (ਭਟ)', 'Bhatt Gayand': 'Bhatt Gayand (ਭਟ)',
          'Bhatt Harbans': 'Bhatt Haribans (ਭਟ)', 'Bhatt Jaalap': 'Bhatt Jalap (ਭਟ)',
          'Bhatt Kalh Sahar': 'Bhatt Kalsahar (ਭਟ)', 'Bhatt Keerat': 'Bhatt Kirat (ਭਟ)',
          'Bhatt Mathura': 'Bhatt Mathura (ਭਟ)', 'Bhatt Nalh': 'Bhatt Nal (ਭਟ)', 'Bhatt Salh': 'Bhatt Sal (ਭਟ)'}


def norm_letter(ch):
    ch = NUKTA.get(ch, ch)
    return CARRIER.get(ch, ch)


def key_ours(r):
    return ''.join(norm_letter(c) for c in r['fl_g'].split())


def key_sos(fl):
    out, i = [], 0
    while i < len(fl):
        if fl.startswith('<>', i): out.append('ੴ'); i += 2; continue
        ch = ASCII.get(fl[i])
        if ch: out.append(norm_letter(ch))
        i += 1
    return ''.join(out)


def load_sos(path):
    db = sqlite3.connect(path)
    rows = db.execute("""SELECT l.source_page, l.first_letters, w.name_english, l.gurmukhi
        FROM lines l JOIN shabads s ON s.id = l.shabad_id JOIN writers w ON w.id = s.writer_id
        WHERE s.source_id = 1 ORDER BY l.order_id""").fetchall()
    by_ang = collections.defaultdict(list)
    for ang, fl, w, g in rows:
        by_ang[ang].append((key_sos(fl or ''), WRITER.get(w, w), g))
    return by_ang


def compare(records, sos):
    by_ang = collections.defaultdict(list)
    for r in records: by_ang[r['ang']].append(r)
    matched, agree, dis = 0, 0, []
    for ang, ours in by_ang.items():
        theirs = sos.get(ang, [])
        sm = difflib.SequenceMatcher(a=[key_ours(r) for r in ours], b=[t[0] for t in theirs],
                                     autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                r, t = ours[a + k], theirs[b + k]
                if not r['text'] or len(t[0]) < 2: continue      # too short to align reliably
                matched += 1
                if r['author'] == t[1]: agree += 1
                else: dis.append((r['id'], ang, r['author'], t[1], r['is_header'], r['text'][:40]))
    return matched, agree, dis



def covered(d, flags):
    lid, ang = d[0], d[1]
    for f in flags:
        if 'ids' in f and f['ids'][0] <= lid <= f['ids'][1]: return f['key']
        if 'ang' in f and f['ang'][0] <= ang <= f['ang'][1]: return f['key']
    return None


if __name__ == '__main__':
    import argparse, os
    a = argparse.ArgumentParser()
    a.add_argument('corpus'); a.add_argument('shabados')
    a.add_argument('--flags', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    'shabados_crosscheck_flags.json'))
    args = a.parse_args()
    with open(args.corpus, encoding='utf-8') as f: recs = [json.loads(l) for l in f]
    with open(args.flags, encoding='utf-8') as f: flags = json.load(f)['flags']
    m, agree, dis = compare(recs, load_sos(args.shabados))
    by_flag = collections.Counter(covered(d, flags) for d in dis)
    print(f'aligned {m} lines with ShabadOS; author agrees on {agree} ({agree / m:.4%})')
    for k, n in sorted(by_flag.items(), key=lambda x: str(x[0])):
        if k: print(f'  {n:5d} differ inside reviewed flag {k}')
    heads = [d for d in dis if d[4] and not covered(d, flags)]
    if heads: print(f'  {len(heads):5d} headings differ (reported, not gated)')
    loose = [d for d in dis if not d[4] and not covered(d, flags)]
    for d in loose[:40]: print('  UNCOVERED', *d)
    if loose:
        sys.exit(f'crosscheck: FAIL -- {len(loose)} disagreements with ShabadOS outside reviewed flags')
    print('crosscheck: PASS -- every disagreement with ShabadOS is a reviewed, flagged attribution')
