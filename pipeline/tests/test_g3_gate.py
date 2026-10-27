# -*- coding: utf-8 -*-
"""The G3 approval gate (pipeline/g3_gate.py): incomplete or invalid rulings fail the build, held
entries never pass the release check, and a complete ruling -- in a temporary fixture only, never in
the committed ledgers -- is accepted. The committed ledgers are checked as they really are."""
import copy, datetime, io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import g3_gate as G  # noqa: E402
import attribution as A  # noqa: E402
import structure as S  # noqa: E402

TODAY = datetime.date(2026, 10, 27)
EVIDENCE = 'validation/attribution-g3-review/SIGN-OFF.md'


def real(kind):
    return G.read(G.LEDGERS[kind])


def ruled(e, decision='approve', status='approved', **over):
    """A complete ruling on entry e, for a fixture. The reviewer is the fixture name."""
    e = copy.deepcopy(e)
    e['status'] = status
    e['g3'] = dict(e.get('g3') or {'item': 'T'}, decision=decision, reviewer=G.FIXTURE_REVIEWER,
                   date='2026-10-01', scope=(e.get('g3') or {'item': 'T'})['item'], evidence=EVIDENCE,
                   entry_sha256=G.entry_sha256(e))
    e['g3'].update(over)
    return e


class Fixture(unittest.TestCase):
    """A temporary repo root holding the evidence file, so `evidence` resolves."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.tmp.name, 'validation', 'attribution-g3-review'))
        open(os.path.join(self.tmp.name, EVIDENCE), 'w').close()
        self.surdas = next(e for e in real('attribution') if e['entry'] == 'surdas-line')
        self.sain = next(e for e in real('structure') if e['entry'] == 'ang695-sain-opens')

    def tearDown(self):
        self.tmp.cleanup()

    def bad(self, entries, kind='attribution', **kw):
        return G.problems(entries, kind, root=self.tmp.name, today=TODAY, allow_fixture=True, **kw)


class CompleteRulings(Fixture):
    def test_a_complete_approval_is_accepted_and_applied(self):
        for kind, e in (('attribution', self.surdas), ('structure', self.sain)):
            with self.subTest(kind=kind):
                ok = ruled(e)
                self.assertEqual(self.bad([ok], kind), [])
                applied = G.check([ok], kind, root=self.tmp.name, today=TODAY, allow_fixture=True)
                self.assertEqual([x['entry'] for x in applied], [e['entry']])

    def test_change_is_an_approval_and_reject_a_rejection(self):
        self.assertEqual(self.bad([ruled(self.surdas, decision='change')]), [])
        rej = ruled(self.surdas, decision='reject', status='rejected')
        self.assertEqual(self.bad([rej]), [])
        self.assertEqual(G.check([rej], 'attribution', root=self.tmp.name, today=TODAY,
                                 allow_fixture=True), [])

    def test_a_complete_fixture_passes_the_release_check_logic(self):
        self.assertEqual(G.outstanding([ruled(self.surdas)]), [])


class IncompleteRulings(Fixture):
    def assertRefused(self, entry, why, kind='attribution'):
        msgs = self.bad([entry], kind)
        self.assertTrue(any(why in m for m in msgs), f'{why!r} not in {msgs}')

    def test_the_committed_state_approved_with_a_blank_ruling_is_refused(self):
        # exactly what PR #17 shipped before the gate: approved, g3 decision/reviewer/date null
        e = copy.deepcopy(self.surdas)
        e['status'] = 'approved'
        self.assertRefused(e, 'g3.decision')
        self.assertRefused(e, 'g3.reviewer is required')
        with self.assertRaises(G.GateError):
            A.apply([{'id': 53935, 'ang': 1253, 'comp_id': 1, 'is_header': 0, 'text': 'x',
                      'markers': [], 'author': 'Bhagat Namdev Ji'}], [e])

    def test_the_structure_pass_refuses_an_incomplete_approval(self):
        e = copy.deepcopy(self.sain)
        e['status'] = 'approved'
        r = [{'id': i, 'ang': 695, 'comp_id': 2749, 'line_no': i - e['start_id'] + 2, 'is_header': 0,
              'section': None, 'text': 'x', 'author': 'A'} for i in range(e['start_id'], e['end_id'] + 1)]
        with self.assertRaises(G.GateError):
            S.apply(r, [e], issued=5380)
        self.assertTrue(all(x['comp_id'] == 2749 for x in r))     # nothing applied

    def test_both_ledger_loaders_validate(self):
        for mod, kind, e in ((A, 'attribution', self.surdas), (S, 'structure', self.sain)):
            bad = dict(copy.deepcopy(e), status='approved')          # blank ruling
            p = os.path.join(self.tmp.name, f'{kind}.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({'entries': [bad]}, f, ensure_ascii=False)
            with self.subTest(kind=kind), self.assertRaises(G.GateError):
                mod.load_ledger(p)

    def test_missing_reviewer(self):
        self.assertRefused(ruled(self.surdas, reviewer=None), 'g3.reviewer is required')
        self.assertRefused(ruled(self.surdas, reviewer='  '), 'g3.reviewer is required')

    def test_missing_or_malformed_date(self):
        self.assertRefused(ruled(self.surdas, date=None), 'g3.date must be YYYY-MM-DD')
        self.assertRefused(ruled(self.surdas, date='27/10/2026'), 'g3.date must be YYYY-MM-DD')
        self.assertRefused(ruled(self.surdas, date='2026-02-30'), 'is not a real date')

    def test_a_future_date(self):
        self.assertRefused(ruled(self.surdas, date='2026-10-28'), 'is in the future')

    def test_missing_or_invalid_decision(self):
        self.assertRefused(ruled(self.surdas, decision=None), 'g3.decision')
        self.assertRefused(ruled(self.surdas, decision='yes'), 'g3.decision')
        self.assertRefused(ruled(self.surdas, decision='reject'), 'g3.decision')   # reject + approved

    def test_rejected_needs_a_reject_decision(self):
        self.assertRefused(ruled(self.surdas, decision='approve', status='rejected'), 'g3.decision')

    def test_scope_must_name_the_item(self):
        self.assertRefused(ruled(self.surdas, scope=None), 'g3.scope')
        self.assertRefused(ruled(self.surdas, scope='A-08'), 'g3.scope')

    def test_evidence_must_be_a_file_in_the_pack(self):
        self.assertRefused(ruled(self.surdas, evidence=None), 'g3.evidence')
        self.assertRefused(ruled(self.surdas, evidence='validation/attribution-g3-review/nope.md'),
                           'g3.evidence')
        self.assertRefused(ruled(self.surdas, evidence='README.md'), 'g3.evidence')
        self.assertRefused(ruled(self.surdas, evidence='validation/attribution-g3-review/../x'),
                           'g3.evidence')

    def test_a_ruling_does_not_carry_over_to_an_edited_entry(self):
        e = ruled(self.surdas)
        e['to'] = 'Bhagat Kabir Ji'                 # edited after the ruling
        self.assertRefused(e, 'entry_sha256')
        e = ruled(self.sain)
        e['end_id'] += 1
        self.assertRefused(e, 'entry_sha256', kind='structure')

    def test_the_fixture_reviewer_is_never_valid_outside_tests(self):
        msgs = G.problems([ruled(self.surdas)], 'attribution', root=self.tmp.name, today=TODAY)
        self.assertTrue(any('test-fixture reviewer' in m for m in msgs), msgs)


class Statuses(Fixture):
    def test_unknown_status_is_refused(self):
        for st in ('Approved', 'approve', 'pending', '', None, 'keep'):
            e = copy.deepcopy(self.sain)
            e['status'] = st
            with self.subTest(status=st):
                self.assertTrue(any('unknown status' in m for m in self.bad([e], 'structure')))

    def test_held_or_proposed_with_a_filled_ruling_is_refused(self):
        for st in ('held', 'proposed'):
            e = ruled(self.surdas, status=st)
            with self.subTest(status=st):
                self.assertTrue(any('ruling fields' in m for m in self.bad([e])))

    def test_stripping_the_g3_block_does_not_make_an_owner_approval(self):
        e = copy.deepcopy(self.surdas)
        e['status'] = 'approved'
        del e['g3']
        self.assertTrue(any('not an owner-approved entry' in m for m in self.bad([e])))
        e['status'] = 'held'
        self.assertTrue(any('only for G3-governed' in m for m in self.bad([e])))
        s = copy.deepcopy(self.sain)
        del s['g3']
        self.assertTrue(any('needs a g3 block' in m for m in self.bad([s], 'structure')))

    def test_owner_approved_entries_still_apply(self):
        japji = next(e for e in real('attribution') if e['entry'] == 'japji')
        self.assertEqual(self.bad([japji]), [])
        rec = [{'id': 1, 'ang': 1, 'comp_id': 2, 'is_header': 0, 'text': 'x', 'markers': [],
                'author': None}]
        A.apply(rec, [japji | {'start_id': 1, 'end_id': 1}])
        self.assertEqual(rec[0]['author'], 'Guru Nanak Dev Ji (M1)')

    def test_proposed_and_rejected_entries_change_nothing(self):
        rec = [{'id': 53935, 'ang': 1253, 'comp_id': 1, 'is_header': 0, 'text': 'x', 'markers': [],
                'author': 'Bhagat Namdev Ji'}]
        for e in (dict(copy.deepcopy(self.surdas), status='proposed'),
                  ruled(self.surdas, decision='reject', status='rejected')):
            self.assertEqual(G.check([e], 'attribution', root=self.tmp.name, today=TODAY,
                                     allow_fixture=True), [])
        A.apply(rec, [dict(copy.deepcopy(self.surdas), status='proposed')])
        self.assertEqual(rec[0]['author'], 'Bhagat Namdev Ji')

    def test_duplicate_entry_names_are_refused(self):
        self.assertTrue(any('duplicate' in m for m in self.bad([self.surdas, self.surdas])))

    def test_an_entry_for_lines_not_in_the_corpus_fails(self):
        with self.assertRaises(G.GateError):
            A.apply([{'id': 1, 'ang': 1, 'comp_id': 1, 'is_header': 0, 'text': 'x', 'markers': [],
                      'author': None}], [self.surdas])

    def test_a_missing_ledger_is_an_error_not_an_empty_one(self):
        with self.assertRaises(FileNotFoundError):
            S.load_ledger(os.path.join(self.tmp.name, 'absent.json'))


class CommittedLedgers(unittest.TestCase):
    """The real ledgers as committed: valid, with every G3 item still awaiting its ruling."""
    def test_they_validate(self):
        for kind in G.LEDGERS:
            with self.subTest(kind=kind):
                self.assertEqual(G.problems(real(kind), kind), [])

    def test_no_g3_ruling_is_recorded_and_none_is_approved(self):
        for kind in G.LEDGERS:
            for e in real(kind):
                if not e.get('g3'):
                    continue
                with self.subTest(entry=e['entry']):
                    self.assertIn(e['status'], ('held', 'proposed'))
                    self.assertTrue(all(e['g3'].get(k) in (None, '') for k in G.RULING))

    def test_the_held_and_pending_set_is_exactly_the_g3_list(self):
        got = sorted((e['g3']['item'], e['entry'], e['status'])
                     for k in G.LEDGERS for e in G.outstanding(real(k)))
        self.assertEqual(got, [
            ('A-07', 'surdas-line', 'held'),
            ('A-08', 'section-salok-farid', 'held'),
            ('A-08', 'section-salok-kabir', 'held'),
            ('A-10', 'ang695-dhanna-opens', 'held'),
            ('A-10', 'ang695-pipa-opens', 'held'),
            ('A-10', 'ang695-sain-opens', 'held'),
            ('A-11 / Ang 323', 'bhagat-run-heading-ang323', 'proposed'),
            ('A-11 / Ang 524', 'bhagat-run-heading-ang524', 'held'),
        ])

    def test_the_committed_corpus_is_what_the_ledger_statuses_say(self):
        # binds status to the built artifact: an applied entry's change is in the corpus, an
        # unapplied G3 entry's is not (a corpus built from other statuses fails here, not only in a
        # full rebuild)
        by_id = {}
        with open(os.path.join(ROOT, 'corpus', 'sggs.jsonl'), encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                by_id[r['id']] = r
        for kind, field in (('attribution', 'author'), ('structure', None)):
            for e in real(kind):
                if not (e.get('g3') or e['status'] in G.APPLIED):
                    continue
                f_ = field or ('section' if e['kind'] == 'section' else 'comp_id')
                rows = [by_id[i] for i in range(e['start_id'], e['end_id'] + 1)]
                want = e['to'] if e['status'] in G.APPLIED else e['from']
                with self.subTest(entry=e['entry'], status=e['status']):
                    self.assertEqual({r[f_] for r in rows}, {want})

    def test_no_committed_ledger_names_the_fixture_reviewer(self):
        for path in G.LEDGERS.values():
            with open(path, encoding='utf-8') as f:
                self.assertNotIn(G.FIXTURE_REVIEWER, f.read())

    def test_the_release_check_fails_today_and_the_plain_gate_passes(self):
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(G.main([]), 0)
            self.assertEqual(G.main(['--release-check']), 1)
        self.assertIn('G3 release check: FAIL — 8 G3 entries', out.getvalue())


if __name__ == '__main__':
    unittest.main()
