# -*- coding: utf-8 -*-
"""Per-voice facts computed from the Gurmukhi of the Granth (additive tables only).

  python3 pipeline/build_author_facts.py --db <sggs.sqlite>

  author_facts       one row per voice: verse/composition/rahao counts, Ang presence
                     (a 1430-bit mask), raags with verse counts, raags no other voice uses,
                     the first verse, pen-name (chhap) usage, Gurmukhi stylometry
  author_mentions    verses in which one voice names another (a Bhagat, or a Guru praised
                     by the Bhatts) -- matched on whole Gurmukhi words, verbatim
  author_dialogues   in the Bhagat salok collections, a Guru's salok that directly follows a
                     Bhagat's salok (Angs 1364-1384) -- both sides by line-id range
  author_distinctive_terms is rebuilt from GURMUKHI words (it was built from the English
                     translation layer, which is not licensed for redistribution)

Nothing here reads or writes scripture: `lines` is only read. Counts use verse lines
(is_header = 0) so every surface shows one number per voice.
"""
import argparse, base64, collections, json, math, re, sqlite3, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attribution import NAMES, AMBIGUOUS  # noqa: E402

N_ANGS = 1430
GDIG = re.compile('[੦-੯]')
WORD = re.compile(r'[਀-੿]+')
# very frequent function words: postpositions, particles, pronouns, copulas
STOP = set('''ਕੈ ਕਾ ਕੀ ਕੇ ਕੋ ਕਉ ਕੂ ਨੋ ਨੂੰ ਤੇ ਤੈ ਤਉ ਤਾ ਤਾਂ ਜਾ ਜਾਂ ਜੇ ਜੋ ਜਿ ਸੋ ਸਿ ਸੇ ਸਭ ਸਭੁ ਸਭਿ ਸਭੇ ਹੈ ਹੈਂ ਹਹਿ ਹੋਇ ਹੋਵੈ
ਨ ਨਾ ਨਹੀ ਨਾਹੀ ਨਾਹਿ ਮਹਿ ਮਾਹਿ ਵਿਚਿ ਅੰਦਰਿ ਭੀ ਭਿ ਹੀ ਇਕੁ ਇਕ ਏਕ ਏਕੁ ਕਿਆ ਕਿਉ ਕੋਈ ਕਿਛੁ ਕਿਛੂ ਇਹੁ ਇਹ ਏਹੁ ਓਹੁ ਉਹੁ ਤਿਸੁ ਜਿਸੁ ਜਿਨਿ ਤਿਨਿ
ਮੈ ਮੇਰਾ ਮੇਰੀ ਮੇਰੇ ਤੂ ਤੂੰ ਤੇਰਾ ਤੇਰੀ ਤੇਰੇ ਹਮ ਹਮਰਾ ਹਮਰੀ ਤੁਮ ਆਪਿ ਆਪੇ ਆਪਣਾ ਆਪਣੀ ਆਪਣੇ ਕਰਿ ਕਹਿ ਕਹੁ ਰੇ ਹੇ ਜੀਉ ਜੀ
ਅਰੁ ਅਤੇ ਕਰੇ ਕਰੈ ਕੀਆ ਕੀਤਾ ਜਿਉ ਤਿਉ ਸਿਉ ਸੰਗਿ ਨਾਲਿ ਬਿਨੁ ਲਗਿ ਉਪਰਿ ਊਪਰਿ ਪਾਸਿ ਆਗੈ ਅਗੈ ਪਾਛੈ ਜਬ ਤਬ ਕਬ ਜਹ ਤਹ ਇਤੁ ਉਤੁ ਏਵ
ਰਹਾਉ ਦੂਜਾ ਭਾਈ ਮਨ ਮਨੁ ਮਨਿ
ਜਉ ਜੁ ਅਬ ਜਿਹ ਤਿਹ ਤਾਹਿ ਜਾਹਿ ਕਹਾ ਕਛੁ ਨਹ ਨਹਿ ਕੈਸੇ ਜੈਸੇ ਤੈਸੇ ਐਸੇ ਤੇਰੋ ਮੇਰੋ ਜੋਈ ਹੋ ਦੀ ਦਾ ਦੇ
ਤੁਧੁ ਤੁਧ ਲਗੁ ਇਕਨ੍ਹਾ ਇਕਨਾ ਜਿਨ ਤਿਨ ਕੇਤੇ ਵਿਣੁ ਭਇਓ ਭਇਆ ਜਾਨੈ ਜਾਣੈ ਜਾਣੀਐ ਰਹੈ ਲਾਗਾ ਪਾਏ ਪਾਇਆ ਹੋਈ ਹੋਆ
ਫੁਨਿ ਕੀਅਉ ਕਰੁ ਜਾਮਿ ਵਲਿ ਗਏ ਅਜੁ ਚਲਿ ਸਿਰਿ ਘਰਿ'''.split())
# whole-word pen-names: a voice signing its own verse is not a "distinctive term"
SIGNS = {f for forms in NAMES.values() for f in forms}
GURU_FORMS = {   # names by which the Bhatts / Satta & Balwand / Sundar praise the Gurus
    'Guru Nanak Dev Ji (M1)': {'ਨਾਨਕੁ', 'ਨਾਨਕ', 'ਨਾਨਕਿ'},
    'Guru Angad Dev Ji (M2)': {'ਅੰਗਦ', 'ਅੰਗਦੁ', 'ਅੰਗਦਿ', 'ਲਹਣਾ', 'ਲਹਣੇ', 'ਲਹਣੈ'},
    'Guru Amar Das Ji (M3)': {'ਅਮਰਦਾਸ', 'ਅਮਰਦਾਸੁ', 'ਅਮਰਦਾਸਿ'},
    'Guru Ram Das Ji (M4)': {'ਰਾਮਦਾਸ', 'ਰਾਮਦਾਸੁ', 'ਰਾਮਦਾਸਿ', 'ਰਾਮਦਾਸੈ'},
    'Guru Arjan Dev Ji (M5)': {'ਅਰਜੁਨ', 'ਅਰਜੁਨੁ', 'ਅਰਜਨੁ', 'ਅਰਜਨ'},
}
PRAISERS = ('(ਭਟ)', 'Satta & Balwand', 'Baba Sundar Ji')


def words(text):
    return [w for w in WORD.findall(text or '') if not GDIG.search(w)]


def mattr(toks, window=100):
    n = len(toks)
    if n < window:
        return len(set(toks)) / n if n else 0.0
    r = [len(set(toks[i:i + window])) / window for i in range(0, n - window + 1, window // 4)]
    return sum(r) / len(r)


def mask_b64(angs):
    bits = bytearray((N_ANGS + 7) // 8)
    for a in angs:
        if 1 <= a <= N_ANGS:
            bits[(a - 1) // 8] |= 1 << (7 - (a - 1) % 8)
    return base64.b64encode(bytes(bits)).decode()


def build(con):
    rows = con.execute('SELECT id, ang, raag, author, comp_id, is_header, is_rahao, text, markers '
                       'FROM lines ORDER BY id').fetchall()
    con.executescript('''
      DROP TABLE IF EXISTS author_facts;
      CREATE TABLE author_facts (
        author TEXT PRIMARY KEY, n_verses INTEGER, n_compositions INTEGER, n_rahao INTEGER,
        n_angs INTEGER, first_ang INTEGER, last_ang INTEGER, first_line_id INTEGER,
        ang_mask TEXT, raags_json TEXT, signature_raags_json TEXT, outside_raag_verses INTEGER,
        chhap_count INTEGER, n_tokens INTEGER, mattr_100 REAL, words_per_verse REAL);
      DROP TABLE IF EXISTS author_mentions;
      CREATE TABLE author_mentions (
        line_id INTEGER, ang INTEGER, src_author TEXT, mentioned TEXT, form TEXT,
        PRIMARY KEY (line_id, mentioned));
      CREATE INDEX idx_am_mentioned ON author_mentions(mentioned);
      CREATE INDEX idx_am_src ON author_mentions(src_author);
      DROP TABLE IF EXISTS author_dialogues;
      CREATE TABLE author_dialogues (
        seq INTEGER PRIMARY KEY, bhagat TEXT, guru TEXT, ang INTEGER,
        bhagat_first_id INTEGER, bhagat_last_id INTEGER, guru_first_id INTEGER, guru_last_id INTEGER);
      CREATE INDEX idx_ad_bhagat ON author_dialogues(bhagat);
      CREATE INDEX idx_ad_guru ON author_dialogues(guru);
    ''')

    verses = [r for r in rows if not r[5] and r[3]]
    by_author = collections.defaultdict(list)
    for r in verses:
        by_author[r[3]].append(r)
    raag_voices = collections.defaultdict(set)
    for r in verses:
        if r[2]:
            raag_voices[r[2]].add(r[3])
    signature = {rg: next(iter(v)) for rg, v in raag_voices.items() if len(v) == 1}

    facts = []
    for author, vs in by_author.items():
        angs = {r[1] for r in vs}
        raags = collections.Counter(r[2] for r in vs if r[2])
        forms = ({'ਨਾਨਕ', 'ਨਾਨਕੁ', 'ਨਾਨਕਿ', 'ਨਾਨਕਾ'} if author.startswith('Guru ')
                 else set(NAMES.get(author, [])))
        # NULL (not measured) for voices whose pen-name forms are not curated (the Bhatts)
        chhap = sum(1 for r in vs if forms & set(words(r[7]))) if forms else None
        toks = [w for r in vs for w in words(r[7])]
        facts.append((author, len(vs), len({r[4] for r in vs}), sum(r[6] for r in vs),
                      len(angs), min(angs), max(angs), vs[0][0], mask_b64(angs),
                      json.dumps([{'raag': k, 'verses': n} for k, n in raags.most_common()], ensure_ascii=False),
                      json.dumps(sorted(k for k, a in signature.items() if a == author), ensure_ascii=False),
                      sum(1 for r in vs if not r[2]), chhap, len(toks), round(mattr(toks), 4),
                      round(len(toks) / len(vs), 2)))
    con.executemany('INSERT INTO author_facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', facts)

    # mentions: whole-word names; an ambiguous form (ਨਾਮਾ "the Name", ਧੰਨਾ "blessed" ...)
    # counts only beside another unambiguous saint's name -- a roll call of the devotees
    bhagat_form = {f: a for a, fs in NAMES.items() for f in fs}
    ment = []
    for r in verses:
        ws = words(r[7]); src = r[3]
        hits = {}
        for w in ws:
            a = bhagat_form.get(w)
            if a and a != src:
                hits.setdefault(a, w)
        sure = {a for a, w in hits.items() if w not in AMBIGUOUS}
        for a, w in hits.items():
            if w in AMBIGUOUS and not (sure - {a}):
                continue
            ment.append((r[0], r[1], src, a, w))
        if src.endswith(PRAISERS) or src in PRAISERS:
            for g, fs in GURU_FORMS.items():
                w = next((x for x in ws if x in fs), None)
                if w:
                    ment.append((r[0], r[1], src, g, w))
    con.executemany('INSERT OR IGNORE INTO author_mentions VALUES (?,?,?,?,?)', ment)

    # dialogues: salok units in the Kabir / Farid collections (Angs 1364-1384)
    units, cur = [], []
    for r in rows:
        if not (1364 <= r[1] <= 1384) or r[5]:
            continue
        cur.append(r)
        mk = json.loads(r[8]) if isinstance(r[8], str) else (r[8] or [])
        if any(GDIG.search(m) for m in mk):
            units.append(cur); cur = []
    # every Guru salok in a run that follows a Bhagat's salok is paired with THAT salok
    # (e.g. Ang 1376: ਮਃ ੩ and then ਮਃ ੫ both follow Kabir's salok 219)
    dia, anchor = [], None
    for u in units:
        a = u[0][3]
        if a and not a.startswith('Guru '):
            anchor = u
        elif a and anchor is not None:
            dia.append((len(dia) + 1, anchor[0][3], a, u[0][1], anchor[0][0], anchor[-1][0], u[0][0], u[-1][0]))
    con.executemany('INSERT INTO author_dialogues VALUES (?,?,?,?,?,?,?,?)', dia)
    return len(facts), len(ment), len(dia)


def distinctive_terms(con, top=15, min_count=4, min_tokens=400):
    """Monroe et al. log-odds with an informative Dirichlet prior, on Gurmukhi words."""
    con.executescript('''
      DROP TABLE IF EXISTS author_distinctive_terms;
      CREATE TABLE author_distinctive_terms (
        author TEXT, term TEXT, z_score REAL, count_author INTEGER, count_rest INTEGER,
        rank INTEGER, PRIMARY KEY (author, rank));
      CREATE INDEX idx_adt_author ON author_distinctive_terms(author, rank);''')
    toks = collections.defaultdict(collections.Counter)
    for author, text in con.execute('SELECT author, text FROM lines WHERE is_header=0 AND author IS NOT NULL'):
        toks[author].update(w for w in words(text) if w not in STOP and w not in SIGNS
                            and not w.startswith('ਨਾਨਕ') and len(w) > 1)
    glob = collections.Counter()
    for c in toks.values():
        glob.update(c)
    total, V, a0 = sum(glob.values()), len(glob), 0.01
    out = []
    for author, ca in sorted(toks.items()):
        na = sum(ca.values())
        if na < min_tokens:
            continue
        scored = []
        for w, cw in ca.items():
            if cw < min_count:
                continue
            cr, nr = glob[w] - cw, total - na
            la = math.log((cw + a0) / (na + a0 * V - cw - a0))
            lr = math.log((cr + a0) / (nr + a0 * V - cr - a0))
            scored.append(((la - lr) / math.sqrt(1 / (cw + a0) + 1 / (cr + a0)), w, cw, cr))
        scored.sort(key=lambda s: (-s[0], s[1]))
        out += [(author, w, round(z, 2), cw, cr, i) for i, (z, w, cw, cr) in enumerate(scored[:top], 1)]
    con.executemany('INSERT INTO author_distinctive_terms VALUES (?,?,?,?,?,?)', out)
    return len(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    db = ap.parse_args().db
    con = sqlite3.connect(db)
    nf, nm, nd = build(con)
    nt = distinctive_terms(con)
    con.commit(); con.close()
    print(f'author facts: {nf} voices, {nm} mentions, {nd} dialogues, {nt} Gurmukhi distinctive terms')
