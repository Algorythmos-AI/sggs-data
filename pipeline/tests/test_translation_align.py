# -*- coding: utf-8 -*-
"""Order-aware English alignment: spans, repeats, the repair pass, and the gate."""
import json, os, sqlite3, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
sys.path.insert(0, PIPE)
from translation_align import Line, Rec, align  # noqa: E402

# Ang 734, Soohee M4 (comp 2942): ShabadOS joins printed lines 9 and 10 into one record.
L734 = [
    (8, 734, 2942, 0, 'ਹਰਿ ਧਨੁ ਰਤਨੁ ਜਵੇਹਰੁ ਮਾਣਕੁ ਹਰਿ ਧਨੈ ਨਾਲਿ ਅੰਮ੍ਰਿਤ ਵੇਲੈ ਵਤੈ ਹਰਿ ਭਗਤੀ ਹਰਿ ਲਿਵ ਲਾਈ ॥'),
    (9, 734, 2942, 0, 'ਹਰਿ ਧਨੁ ਅੰਮ੍ਰਿਤ ਵੇਲੈ ਵਤੈ ਕਾ ਬੀਜਿਆ ਭਗਤ ਖਾਇ ਖਰਚਿ ਰਹੇ ਨਿਖੁਟੈ ਨਾਹੀ ॥'),
    (10, 734, 2942, 0, 'ਹਲਤਿ ਪਲਤਿ ਹਰਿ ਧਨੈ ਕੀ ਭਗਤਾ ਕਉ ਮਿਲੀ ਵਡਿਆਈ ॥੩॥'),
    (11, 734, 2942, 0, 'ਹਰਿ ਧਨੁ ਨਿਰਭਉ ਸਦਾ ਸਦਾ ਅਸਥਿਰੁ ਹੈ ਸਾਚਾ ॥'),
]
R734 = [
    (734, L734[0][4], 'JEWELS'),
    (734, L734[1][4] + ' ' + L734[2][4], 'SEED'),
    (734, L734[3][4], 'FEARLESS'),
]
# Japji-style refrain: identical text twice, one record per occurrence, in order.
LREP = [
    (20, 3, 1, 0, 'ਸੁਣਿਐ ਸਿਧ ਪੀਰ ਸੁਰਿ ਨਾਥ ॥'),
    (21, 3, 1, 0, 'ਨਾਨਕ ਭਗਤਾ ਸਦਾ ਵਿਗਾਸੁ ॥'),
    (22, 3, 1, 0, 'ਸੁਣਿਐ ਦੂਖ ਪਾਪ ਕਾ ਨਾਸੁ ॥੮॥'),
    (23, 3, 1, 0, 'ਸੁਣਿਐ ਸਤੁ ਸੰਤੋਖੁ ਗਿਆਨੁ ॥'),
    (24, 3, 1, 0, 'ਨਾਨਕ ਭਗਤਾ ਸਦਾ ਵਿਗਾਸੁ ॥'),
    (25, 3, 1, 0, 'ਸੁਣਿਐ ਦੂਖ ਪਾਪ ਕਾ ਨਾਸੁ ॥੯॥'),
]
RREP = [(3, t[4], f'EN{t[0]}') for t in LREP]


def run(lines, recs):
    ls = [Line(*t) for t in lines]
    rs = [Rec(i, a, g, e) for i, (a, g, e) in enumerate(recs)]
    placed, amb = align(rs, ls)
    return {tuple(x.id for x in run): (r.en, q) for r, run, q in placed}, amb


class AlignTests(unittest.TestCase):
    def test_span_ang_734(self):
        got, amb = run(L734, R734)
        self.assertEqual(got[(9, 10)], ('SEED', 'span'))
        self.assertEqual(got[(8,)], ('JEWELS', 'exact'))
        self.assertEqual(got[(11,)], ('FEARLESS', 'exact'))
        self.assertEqual(amb, [])

    def test_repeats_take_their_own_record(self):
        got, _ = run(LREP, RREP)
        for t in LREP:
            self.assertEqual(got[(t[0],)], (f'EN{t[0]}', 'exact'))

    def test_one_to_one_beats_a_span(self):
        # Both lines have their own records AND a joined record exists: 1:1 wins, joined unused.
        recs = [(734, L734[1][4], 'NINE'), (734, L734[1][4] + ' ' + L734[2][4], 'JOINED'), (734, L734[2][4], 'TEN')]
        got, _ = run(L734[1:3], recs)
        self.assertEqual(got, {(9,): ('NINE', 'exact'), (10,): ('TEN', 'exact')})

    def test_span_never_crosses_compositions_or_headings(self):
        lines = [(1, 5, 1, 0, 'ਕਬੀਰੁ'), (2, 5, 2, 1, 'ਮਾਰੂ'), (3, 5, 2, 0, 'ਰਾਮੁ ਸਿਮਰੁ ਪਛੁਤਾਹਿਗਾ ਮਨ ॥')]
        got, _ = run(lines, [(5, 'ਕਬੀਰੁ ॥ ਮਾਰੂ ॥', 'KABEER MAAROO'), (5, lines[2][4], 'REMEMBER')])
        self.assertNotIn((1, 2), got)
        self.assertEqual(got[(3,)], ('REMEMBER', 'exact'))

    def test_refrain_label_inside_a_span(self):
        lines = [(1, 9, 7, 0, 'ਹਰਿ ਧਨੁ ਸੰਚੀਐ ਭਾਈ ॥'), (2, 9, 7, 0, 'ਜਿ ਹਲਤਿ ਪਲਤਿ ਹਰਿ ਹੋਇ ਸਖਾਈ ॥੧॥ ਰਹਾਉ ॥')]
        got, _ = run(lines, [(9, 'ਹਰਿ ਧਨੁ ਸੰਚੀਐ ਭਾਈ ॥ ਜਿ ਹਲਤਿ ਪਲਤਿ ਹਰਿ ਹੋਇ ਸਖਾਈ ॥੧॥ ਰਹਾਉ ॥', 'GATHER')])
        self.assertEqual(got[(1, 2)], ('GATHER', 'span'))

    def test_far_ang_never_matches(self):
        got, _ = run([(1, 100, 1, 0, 'ਸਤਿ ਨਾਮੁ ॥')], [(300, 'ਸਤਿ ਨਾਮੁ ॥', 'X')])
        self.assertEqual(got, {})

    def test_tie_is_not_placed(self):
        # One record, two identical lines, nothing to tell them apart: place nothing.
        lines = [(1, 4, 1, 0, 'ਵਾਹੁ ਵਾਹੁ ॥'), (2, 4, 1, 0, 'ਵਾਹੁ ਵਾਹੁ ॥')]
        got, amb = run(lines, [(4, 'ਵਾਹੁ ਵਾਹੁ ॥', 'WAAHU')])
        self.assertEqual(got, {})
        self.assertEqual([why for _, why in amb], ['tie'])


class LoaderAndGateTests(unittest.TestCase):
    """End to end on a tiny DB: both loader passes, then the gate."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, 'db.sqlite')
        con = sqlite3.connect(self.db)
        con.executescript('CREATE TABLE lines(id INTEGER PRIMARY KEY, ang INT, comp_id INT, is_header INT, text TEXT);'
                          'CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);')
        con.executemany('INSERT INTO lines VALUES(?,?,?,?,?)', L734)
        con.commit(); con.close()
        self.src = os.path.join(self.tmp, 'translations'); os.makedirs(self.src)

    def write(self, name, recs):
        with open(os.path.join(self.src, name), 'w', encoding='utf-8') as f:
            for a, g, e in recs: f.write(json.dumps({'ang': a, 'gurmukhi': g, 'en': e}, ensure_ascii=False) + '\n')

    def sh(self, *args):
        return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=PIPE)

    def test_repair_pass_never_breaks_a_span_or_overwrites_with_a_joined_record(self):
        self.write('en_full_shabados.jsonl', R734)
        # The repair source joins 8+9 but translates only line 8, and re-translates the span lines.
        self.write('en_001_006.jsonl', [(734, L734[0][4] + ' ' + L734[1][4], 'HALF'), (734, L734[2][4], 'TEN ONLY')])
        r1 = self.sh('load_translations.py', self.db, '--source=ssk-shabados', os.path.join(self.src, 'en_full_shabados.jsonl'))
        self.assertEqual(r1.returncode, 0, r1.stderr)
        r2 = self.sh('load_translations.py', self.db, os.path.join(self.src, 'en_0*.jsonl'))
        self.assertEqual(r2.returncode, 0, r2.stderr)
        con = sqlite3.connect(self.db)
        rows = dict(con.execute("SELECT line_id, text FROM translations"))
        spans = con.execute('SELECT first_line_id, last_line_id FROM translation_spans').fetchall()
        self.assertEqual(rows, {8: 'JEWELS', 10: 'SEED', 11: 'FEARLESS'})
        self.assertEqual(spans, [(9, 10)])
        g = self.sh('translation_alignment_gate.py', self.db, '--sources', self.src)
        self.assertEqual(g.returncode, 0, g.stdout + g.stderr)

    def test_gate_fails_on_a_member_with_its_own_english(self):
        self.write('en_full_shabados.jsonl', R734); self.write('en_001_006.jsonl', [])
        self.sh('load_translations.py', self.db, '--source=ssk-shabados', os.path.join(self.src, 'en_full_shabados.jsonl'))
        con = sqlite3.connect(self.db)
        con.execute("INSERT INTO translations VALUES(9,'en','ssk-shabados','WRONG','exact')"); con.commit(); con.close()
        g = self.sh('translation_alignment_gate.py', self.db, '--sources', self.src)
        self.assertEqual(g.returncode, 1)
        self.assertIn('member 9 has its own English', g.stdout)


if __name__ == '__main__':
    unittest.main()
