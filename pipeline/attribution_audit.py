# -*- coding: utf-8 -*-
"""Line-level attribution audit: our corpus `author` vs an independent oracle
(the ShabadOS database's per-shabad writer).

The oracle is a cross-check only. It is never copied into the corpus, never
shipped and never cited: a disagreement is a question for the evidence printed
in the Granth itself (the composition's heading, its ਮਹਲਾ/ਮਃ label, and the
pen-name -- chhap -- in its closing verse), and contested cases go to a scholar.

Usage:
  python3 attribution_audit.py <shabados.db> <corpus.jsonl> <out_dir>
Writes <out_dir>/diff.csv (one row per disagreeing line) and summary.json.
"""
import sys, os, re, json, csv, sqlite3, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sggs_pipeline import CONS, HALANT  # noqa: E402

# ---- ShabadOS ASCII Gurmukhi -> Unicode (same mapping as shabados_ingest.py) ----
DIGRAPHS = dict([('<>', 'ੴ'), ('AW', 'ਆਂ'), ('Aw', 'ਆ'), ('AY', 'ਐ'), ('AO', 'ਔ'),
                 ('aU', 'ਊ'), ('au', 'ਉ'), ('eI', 'ਈ'), ('ey', 'ਏ'), ('ie', 'ਇ')])
MAP = {
    'a': 'ੳ', 'A': 'ਅ', 'e': 'ੲ', 's': 'ਸ', 'h': 'ਹ',
    'k': 'ਕ', 'K': 'ਖ', 'g': 'ਗ', 'G': 'ਘ', '|': 'ਙ',
    'c': 'ਚ', 'C': 'ਛ', 'j': 'ਜ', 'J': 'ਝ', '\\': 'ਞ',
    't': 'ਟ', 'T': 'ਠ', 'f': 'ਡ', 'F': 'ਢ', 'x': 'ਣ',
    'q': 'ਤ', 'Q': 'ਥ', 'd': 'ਦ', 'D': 'ਧ', 'n': 'ਨ',
    'p': 'ਪ', 'P': 'ਫ', 'b': 'ਬ', 'B': 'ਭ', 'm': 'ਮ',
    'X': 'ਯ', 'r': 'ਰ', 'l': 'ਲ', 'v': 'ਵ', 'V': 'ੜ',
    'E': 'ਓ', 'S': 'ਸ਼', 'z': 'ਜ਼', 'Z': 'ਗ਼', '^': 'ਖ਼', '&': 'ਫ਼', 'L': 'ਲ਼',
    'w': 'ਾ', 'i': 'ਿ', 'I': 'ੀ', 'u': 'ੁ', 'U': 'ੂ', 'y': 'ੇ', 'Y': 'ੈ', 'o': 'ੋ', 'O': 'ੌ',
    'W': 'ਾਂ', 'M': 'ੰ', 'µ': 'ੰ', 'N': 'ਂ', 'ˆ': 'ਂ', 'Ú': 'ਃ', '@': 'ੑ', '~': 'ੱ', '`': 'ੱ',
    'R': '੍ਰ', '®': '੍ਰ', 'H': '੍ਹ', 'Í': '੍ਵ', '´': '੍ਯ', 'Î': '੍ਯ', 'ç': '੍ਚ', '†': '੍ਟ',
    'œ': '੍ਤ', '˜': '੍ਨ', 'ü': 'ੁ', '¨': 'ੂ', 'Ø': '',
    ']': '॥', '[': '।',
    '0': '੦', '1': '੧', '2': '੨', '3': '੩', '4': '੪', '5': '੫', '6': '੬', '7': '੭', '8': '੮', '9': '੯',
    ' ': ' ', ';': '', ',': '', '.': '',
    '₁': '', '₂': '', '₃': '', '₄': '', '₅': '', '₆': '', '₈': '',
}
PASSTHROUGH = set('ੴਆਉਊਇਈਏਐਔ') | {'ਾ', 'ਂ'}
FOLD = {'ਸ਼': 'ਸ', 'ਖ਼': 'ਖ', 'ਗ਼': 'ਗ', 'ਜ਼': 'ਜ', 'ਫ਼': 'ਫ', 'ਲ਼': 'ਲ', 'ੱ': '', 'ੑ': ''}


def move_sihari(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == 'ਿ':
            j = i + 1
            if j < n and s[j] in CONS:
                j += 1
                while j + 1 < n and s[j] == HALANT and s[j + 1] in CONS:
                    j += 2
                out.append(s[i + 1:j]); out.append('ਿ')
                i = j; continue
        out.append(c); i += 1
    return ''.join(out)


def to_unicode(ascii_g):
    s = ascii_g
    for a, b in DIGRAPHS.items():
        s = s.replace(a, b)
    u = ''.join(ch if ch in PASSTHROUGH else MAP.get(ch, '') for ch in s)
    for a, b in FOLD.items():
        u = u.replace(a, b)
    return unicodedata.normalize('NFC', move_sihari(u))


_STRIP = re.compile(r'[॥।\s੦-੯ੱੑ]+')
_RAHAO = re.compile(r'ਰਹਾਉ(ਦੂਜਾ)?$')


def norm(s):
    for a, b in FOLD.items():
        s = s.replace(a, b)
    return _RAHAO.sub('', _STRIP.sub('', unicodedata.normalize('NFC', s)))


# ShabadOS writer -> our canonical author string. ShabadOS has no separate
# writer for Bhai Mardana or the collective Bhatt label; those never match by
# construction and are reported as their own classes.
WRITER = {
    'Guru Nanak Dev Ji': 'Guru Nanak Dev Ji (M1)', 'Guru Angad Dev Ji': 'Guru Angad Dev Ji (M2)',
    'Guru Amardas Ji': 'Guru Amar Das Ji (M3)', 'Guru Ramdas Ji': 'Guru Ram Das Ji (M4)',
    'Guru Arjan Dev Ji': 'Guru Arjan Dev Ji (M5)', 'Guru Tegh Bahadur Ji': 'Guru Tegh Bahadur Ji (M9)',
    'Bhagat Beni Ji': 'Bhagat Beni Ji', 'Bhagat Bheekhan Ji': 'Bhagat Bhikhan Ji',
    'Bhagat Dhanna Ji': 'Bhagat Dhanna Ji', 'Sheikh Farid Ji': 'Sheikh Farid Ji',
    'Bhagat Jaidev Ji': 'Bhagat Jaidev Ji', 'Bhagat Kabir Ji': 'Bhagat Kabir Ji',
    'Bhagat Namdev Ji': 'Bhagat Namdev Ji', 'Bhagat Parmanand Ji': 'Bhagat Parmanand Ji',
    'Bhagat Pipa Ji': 'Bhagat Pipa Ji', 'Bhagat Ramanand Ji': 'Bhagat Ramanand Ji',
    'Bhagat Ravidas Ji': 'Bhagat Ravidas Ji', 'Bhagat Sadhna Ji': 'Bhagat Sadhna Ji',
    'Bhagat Sain Ji': 'Bhagat Sain Ji', 'Bhagat Surdas Ji': 'Bhagat Surdas Ji',
    'Bhagat Trilochan Ji': 'Bhagat Trilochan Ji', 'Baba Sundar': 'Baba Sundar Ji',
    'Satta and Balwand': 'Satta & Balwand',
    'Bhatt Balh': 'Bhatt Bal (ਭਟ)', 'Bhatt Bhalh': 'Bhatt Bhal (ਭਟ)', 'Bhatt Bhikha': 'Bhatt Bhikha (ਭਟ)',
    'Bhatt Gayand': 'Bhatt Gayand (ਭਟ)', 'Bhatt Harbans': 'Bhatt Haribans (ਭਟ)',
    'Bhatt Jaalap': 'Bhatt Jalap (ਭਟ)', 'Bhatt Kalh Sahar': 'Bhatt Kalsahar (ਭਟ)',
    'Bhatt Keerat': 'Bhatt Kirat (ਭਟ)', 'Bhatt Mathura': 'Bhatt Mathura (ਭਟ)',
    'Bhatt Nalh': 'Bhatt Nal (ਭਟ)', 'Bhatt Salh': 'Bhatt Sal (ਭਟ)',
    'Poet Alam': 'Poet Alam',
}

WINDOW = 60   # how far ahead (in our line order) a ShabadOS line may land


def load_oracle(db):
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    rows = con.execute("""
        SELECT l.source_page, l.gurmukhi, w.name_english, l.type_id, l.shabad_id
        FROM lines l JOIN shabads s ON s.id = l.shabad_id JOIN writers w ON w.id = s.writer_id
        WHERE s.source_id = 1 ORDER BY l.order_id""").fetchall()
    con.close()
    return [(ang, norm(to_unicode(g)), WRITER.get(w, w), t, sid) for ang, g, w, t, sid in rows]


def align(records, oracle):
    """Monotone greedy alignment: each oracle line claims the next unclaimed
    record (in corpus order, within WINDOW) whose normalised text is equal."""
    keys = [norm(r['text']) for r in records]
    theirs = [None] * len(records)
    shabad = [None] * len(records)
    ptr, matched = 0, 0
    for ang, k, writer, _t, sid in oracle:
        if not k:
            continue
        hi = min(len(records), ptr + WINDOW)
        for j in range(ptr, hi):
            if keys[j] == k and theirs[j] is None:
                theirs[j], shabad[j] = writer, sid
                ptr, matched = j + 1, matched + 1
                break
    return theirs, shabad, matched


def main(db, corpus, out_dir):
    records = [json.loads(l) for l in open(corpus, encoding='utf-8')]
    oracle = load_oracle(db)
    theirs, shabad, matched = align(records, oracle)
    os.makedirs(out_dir, exist_ok=True)
    rows, by_pair = [], collections.Counter()
    unmatched_body = 0
    for r, t, sid in zip(records, theirs, shabad):
        if r['is_header']:
            continue
        if t is None:
            unmatched_body += 1
            continue
        if t != r['author']:
            rows.append({'id': r['id'], 'ang': r['ang'], 'comp_id': r['comp_id'],
                         'ours': r['author'] or '', 'theirs': t, 'oracle_shabad': sid,
                         'gurmukhi': r['gurmukhi']})
            by_pair[(r['author'] or 'NULL', t)] += 1
    with open(os.path.join(out_dir, 'diff.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['id'])
        w.writeheader(); w.writerows(rows)
    body = sum(1 for r in records if not r['is_header'])
    summary = {
        'corpus_body_lines': body, 'oracle_lines': len(oracle), 'aligned_lines': matched,
        'unaligned_body_lines': unmatched_body, 'disagreeing_lines': len(rows),
        'by_pair': [{'ours': a, 'theirs': b, 'lines': n} for (a, b), n in by_pair.most_common()],
    }
    json.dump(summary, open(os.path.join(out_dir, 'summary.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f"body lines {body} | aligned {matched} | unaligned body {unmatched_body} | "
          f"disagreeing {len(rows)}")
    for (a, b), n in by_pair.most_common(40):
        print(f'  {n:5}  ours={a:28} oracle={b}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
