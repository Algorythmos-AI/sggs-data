# -*- coding: utf-8 -*-
"""attribution_pass.py: the traps it must not fall into, and the corpus as a fixed point.
Synthetic fixtures use real print conventions; nothing here edits scripture."""
import json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import attribution_pass as ap

M5, M3 = 'Guru Arjan Dev Ji (M5)', 'Guru Amar Das Ji (M3)'


def rec(i, text, author, markers=(), header=0, raag='ਆਸਾ', ang=487, comp=1):
    return {'id': i, 'ang': ang, 'raag': raag, 'author': author, 'comp_id': comp,
            'is_header': header, 'markers': list(markers), 'text': text}


def run(records, ledger=None):
    log = ap.apply(records, ledger or {})
    return {r['id']: r['author'] for r in records}, log


class BhagatShabads(unittest.TestCase):
    def test_title_plus_signature_reattributes(self):
        rs = [rec(1, 'ਆਸਾ ਬਾਣੀ ਭਗਤ ਧੰਨੇ ਜੀ ਕੀ', 'Bhagat Ravidas Ji', header=1),
              rec(2, 'ਭ੍ਰਮਤ ਫਿਰਤ ਬਹੁ ਜਨਮ ਬਿਲਾਨੇ', 'Bhagat Ravidas Ji', ['੧']),
              rec(3, 'ਧੰਨੈ ਧਨੁ ਪਾਇਆ ਧਰਣੀਧਰੁ', 'Bhagat Ravidas Ji', ['੪', '੧'])]
        got, _ = run(rs)
        self.assertEqual(set(got.values()), {'Bhagat Dhanna Ji'})

    def test_signature_without_rubric_is_never_enough(self):
        rs = [rec(1, 'ਆਸਾ', 'Bhagat Ravidas Ji', header=1),
              rec(2, 'ਕੋਈ ਤੁਕ', 'Bhagat Ravidas Ji', ['੧']),
              rec(3, 'ਕਹੈ ਧੰਨਾ ਪੂਰਨ ਤਾਹੂ ਕੋ', 'Bhagat Ravidas Ji', ['੨', '੧'])]
        got, log = run(rs)
        self.assertEqual(log, [])

    def test_name_in_body_is_not_evidence(self):
        # Ravidas praising other Bhagats in the body; his own signature closes the shabad
        rs = [rec(1, 'ਰਾਗੁ ਮਾਰੂ ਬਾਣੀ ਰਵਿਦਾਸ ਜੀਉ ਕੀ', 'Bhagat Ravidas Ji', header=1, raag='ਮਾਰੂ'),
              rec(2, 'ਨਾਮਦੇਵ ਕਬੀਰੁ ਤਿਲੋਚਨੁ ਸਧਨਾ ਸੈਨੁ ਤਰੈ', 'Bhagat Ravidas Ji', raag='ਮਾਰੂ'),
              rec(3, 'ਕਹਿ ਰਵਿਦਾਸੁ ਸੁਨਹੁ ਰੇ ਸੰਤਹੁ', 'Bhagat Ravidas Ji', ['੨', '੧'], raag='ਮਾਰੂ')]
        _, log = run(rs)
        self.assertEqual(log, [])

    def test_guru_heading_wins_over_a_bhagat_signature(self):
        # ਸਾਰੰਗ ਮਹਲਾ ੫ ਸੂਰਦਾਸ / ਭੈਰਉ ਮਹਲਾ ੫ … ਕਹੁ ਕਬੀਰ: the print's ਮਹਲਾ is kept
        rs = [rec(1, 'ਗਉੜੀ ਕਬੀਰ ਜੀ ਕੀ ਨਾਲਿ ਰਲਾਇ ਲਿਖਿਆ ਮਹਲਾ ੫', M5, header=1, raag='ਗਉੜੀ'),
              rec(2, 'ਐਸੋ ਅਚਰਜੁ ਦੇਖਿਓ ਕਬੀਰ', M5, ['੧', 'ਰਹਾਉ'], raag='ਗਉੜੀ'),
              rec(3, 'ਕਹੁ ਕਬੀਰ ਗੁਰਿ ਸੋਝੀ ਪਾਈ', M5, ['੪', '੧', '੧੪'], raag='ਗਉੜੀ')]
        _, log = run(rs)
        self.assertEqual(log, [])

    def test_bare_name_rubric_inside_one_comp(self):
        # Ang 695: Sain, Pipa, Dhanna share one comp_id; each opens with a bare-name line
        rs = [rec(1, 'ਸ੍ਰੀ ਸੈਣੁ', 'Bhagat Trilochan Ji', ang=695, raag='ਧਨਾਸਰੀ'),
              rec(2, 'ਧੂਪ ਦੀਪ ਘ੍ਰਿਤ ਸਾਜਿ ਆਰਤੀ', 'Bhagat Trilochan Ji', ang=695, raag='ਧਨਾਸਰੀ'),
              rec(3, 'ਸੈਨੁ ਭਣੈ ਭਜੁ ਪਰਮਾਨੰਦੇ', 'Bhagat Trilochan Ji', ['੪', '੨'], ang=695, raag='ਧਨਾਸਰੀ'),
              rec(4, 'ਪੀਪਾ', 'Bhagat Trilochan Ji', ang=695, raag='ਧਨਾਸਰੀ'),
              rec(5, 'ਕਾਯਉ ਦੇਵਾ ਕਾਇਅਉ ਦੇਵਲ', 'Bhagat Trilochan Ji', ang=695, raag='ਧਨਾਸਰੀ'),
              rec(6, 'ਪੀਪਾ ਪ੍ਰਣਵੈ ਪਰਮ ਤਤੁ ਹੈ', 'Bhagat Trilochan Ji', ['੨', '੩'], ang=695, raag='ਧਨਾਸਰੀ')]
        got, _ = run(rs)
        self.assertEqual([got[i] for i in range(1, 7)],
                         ['Bhagat Sain Ji'] * 3 + ['Bhagat Pipa Ji'] * 3)
        self.assertEqual({r['comp_id'] for r in rs}, {1})          # grouping untouched

    def test_block_title_carries_past_an_interleaved_guru_shabad(self):
        # Ang 487-488: Dhanna, then M5's shabad about Dhanna, then Dhanna again (no new heading)
        rs = [rec(1, 'ਆਸਾ ਬਾਣੀ ਭਗਤ ਧੰਨੇ ਜੀ ਕੀ', 'Bhagat Ravidas Ji', header=1),
              rec(2, 'ਧੰਨੈ ਧਨੁ ਪਾਇਆ ਧਰਣੀਧਰੁ', 'Bhagat Ravidas Ji', ['੪', '੧']),
              rec(3, 'ਮਹਲਾ ੫', M5, header=1),
              rec(4, 'ਮਿਲੇ ਪ੍ਰਤਖਿ ਗੁਸਾਈਆ ਧੰਨਾ ਵਡਭਾਗਾ', M5, ['੪', '੨']),
              rec(5, 'ਰੇ ਚਿਤ ਚੇਤਸਿ ਕੀ ਨ ਦਯਾਲ', M5, ['੧', 'ਰਹਾਉ']),
              rec(6, 'ਕਹੈ ਧੰਨਾ ਪੂਰਨ ਤਾਹੂ ਕੋ', M5, ['੩', '੩'])]
        got, _ = run(rs)
        self.assertEqual(got[3], M5); self.assertEqual(got[4], M5)   # the Guru's shabad stays
        self.assertEqual(got[5], 'Bhagat Dhanna Ji'); self.assertEqual(got[6], 'Bhagat Dhanna Ji')

    def test_parmanand_is_not_a_signature(self):
        # ਪਰਮਾਨੰਦ is an ordinary word too; it is only ever attributed through the ledger
        self.assertNotIn('ਪਰਮਾਨੰਦ', ap.FORM_TO_AUTHOR)
        self.assertNotIn('ਪਰਮਾਨੰਦੇ', ap.FORM_TO_AUTHOR)


class SalokScope(unittest.TestCase):
    def test_guru_label_covers_its_own_salok_only(self):
        F = 'Sheikh Farid Ji'
        rs = [rec(1, 'ਸਲੋਕ ਸੇਖ ਫਰੀਦ ਕੇ', F, header=1, raag=None, ang=1377),
              rec(2, 'ਫਰੀਦਾ ਪਹਿਲੀ ਤੁਕ', F, ['੧੨'], raag=None, ang=1378),
              rec(3, 'ਮਃ ੩', M3, header=1, raag=None, ang=1378),
              rec(4, 'ਫਰੀਦਾ ਕਾਲੀ ਧਉਲੀ ਸਾਹਿਬੁ', M3, raag=None, ang=1378),
              rec(5, 'ਗੁਰ ਕੀ ਤੁਕ', M3, ['੧੩'], raag=None, ang=1378),
              rec(6, 'ਫਰੀਦਾ ਅਗਲੀ ਤੁਕ', M3, raag=None, ang=1378),
              rec(7, 'ਫਰੀਦਾ ਦੂਜੀ ਤੁਕ', M3, ['੧੪'], raag=None, ang=1378)]
        got, _ = run(rs)
        self.assertEqual([got[i] for i in range(1, 8)], [F, F, M3, M3, M3, F, F])


class Ledger(unittest.TestCase):
    def test_guard_refuses_a_moved_corpus(self):
        rs = [rec(1, 'ਕੋਈ ਤੁਕ', 'Bhagat Namdev Ji')]
        led = {'decisions': [{'key': 'k', 'action': 'set_author', 'ids': [1, 1],
                              'author': 'Bhagat Surdas Ji', 'expect_author': [M5]}]}
        with self.assertRaises(SystemExit):
            ap.apply(rs, led)

    def test_ledger_is_idempotent(self):
        rs = [rec(1, 'ਕੋਈ ਤੁਕ', 'Bhagat Namdev Ji')]
        led = {'decisions': [{'key': 'k', 'action': 'set_author', 'ids': [1, 1],
                              'author': 'Bhagat Surdas Ji', 'expect_author': ['Bhagat Namdev Ji']}]}
        self.assertEqual(len(ap.apply(rs, led)), 1)
        self.assertEqual(ap.apply(rs, led), [])

    def test_ledger_file_is_well_formed(self):
        with open(os.path.join(ROOT, 'pipeline', 'attribution_decisions.json'), encoding='utf-8') as f: led = json.load(f)
        keys = [d['key'] for d in led['decisions'] + led['flags']]
        self.assertEqual(len(keys), len(set(keys)))
        for d in led['decisions']:
            self.assertEqual(d['action'], 'set_author')
            self.assertLessEqual(d['ids'][0], d['ids'][1])
            for f in ('author', 'expect_author', 'evidence', 'review'): self.assertIn(f, d)


class CommittedCorpus(unittest.TestCase):
    CORPUS = os.path.join(ROOT, 'corpus', 'sggs.jsonl')

    @unittest.skipUnless(os.path.exists(CORPUS), 'corpus not present')
    def test_corpus_is_a_fixed_point_of_the_pass(self):
        """The committed corpus already carries every attribution: re-running the pass with
        the committed ledger changes nothing (a hand edit or a stale corpus fails here)."""
        with open(self.CORPUS, encoding='utf-8') as f: recs = [json.loads(l) for l in f]
        with open(os.path.join(ROOT, 'pipeline', 'attribution_decisions.json'), encoding='utf-8') as f: led = json.load(f)
        self.assertEqual(ap.apply(recs, led), [])

    @unittest.skipUnless(os.path.exists(CORPUS), 'corpus not present')
    def test_every_bhagat_of_the_granth_has_bani(self):
        with open(self.CORPUS, encoding='utf-8') as f: recs = [json.loads(l) for l in f]
        authors = {r['author'] for r in recs}
        for name in ('Bhagat Dhanna Ji', 'Bhagat Pipa Ji', 'Bhagat Sain Ji', 'Bhagat Sadhna Ji',
                     'Bhagat Parmanand Ji', 'Bhagat Surdas Ji', 'Baba Sundar Ji', 'Bhagat Jaidev Ji'):
            self.assertIn(name, authors)
        self.assertNotIn(None, authors)


if __name__ == '__main__':
    unittest.main()
