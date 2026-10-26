# -*- coding: utf-8 -*-
"""Attribution post-pass: each rule on a minimal composition, plus spot checks on the
committed corpus (who composed the verses the 2026-10-23 audit found mis-tagged)."""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import attribution as A  # noqa: E402

M3, M5 = 'Guru Amar Das Ji (M3)', 'Guru Arjan Dev Ji (M5)'


def recs(spec, author):
    """spec: [(text, is_header, markers)] -> corpus-shaped records, all tagged `author`
    (the bleed the pass repairs), each heading opening a new comp like build_corpus."""
    out, comp = [], 0
    for i, (text, hdr, markers) in enumerate(spec, 1):
        if hdr and (not out or not out[-1]['is_header']):
            comp += 1
        out.append({'id': i, 'ang': 1, 'comp_id': comp or 1, 'is_header': hdr, 'text': text,
                    'markers': markers, 'author': author, 'gurmukhi': text})
    return out


class Rules(unittest.TestCase):
    def test_heading_names_an_inflected_bhagat(self):
        r = recs([('ਆਸਾ ਬਾਣੀ ਭਗਤ ਧੰਨੇ ਜੀ ਕੀ', 1, []), ('ਭ੍ਰਮਤ ਫਿਰਤ ਬਹੁ ਜਨਮ ਬਿਲਾਨੇ', 0, []),
                  ('ਧੰਨੈ ਧਨੁ ਪਾਇਆ ਧਰਣੀਧਰੁ', 0, ['੪', '੧'])], 'Bhagat Ravidas Ji')
        A.apply(r)
        self.assertTrue(all(x['author'] == 'Bhagat Dhanna Ji' for x in r))

    def test_bare_label_opens_a_shabad(self):
        r = recs([('ਧਨਾਸਰੀ ਬਾਣੀ ਭਗਤਾਂ ਕੀ', 1, []), ('ਤ੍ਰਿਲੋਚਨ ਦੀ ਪੰਗਤਿ', 0, []),
                  ('ਬਦਤਿ ਤ੍ਰਿਲੋਚਨ ਰਾਮ ਜੀ', 0, ['੬', '੧']), ('ਪੀਪਾ', 0, []), ('ਕਾਇਉ ਦੇਵਾ', 0, []),
                  ('ਪੀਪਾ ਪ੍ਰਣਵੈ ਪਰਮ ਤਤੁ ਹੈ', 0, ['੨', '੩'])], 'Bhagat Trilochan Ji')
        A.apply(r)
        self.assertEqual([x['author'] for x in r[3:]], ['Bhagat Pipa Ji'] * 3)
        self.assertEqual(r[2]['author'], 'Bhagat Trilochan Ji')

    def test_mahalla_label_covers_one_salok_in_a_collection(self):
        r = recs([('ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ', 1, []), ('ਫਰੀਦਾ ਪਹਿਲੀ', 0, ['੧']),
                  ('ਮਃ ੩', 1, []), ('ਗੁਰੂ ਦਾ ਸਲੋਕੁ', 0, ['੨']),
                  ('ਫਰੀਦਾ ਤੀਜੀ', 0, []), ('ਦੂਜੀ ਤੁਕ', 0, ['੩'])], M3)
        A.apply(r)
        self.assertEqual([x['author'] for x in r],
                         ['Sheikh Farid Ji', 'Sheikh Farid Ji', M3, M3, 'Sheikh Farid Ji', 'Sheikh Farid Ji'])

    def test_a_mahalla_heading_wins_over_a_named_bhagat(self):
        r = recs([('ਗਉੜੀ ਕਬੀਰ ਜੀ ਕੀ ਨਾਲਿ ਰਲਾਇ ਲਿਖਿਆ ਮਹਲਾ ੫', 1, []), ('ਐਸੋ ਅਚਰਜੁ ਦੇਖਿਓ ਕਬੀਰ', 0, []),
                  ('ਕਹੁ ਕਬੀਰ ਗੁਰਿ ਸੋਝੀ ਪਾਈ', 0, ['੪', '੧', '੧੪'])], M5)
        A.apply(r)
        self.assertTrue(all(x['author'] == M5 for x in r))

    def test_numbered_pauri_names_its_mahalla(self):
        r = recs([('ਪਉੜੀ ੫', 1, []), ('ਲੈ ਫਾਹੇ ਰਾਤੀ ਤੁਰਹਿ', 0, ['੨੭'])], 'Guru Ram Das Ji (M4)')
        A.apply(r)
        self.assertTrue(all(x['author'] == M5 for x in r))

    def test_ordinary_words_are_not_signatures(self):
        # ਨਾਮੇ = "in the Name" inside a Guru's pauri: never Namdev
        r = recs([('ਪਉੜੀ', 1, []), ('ਪੀਵਤਿ ਅੰਮ੍ਰਿਤ ਨਾਮੁ ਜਨ ਨਾਮੇ ਰਹੇ ਅਘਾਇ', 0, ['੧੪'])], M5)
        A.apply(r)
        self.assertEqual(r[1]['author'], M5)

    def test_numbered_series_carries_its_signature(self):
        r = recs([('ਟੋਡੀ ਬਾਣੀ ਭਗਤਾਂ ਕੀ', 1, []), ('ਕੋਈ ਬੋਲੈ ਨਿਰਵਾ', 0, ['੨', '੧']),
                  ('ਦੂਜਾ ਸਬਦੁ', 0, ['੨', '੨']), ('ਨਾਮਾ ਕਹੈ ਤਤੁ', 0, ['੪', '੩'])],
                 'Guru Tegh Bahadur Ji (M9)')
        A.apply(r)
        self.assertTrue(all(x['author'] == 'Bhagat Namdev Ji' for x in r))

    def test_never_moves_one_bhagat_to_another_without_evidence(self):
        # an unsigned shabad later in a Namdev section, tagged Ravidas: the section's name
        # alone is not evidence enough to move it from one Bhagat to another
        r = recs([('ਰਾਗੁ ਸੋਰਠਿ ਬਾਣੀ ਭਗਤ ਨਾਮਦੇ ਜੀ ਕੀ', 1, []), ('ਪਹਿਲਾ ਸਬਦੁ', 0, []),
                  ('ਕਹਿ ਨਾਮਾ ਤਤੁ', 0, ['੩', '੧']), ('ਗਉੜੀ ਬੈਰਾਗਣਿ', 1, []),
                  ('ਸਤਜੁਗਿ ਸਤੁ', 0, []), ('ਤਾ ਤੇ ਰਵਿਦਾਸ ਉਦਾਸ', 0, ['੮', '੧'])], 'Bhagat Ravidas Ji')
        A.apply(r)
        self.assertEqual(r[2]['author'], 'Bhagat Namdev Ji')
        self.assertEqual(r[5]['author'], 'Bhagat Ravidas Ji')

    def test_idempotent(self):
        r = recs([('ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ', 1, []), ('ਫਰੀਦਾ ਪਹਿਲੀ', 0, ['੧'])], M3)
        A.apply(r)
        log, _ = A.apply(r)
        self.assertEqual(log, [])


class Corpus(unittest.TestCase):
    """The committed corpus carries the repaired attribution."""
    @classmethod
    def setUpClass(cls):
        p = os.path.join(ROOT, 'corpus', 'sggs.jsonl')
        cls.by_id = {}
        for line in open(p, encoding='utf-8'):
            r = json.loads(line)
            cls.by_id[r['id']] = r

    def who(self, needle, ang):
        hits = [r for r in self.by_id.values() if r['ang'] == ang and needle in r['gurmukhi']]
        self.assertTrue(hits, f'not found on Ang {ang}: {needle}')
        return hits[0]['author']

    def test_spot_checks(self):
        cases = [
            ('ਫਰੀਦਾ ਬਾਰਿ ਪਰਾਇਐ ਬੈਸਣਾ', 1380, 'Sheikh Farid Ji'),
            ('ਇਹੁ ਤਨੁ ਸਭੋ ਰਤੁ ਹੈ', 1380, M3),
            ('ਐਸੋ ਅਚਰਜੁ ਦੇਖਿਓ ਕਬੀਰ', 326, M5),
            ('ਜਨੁ ਧੰਨਾ ਲੇਵੈ ਮੰਗੀ', 695, 'Bhagat Dhanna Ji'),
            ('ਸੈਨੁ ਭਣੈ ਭਜੁ ਪਰਮਾਨੰਦੇ', 695, 'Bhagat Sain Ji'),
            ('ਪੀਪਾ ਪ੍ਰਣਵੈ ਪਰਮ ਤਤੁ ਹੈ', 695, 'Bhagat Pipa Ji'),
            ('ਅਉਸਰ ਲਜਾ ਰਾਖਿ ਲੇਹੁ ਸਧਨਾ ਜਨੁ ਤੋਰਾ', 858, 'Bhagat Sadhna Ji'),
            ('ਬਦਤਿ ਜੈਦੇਉ ਜੈਦੇਵ ਕਉ ਰੰਮਿਆ', 1106, 'Bhagat Jaidev Ji'),
            ('ਪਰਮਾਨੰਦ ਸਾਧਸੰਗਤਿ ਮਿਲਿ', 1253, 'Bhagat Parmanand Ji'),
            ('ਕਹੈ ਸੁੰਦਰੁ ਸੁਣਹੁ ਸੰਤਹੁ', 924, 'Baba Sundar Ji'),
            ('ਆਦਿ ਸਚੁ ਜੁਗਾਦਿ ਸਚੁ', 1, 'Guru Nanak Dev Ji (M1)'),
            ('ਵਰਤ ਨ ਰਹਉ ਨ ਮਹ ਰਮਦਾਨਾ', 1136, M5),
            ('ਸੂਰਦਾਸ ਮਨੁ ਪ੍ਰਭਿ ਹਥਿ ਲੀਨੋ', 1253, M5),
            # held for G3 (A-07, A-11): applied by approved ledger entries
            ('ਛਾਡਿ ਮਨ ਹਰਿ ਬਿਮੁਖਨ ਕੋ ਸੰਗੁ', 1253, 'Bhagat Surdas Ji'),
            ('ਸੁਧੁ ਰਾਗੁ ਗੂਜਰੀ ਭਗਤਾ ਕੀ ਬਾਣੀ', 524, 'Bhagat Kabir Ji'),
        ]
        for needle, ang, want in cases:
            with self.subTest(ang=ang, line=needle):
                self.assertEqual(self.who(needle, ang), want)

    def test_contested_lines_are_unchanged(self):
        # proposed ledger entries change nothing until a scholar approves them
        self.assertEqual(self.who('ਕਲਿ ਕਲਵਾਲੀ ਕਾਮੁ ਮਦੁ', 553), 'Bhai Mardana')
        self.assertEqual(self.who('ਰਾਗ ਏਕ ਸੰਗਿ ਪੰਚ ਬਰੰਗਨ', 1429), M5)
        self.assertEqual(self.who('ਸੁਧੁ ਕੀਚੇ ਰਾਗੁ ਗਉੜੀ ਭਗਤਾਂ ਕੀ ਬਾਣੀ', 323), M5)


if __name__ == '__main__':
    unittest.main()
