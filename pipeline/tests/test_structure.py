# -*- coding: utf-8 -*-
"""Structure post-pass: each ledger kind on minimal records, the refusals that keep an entry from
applying to lines it was not written for, and spot checks on the committed corpus."""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import structure as S  # noqa: E402


def recs(spec):
    """spec: [(comp_id, is_header, section)] -> corpus-shaped records with dense ids and line_no."""
    out, seen = [], {}
    for i, (comp, hdr, sec) in enumerate(spec, 1):
        seen[comp] = seen.get(comp, 0) + 1
        out.append({'id': i, 'ang': 1, 'comp_id': comp, 'line_no': seen[comp], 'is_header': hdr,
                    'section': sec, 'text': f'line {i}', 'author': 'A'})
    return out


PENDING = {'item': 'T', 'decision': None, 'reviewer': None, 'date': None}


def opens(a, b, frm, to, status='held'):
    # held: applied without a ruling, as in a draft PR (test_g3_gate covers complete rulings)
    return {'entry': f'opens-{a}', 'kind': 'opens', 'start_id': a, 'end_id': b, 'from': frm, 'to': to,
            'status': status, 'g3': dict(PENDING)}


def section(a, b, frm, to):
    return {'entry': f'section-{a}', 'kind': 'section', 'start_id': a, 'end_id': b, 'from': frm,
            'to': to, 'status': 'held', 'g3': dict(PENDING)}


class Kinds(unittest.TestCase):
    def test_section_moves_only_the_range(self):
        r = recs([(1, 1, 'X'), (1, 0, 'X'), (2, 1, 'X'), (2, 0, 'X')])
        S.apply(r, [section(3, 4, 'X', 'Y')], issued=2)
        self.assertEqual([x['section'] for x in r], ['X', 'X', 'Y', 'Y'])

    def test_labels_open_compositions_above_every_issued_id(self):
        # one comp holding three shabads, each after the first opened by a bare label stored as a verse
        r = recs([(7, 1, None), (7, 0, None), (7, 0, None), (7, 0, None), (7, 0, None), (7, 0, None)])
        S.apply(r, [opens(3, 4, 7, 11), opens(5, 6, 7, 12)], issued=10)
        self.assertEqual([x['comp_id'] for x in r], [7, 7, 11, 11, 12, 12])
        self.assertEqual([x['is_header'] for x in r], [1, 0, 1, 0, 1, 0])
        self.assertEqual([x['line_no'] for x in r], [1, 2, 1, 2, 1, 2])

    def test_proposed_entries_change_nothing(self):
        r = recs([(7, 1, None), (7, 0, None), (7, 0, None)])
        before = json.dumps(r)
        log = S.apply(r, [opens(2, 3, 7, 11, status='proposed')], issued=10)
        self.assertEqual(log, [])
        self.assertEqual(json.dumps(r), before)

    def test_an_entry_cannot_apply_twice(self):
        r = recs([(7, 1, None), (7, 0, None), (7, 0, None)])
        S.apply(r, [opens(2, 3, 7, 11)], issued=10)
        with self.assertRaises(S.LedgerMismatch):
            S.apply(r, [opens(2, 3, 7, 11)], issued=10)


class Refusals(unittest.TestCase):
    def test_a_new_id_must_be_above_every_issued_id(self):
        r = recs([(7, 1, None), (7, 0, None), (7, 0, None)])
        with self.assertRaises(S.LedgerMismatch):
            S.apply(r, [opens(2, 3, 7, 9)], issued=10)      # 9 may be a burned id: never reuse it

    def test_the_expected_composition_must_match(self):
        r = recs([(7, 1, None), (7, 0, None), (8, 1, None)])
        with self.assertRaises(S.LedgerMismatch):
            S.apply(r, [opens(2, 3, 7, 11)], issued=10)

    def test_the_expected_section_must_match(self):
        r = recs([(1, 1, 'X'), (1, 0, 'Z')])
        with self.assertRaises(S.LedgerMismatch):
            S.apply(r, [section(1, 2, 'X', 'Y')], issued=1)

    def test_no_tail_is_left_behind(self):
        # moving lines 2-3 out of comp 7 would leave line 4 as a body line of 7 after them
        r = recs([(7, 1, None), (7, 0, None), (7, 0, None), (7, 0, None)])
        with self.assertRaises(S.LedgerMismatch):
            S.apply(r, [opens(2, 3, 7, 11)], issued=10)

    def test_a_header_is_not_reopened(self):
        r = recs([(7, 1, None), (7, 1, None), (7, 0, None)])
        with self.assertRaises(S.LedgerMismatch):
            S.apply(r, [opens(2, 3, 7, 11)], issued=10)


class Ledger(unittest.TestCase):
    def test_every_entry_is_well_formed(self):
        for e in S.load_ledger(os.path.join(ROOT, 'pipeline', 'structure_ledger.json')):
            with self.subTest(entry=e['entry']):
                self.assertIn(e['kind'], ('section', 'opens'))
                self.assertIn(e['status'], ('approved', 'held', 'proposed', 'rejected'))
                self.assertLessEqual(e['start_id'], e['end_id'])
                self.assertTrue(e['evidence'] and e['reason'])
                self.assertIn('item', e['g3'])


class Corpus(unittest.TestCase):
    """The committed corpus carries every structure-ledger entry a build applies (approved or held)."""
    @classmethod
    def setUpClass(cls):
        cls.by_id = {}
        for line in open(os.path.join(ROOT, 'corpus', 'sggs.jsonl'), encoding='utf-8'):
            r = json.loads(line)
            cls.by_id[r['id']] = r
        cls.ledger = S.load_ledger(os.path.join(ROOT, 'pipeline', 'structure_ledger.json'))

    def test_approved_entries_hold(self):
        for e in self.ledger:
            if e['status'] not in ('approved', 'held'):
                continue
            rows = [self.by_id[i] for i in range(e['start_id'], e['end_id'] + 1)]
            with self.subTest(entry=e['entry']):
                if e['kind'] == 'section':
                    self.assertTrue(all(r['section'] == e['to'] for r in rows))
                else:
                    self.assertTrue(all(r['comp_id'] == e['to'] for r in rows))
                    self.assertEqual(rows[0]['is_header'], 1)
                    self.assertEqual([r['line_no'] for r in rows], list(range(1, len(rows) + 1)))

    def test_compositions_stay_whole(self):
        # every comp_id is one contiguous run of ids, and opens with a heading
        first, last = {}, {}
        for i in sorted(self.by_id):
            c = self.by_id[i]['comp_id']
            first.setdefault(c, i)
            self.assertEqual(last.get(c, i - 1), i - 1, f'comp {c} is split around id {i}')
            last[c] = i
        self.assertTrue(all(self.by_id[i]['is_header'] for i in first.values()))


if __name__ == '__main__':
    unittest.main()
