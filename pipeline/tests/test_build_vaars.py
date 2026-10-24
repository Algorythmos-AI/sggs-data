# -*- coding: utf-8 -*-
"""Vaar anatomy: the label grammar and heading rules on minimal lines, plus the printed
structure of all 22 Vaars on the committed DB (each count read from the print: label lines and
the ॥N॥ each pauri closes with — the same proof the iOS reader runs)."""
import os, sqlite3, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import build_vaars as V  # noqa: E402

DB = os.path.join(ROOT, 'db', 'sggs.sqlite')


def line(t, header=0, pada=0, i=1):
    return {'id': i, 'gurmukhi': t, 'is_header': header, 'pada_total': pada}


class Labels(unittest.TestCase):
    def test_salok_labels(self):
        self.assertTrue(V.is_salok_label(line('ਸਲੋਕੁ ਮਃ ੧ ॥', 1)))
        self.assertTrue(V.is_salok_label(line('ਡਖਣੇ ਮਃ ੫ ॥', 1)), "Maru M5's inner ਡਖਣੇ saloks")
        self.assertTrue(V.is_salok_label(line('ਮਰਦਾਨਾ ੧ ॥', 0, 1)), 'an unflagged short rubric')
        self.assertFalse(V.is_salok_label(line('ਮਃ ੧ ॥੨॥', 1)), 'a verse number is never a label')
        self.assertFalse(V.is_salok_label(line('ਸਲੋਕ ਪੜਿ ਪੜਿ ਪੰਡਿਤ ਥਕੇ ॥', 0, 1)), 'a verse that opens with a label word')

    def test_dhuni_rubric(self):
        self.assertTrue(V.is_dhuni_rubric('ਜੋਧੈ ਵੀਰੈ ਪੂਰਬਾਣੀ ਕੀ ਧੁਨੀ ॥'))
        self.assertTrue(V.is_dhuni_rubric('ਲਲਾਂ ਬਹਲੀਮਾ ਕੀ ਧੁਨਿ ਗਾਵਣੀ'))
        self.assertFalse(V.is_dhuni_rubric('ਅਨਹਦ ਧੁਨਿ ਵਾਜੇ ॥੩॥'), 'a numbered verse is never a rubric')

    def test_heading_title_skips_the_invocation(self):
        run = [line('ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥', 1, i=1), line('ਰਾਮਕਲੀ ਕੀ ਵਾਰ ਮਹਲਾ ੩ ॥', 1, i=2),
               line('ਜੋਧੈ ਵੀਰੈ ਪੂਰਬਾਣੀ ਕੀ ਧੁਨੀ ॥', 0, 1, i=3), line('ਸਲੋਕੁ ਮਃ ੩ ॥', 1, i=4),
               line('ਸਤਿਗੁਰੁ ਸਹਜੈ ਦਾ ਖੇਤੁ ਹੈ ॥', 0, 1, i=5)]
        self.assertEqual(V.heading_title(run), 'ਰਾਮਕਲੀ ਕੀ ਵਾਰ ਮਹਲਾ ੩ ॥ ਜੋਧੈ ਵੀਰੈ ਪੂਰਬਾਣੀ ਕੀ ਧੁਨੀ')


@unittest.skipUnless(os.path.exists(DB) and open(DB, 'rb').read(16).startswith(b'SQLite format 3'),
                     'db/sggs.sqlite not installed (git lfs pull)')
class PrintedStructure(unittest.TestCase):
    """vaar_id → (pauris, saloks) as printed."""
    PRINTED = {1: (21, 43), 2: (27, 63), 3: (33, 68), 4: (21, 42), 5: (24, 59), 6: (22, 44),
               7: (21, 42), 8: (21, 42), 9: (21, 43), 10: (29, 58), 11: (20, 20), 12: (20, 47),
               13: (13, 27), 14: (21, 52), 15: (22, 44), 16: (8, 0), 17: (22, 47), 18: (23, 69),
               19: (3, 0), 20: (36, 74), 21: (28, 58), 22: (15, 30)}

    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(f'file:{DB}?mode=ro&immutable=1', uri=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_counts_match_the_print(self):
        got = {v: (p, s) for v, p, s in self.db.execute('SELECT vaar_id, n_pauris, n_saloks FROM vaars')}
        self.assertEqual(got, self.PRINTED)
        self.assertEqual(self.db.execute('SELECT count(*) FROM vaar_units').fetchone()[0], 471 + 972)

    def test_no_title_is_the_invocation(self):
        rows = self.db.execute("SELECT vaar_id FROM vaars WHERE title LIKE 'ੴ%' OR title NOT LIKE '%ਵਾਰ%'").fetchall()
        self.assertEqual(rows, [])

    def test_the_last_pauri_ends_with_its_composition(self):
        for vid, cid, first, n in self.db.execute(
                'SELECT vaar_id, comp_id, first_line_id, n_lines FROM vaar_units u WHERE seq = '
                '(SELECT max(seq) FROM vaar_units WHERE vaar_id = u.vaar_id)'):
            last = self.db.execute('SELECT max(id) FROM lines WHERE comp_id = ?', (cid,)).fetchone()[0]
            self.assertLessEqual(first + n - 1, last, f'vaar {vid}: the last pauri runs past its composition')


if __name__ == '__main__':
    unittest.main()
