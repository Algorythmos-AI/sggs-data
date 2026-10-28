# -*- coding: utf-8 -*-
"""The G3 approval gate (pipeline/g3_gate.py): incomplete, unprovenanced or invalid rulings fail the
build; held entries never pass the release check; a G3 item cannot be stripped, renamed or quietly
kept; and a complete ruling -- in a temporary fixture only, never in the committed ledgers, with the
fixture reviewer -- is accepted end to end. The committed ledgers and corpus are checked as they are."""
import copy, datetime, io, json, os, shutil, subprocess, sys, tempfile, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import g3_gate as G  # noqa: E402
import attribution as A  # noqa: E402
import structure as S  # noqa: E402

TODAY = datetime.date(2026, 10, 28)
RULING_FILE = G.RULINGS + 'fixture-reply.txt'


def real(kind):
    return G.read(G.LEDGERS[kind])


def named(kind, name):
    return copy.deepcopy(next(e for e in real(kind) if e['entry'] == name))


def keypair(d, name):
    """A throwaway ed25519 key in d; returns (private key path, allowed_signers line for the fixture)."""
    key = os.path.join(d, name)
    subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-C', name, '-f', key], check=True)
    with open(key + '.pub', encoding='utf-8') as f:
        pub = f.read().strip()
    return key, f'{G.FIXTURE_PRINCIPAL} namespaces="{G.SIG_NAMESPACE}" {pub}\n'


def sign(key, path, namespace=G.SIG_NAMESPACE):
    if os.path.exists(path + '.sig'):
        os.remove(path + '.sig')
    subprocess.run(['ssh-keygen', '-q', '-Y', 'sign', '-f', key, '-n', namespace, path], check=True,
                   capture_output=True)


class Fixture(unittest.TestCase):
    """A temporary repo root holding a ruling file, so `evidence` resolves and hashes."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.tmp.name, G.RULINGS))
        with open(os.path.join(self.tmp.name, RULING_FILE), 'w', encoding='utf-8') as f:
            f.write('fixture: not a ruling\n')
        # the fixture reviewer's key, registered in a temporary allowed_signers; the ruling is signed
        self.keydir = os.path.join(self.tmp.name, 'keys')
        os.makedirs(self.keydir)
        self.key, line = keypair(self.keydir, 'fixture')
        self.signers = os.path.join(self.keydir, 'allowed_signers')
        with open(self.signers, 'w', encoding='utf-8') as f:
            f.write(line)
        sign(self.key, os.path.join(self.tmp.name, RULING_FILE))
        self.surdas = named('attribution', 'surdas-line')
        self.sain = named('structure', 'ang695-sain-opens')
        self.gate = dict(root=self.tmp.name, today=TODAY, allow_fixture=True, signers=self.signers)

    def tearDown(self):
        self.tmp.cleanup()

    def ruled(self, e, decision='approve', status='approved', **over):
        """A complete ruling on entry e, for a fixture. The reviewer is the fixture name."""
        e = copy.deepcopy(e)
        e['status'] = status
        e['g3'] = dict(e['g3'], decision=decision, reviewer=G.FIXTURE_REVIEWER, date='2026-10-27',
                       scope=e['g3']['item'], evidence=RULING_FILE,
                       evidence_sha256=G.file_sha256(os.path.join(self.tmp.name, RULING_FILE)),
                       entry_sha256=G.entry_sha256(e))
        e['g3'].update(over)
        return e

    def bad(self, entries, kind='attribution', **kw):
        return G.problems(entries, kind, **dict(self.gate, **kw))

    def assertRefused(self, entry, why, kind='attribution', **kw):
        msgs = self.bad([entry], kind, **kw)
        self.assertTrue(any(why in m for m in msgs), f'{why!r} not in {msgs}')


class CompleteRulings(Fixture):
    def test_a_complete_approval_is_accepted(self):
        for kind, e in (('attribution', self.surdas), ('structure', self.sain)):
            with self.subTest(kind=kind):
                ok = self.ruled(e)
                self.assertEqual(self.bad([ok], kind), [])
                self.assertEqual([x['entry'] for x in G.check([ok], kind, **self.gate)], [e['entry']])
                self.assertEqual(G.outstanding([ok]), [])

    def test_both_passes_apply_a_complete_approval(self):
        rec = [{'id': 53935, 'ang': 1253, 'comp_id': 1, 'is_header': 0, 'text': 'x', 'markers': [],
                'author': 'Bhagat Namdev Ji'}]
        A.apply(rec, [self.ruled(self.surdas)], gate=self.gate)
        self.assertEqual(rec[0]['author'], 'Bhagat Surdas Ji')
        e = self.sain
        r = [{'id': e['start_id'] - 1, 'ang': 695, 'comp_id': 2749, 'line_no': 1, 'is_header': 1,
              'section': None, 'text': 'h', 'author': 'A'}] + \
            [{'id': i, 'ang': 695, 'comp_id': 2749, 'line_no': i - e['start_id'] + 2, 'is_header': 0,
              'section': None, 'text': 'x', 'author': 'A'} for i in range(e['start_id'], e['end_id'] + 1)]
        S.apply(r, [self.ruled(e)], issued=5380, gate=self.gate)
        self.assertEqual({x['comp_id'] for x in r[1:]}, {5381})
        self.assertEqual(r[1]['is_header'], 1)

    def test_change_is_an_approval_and_reject_a_rejection(self):
        self.assertEqual(self.bad([self.ruled(self.surdas, decision='change')]), [])
        rej = self.ruled(self.surdas, decision='reject', status='rejected')
        self.assertEqual(self.bad([rej]), [])
        self.assertEqual(G.check([rej], 'attribution', **self.gate), [])

    def test_the_release_check_passes_once_every_item_is_ruled(self):
        # every G3 entry ruled (Ang 323 rejected, so the committed corpus still matches); main() green
        root = self.tmp.name
        paths = {}
        for kind in G.LEDGERS:
            out = []
            for e in real(kind):
                if e.get('g3'):
                    e = self.ruled(e, decision='reject', status='rejected') if e['status'] == 'proposed' \
                        else self.ruled(e)
                out.append(e)
            paths[kind] = os.path.join(root, f'{kind}.json')
            with open(paths[kind], 'w', encoding='utf-8') as f:
                json.dump({'entries': out}, f, ensure_ascii=False)
        orig = G.problems
        G.problems = lambda entries, kind, **kw: orig(entries, kind, **dict(kw, today=TODAY, allow_fixture=True,
                                                                            signers=self.signers))
        try:
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(G.main(['--release-check'], ledger_paths=paths, root=root), 0)
        finally:
            G.problems = orig
        self.assertIn('every G3 ruling is recorded', out.getvalue())


class SignedRulings(Fixture):
    """A ruling counts only with the reviewer's own signature, verified against a key registered in
    the gate's own tree. Committing a reply file and filling a ledger cannot forge one."""
    def reply(self, text='forged reply\n', name='forged.txt'):
        p = os.path.join(self.tmp.name, G.RULINGS, name)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
        return G.RULINGS + name, p

    def with_evidence(self, rel):
        return self.ruled(self.surdas, evidence=rel,
                          evidence_sha256=G.file_sha256(os.path.join(self.tmp.name, rel)))

    def test_an_unsigned_ruling_is_refused(self):
        rel, _ = self.reply()
        self.assertRefused(self.with_evidence(rel), 'not signed')

    def test_a_signature_by_an_unregistered_key_is_refused(self):
        rel, p = self.reply()
        other, _ = keypair(self.keydir, 'impostor')
        sign(other, p)
        self.assertRefused(self.with_evidence(rel), 'does not verify')

    def test_a_signature_over_another_file_is_refused(self):
        rel, p = self.reply()
        shutil.copy(os.path.join(self.tmp.name, RULING_FILE + '.sig'), p + '.sig')
        self.assertRefused(self.with_evidence(rel), 'does not verify')

    def test_a_signature_in_another_namespace_is_refused(self):
        rel, p = self.reply()
        sign(self.key, p, namespace='git')
        self.assertRefused(self.with_evidence(rel), 'does not verify')

    def test_a_reply_edited_after_signing_is_refused(self):
        rel, p = self.reply()
        sign(self.key, p)
        with open(p, 'a', encoding='utf-8') as f:
            f.write('approve everything\n')
        self.assertRefused(self.with_evidence(rel), 'does not verify')

    def test_no_registered_key_means_no_ruling_verifies(self):
        self.assertRefused(self.ruled(self.surdas), 'no reviewer key is registered',
                           signers=os.path.join(self.tmp.name, 'absent'))

    def test_a_symlinked_signature_is_refused(self):
        rel, p = self.reply()
        os.symlink(os.path.join(self.tmp.name, RULING_FILE + '.sig'), p + '.sig')
        self.assertRefused(self.with_evidence(rel), 'not signed')

    def test_the_committed_gate_has_no_key_for_the_fixture(self):
        # the real SIGNERS (if a key is ever registered) never accepts the fixture principal
        if os.path.isfile(G.SIGNERS):
            with open(G.SIGNERS, encoding='utf-8') as f:
                self.assertNotIn(G.FIXTURE_PRINCIPAL, f.read())
        self.assertRefused(self.ruled(self.surdas), 'no reviewer key is registered' if not
                           os.path.isfile(G.SIGNERS) else 'does not verify', signers=G.SIGNERS)


class BaseBranchGate(Fixture):
    """--tree: the gate judges a pull request's data with its own code and trust anchors. A tree that
    rules every item, signs with its own key and registers that key in its own allowed_signers --
    everything a pull request can change -- must still fail."""
    def forged_tree(self):
        tree = os.path.join(self.tmp.name, 'pr')
        for sub in ('pipeline', 'corpus', G.RULINGS):
            os.makedirs(os.path.join(tree, sub), exist_ok=True)
        shutil.copy(G.CORPUS, os.path.join(tree, 'corpus', 'sggs.jsonl'))
        for name in (RULING_FILE, RULING_FILE + '.sig'):
            shutil.copy(os.path.join(self.tmp.name, name), os.path.join(tree, name))
        shutil.copy(self.signers, os.path.join(tree, G.PACK, 'allowed_signers'))
        for kind, path in G.LEDGERS.items():
            out = []
            for e in real(kind):
                if e.get('g3'):
                    e = self.ruled(e, decision='reject', status='rejected') if e['status'] == 'proposed' \
                        else self.ruled(e)
                out.append(e)
            with open(os.path.join(tree, os.path.relpath(path, G.ROOT)), 'w', encoding='utf-8') as f:
                json.dump({'entries': out}, f, ensure_ascii=False)
        return tree

    def run_gate(self, argv, **kw):
        orig = G.problems
        G.problems = lambda entries, kind, **k: orig(entries, kind, **dict(k, today=TODAY, allow_fixture=True, **kw))
        try:
            with redirect_stdout(io.StringIO()) as out:
                code = G.main(argv)
        finally:
            G.problems = orig
        return code, out.getvalue()

    def test_a_tree_that_registers_its_own_key_is_refused(self):
        code, out = self.run_gate(['--release-check', '--tree', self.forged_tree()])
        self.assertEqual(code, 1, out)
        self.assertTrue('no reviewer key is registered' in out or 'does not verify' in out, out)

    def test_the_same_tree_passes_only_with_a_trusted_key(self):
        # control: with the key trusted by the gate itself, the forged tree's rulings verify
        code, out = self.run_gate(['--release-check', '--tree', self.forged_tree()], signers=self.signers)
        self.assertEqual(code, 0, out)

    def test_tree_needs_a_directory(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(G.main(['--tree']), 2)


class IncompleteRulings(Fixture):
    def test_the_state_pr17_shipped_approved_with_a_blank_ruling_is_refused(self):
        e = dict(copy.deepcopy(self.surdas), status='approved')
        self.assertRefused(e, 'g3.decision')
        self.assertRefused(e, 'not a G3 reviewer of record')
        with self.assertRaises(G.GateError):
            A.apply([{'id': 53935, 'ang': 1253, 'comp_id': 1, 'is_header': 0, 'text': 'x',
                      'markers': [], 'author': 'Bhagat Namdev Ji'}], [e])

    def test_the_structure_pass_refuses_an_incomplete_approval(self):
        e = dict(copy.deepcopy(self.sain), status='approved')
        r = [{'id': i, 'ang': 695, 'comp_id': 2749, 'line_no': i - e['start_id'] + 2, 'is_header': 0,
              'section': None, 'text': 'x', 'author': 'A'} for i in range(e['start_id'], e['end_id'] + 1)]
        with self.assertRaises(G.GateError):
            S.apply(r, [e], issued=5380)
        self.assertTrue(all(x['comp_id'] == 2749 for x in r))     # nothing applied

    def test_both_ledger_loaders_validate(self):
        for mod, kind, e in ((A, 'attribution', self.surdas), (S, 'structure', self.sain)):
            entries = [dict(x, status='approved') if x['entry'] == e['entry'] else x for x in real(kind)]
            p = os.path.join(self.tmp.name, f'{kind}.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({'entries': entries}, f, ensure_ascii=False)
            with self.subTest(kind=kind), self.assertRaises(G.GateError):
                mod.load_ledger(p)

    def test_reviewer_must_be_of_record(self):
        for rev in (None, '', '  ', 'x', 'An Engineer', G.FIXTURE_REVIEWER + '\u200b'):
            with self.subTest(reviewer=rev):
                self.assertRefused(self.ruled(self.surdas, reviewer=rev), 'not a G3 reviewer of record')

    def test_the_fixture_reviewer_is_never_valid_outside_tests(self):
        self.assertRefused(self.ruled(self.surdas), 'not a G3 reviewer of record', allow_fixture=False)

    def test_missing_or_malformed_date(self):
        self.assertRefused(self.ruled(self.surdas, date=None), 'g3.date must be YYYY-MM-DD')
        self.assertRefused(self.ruled(self.surdas, date='27/10/2026'), 'g3.date must be YYYY-MM-DD')
        self.assertRefused(self.ruled(self.surdas, date='2026-10-27\n'), 'g3.date must be YYYY-MM-DD')
        self.assertRefused(self.ruled(self.surdas, date='2026-02-30'), 'is not a real date')

    def test_a_future_or_too_early_date(self):
        self.assertRefused(self.ruled(self.surdas, date='2026-10-29'), 'is in the future')
        self.assertRefused(self.ruled(self.surdas, date='1900-01-01'), 'predates the held pull request')
        self.assertRefused(self.ruled(self.surdas, date='2026-10-25'), 'predates the held pull request')

    def test_missing_or_invalid_decision(self):
        self.assertRefused(self.ruled(self.surdas, decision=None), 'g3.decision')
        self.assertRefused(self.ruled(self.surdas, decision='yes'), 'g3.decision')
        self.assertRefused(self.ruled(self.surdas, decision='reject'), 'g3.decision')   # reject + approved

    def test_rejected_needs_a_reject_decision(self):
        self.assertRefused(self.ruled(self.surdas, decision='approve', status='rejected'), 'g3.decision')

    def test_scope_must_name_the_item(self):
        self.assertRefused(self.ruled(self.surdas, scope=None), 'g3.scope')
        self.assertRefused(self.ruled(self.surdas, scope='A-08'), 'g3.scope')

    def test_evidence_must_be_the_reviewers_reply_in_rulings(self):
        for ev in (None, G.PACK + 'SIGN-OFF.md', G.PACK + 'README.md', 'README.md', G.RULINGS + 'nope.txt',
                   G.RULINGS + '../SIGN-OFF.md', '/etc/hosts'):
            with self.subTest(evidence=ev):
                self.assertRefused(self.ruled(self.surdas, evidence=ev), 'g3.evidence')

    def test_a_symlinked_ruling_is_refused(self):
        for target in ('/etc/hosts', os.path.join(self.tmp.name, RULING_FILE)):     # outside, and inside
            link = os.path.join(self.tmp.name, G.RULINGS, 'link.txt')
            if os.path.lexists(link):
                os.remove(link)
            os.symlink(target, link)
            with self.subTest(target=target):
                self.assertRefused(self.ruled(self.surdas, evidence=G.RULINGS + 'link.txt'), 'not a symlink')

    def test_the_ruling_file_must_be_the_one_hashed(self):
        self.assertRefused(self.ruled(self.surdas, evidence_sha256='0' * 64), 'evidence_sha256')
        e = self.ruled(self.surdas)
        with open(os.path.join(self.tmp.name, RULING_FILE), 'a', encoding='utf-8') as f:
            f.write('edited after the ruling\n')
        self.assertRefused(e, 'evidence_sha256')

    def test_a_ruling_does_not_carry_over_to_an_edited_entry(self):
        e = self.ruled(self.surdas)
        e['to'] = 'Bhagat Kabir Ji'                 # edited after the ruling
        self.assertRefused(e, 'entry_sha256')
        e = self.ruled(self.sain)
        e['end_id'] += 1
        self.assertRefused(e, 'entry_sha256', kind='structure')

    def test_prose_edits_do_not_void_a_ruling(self):
        e = self.ruled(self.surdas)
        e['reason'] += ' (wording corrected)'
        self.assertEqual(self.bad([e]), [])


class Statuses(Fixture):
    def test_unknown_status_is_refused(self):
        for st in ('Approved', 'approve', 'pending', '', None, 'keep'):
            e = dict(copy.deepcopy(self.sain), status=st)
            with self.subTest(status=st):
                self.assertTrue(any('unknown status' in m for m in self.bad([e], 'structure')))

    def test_a_g3_item_cannot_be_kept(self):
        self.assertRefused(dict(copy.deepcopy(self.surdas), status='keep'), 'cannot be `keep`')

    def test_held_or_proposed_with_a_filled_ruling_is_refused(self):
        for st in ('held', 'proposed'):
            with self.subTest(status=st):
                self.assertRefused(self.ruled(self.surdas, status=st), 'ruling fields')

    def test_stripping_the_g3_block_is_refused(self):
        for st in ('approved', 'proposed', 'held', 'keep'):
            e = dict(copy.deepcopy(self.surdas), status=st)
            del e['g3']
            with self.subTest(status=st):
                self.assertRefused(e, 'needs its g3 block')
        s = copy.deepcopy(self.sain)
        del s['g3']
        self.assertRefused(s, 'needs a g3 block', kind='structure')

    def test_a_new_entry_cannot_be_approved_without_a_ruling(self):
        e = {'entry': 'new-fix', 'start_id': 1, 'end_id': 2, 'from': 'A', 'to': 'B', 'status': 'approved',
             'reason': 'x'}
        self.assertRefused(e, 'not an owner-approved entry')

    def test_owner_approved_entries_still_apply(self):
        japji = named('attribution', 'japji')
        self.assertEqual(self.bad([japji]), [])
        self.assertEqual(G.ledger_problems(real('attribution'), 'attribution'), [])
        rec = [{'id': 1, 'ang': 1, 'comp_id': 2, 'is_header': 0, 'text': 'x', 'markers': [], 'author': None}]
        A.apply(rec, [japji | {'start_id': 1, 'end_id': 1}])
        self.assertEqual(rec[0]['author'], 'Guru Nanak Dev Ji (M1)')

    def test_proposed_and_rejected_entries_change_nothing(self):
        rec = [{'id': 53935, 'ang': 1253, 'comp_id': 1, 'is_header': 0, 'text': 'x', 'markers': [],
                'author': 'Bhagat Namdev Ji'}]
        for e in (dict(copy.deepcopy(self.surdas), status='proposed'),
                  self.ruled(self.surdas, decision='reject', status='rejected')):
            self.assertEqual(G.check([e], 'attribution', **self.gate), [])
            A.apply(rec, [e], gate=self.gate)
            self.assertEqual(rec[0]['author'], 'Bhagat Namdev Ji')

    def test_duplicate_entry_names_are_refused(self):
        self.assertTrue(any('duplicate' in m for m in self.bad([self.surdas, self.surdas])))

    def test_required_fields_must_be_present(self):
        for field in ('to', 'start_id', 'entry'):
            e = copy.deepcopy(self.surdas)
            del e[field]
            with self.subTest(field=field):
                self.assertTrue(any('missing required field' in m for m in self.bad([e])))
        s = copy.deepcopy(self.sain)
        del s['kind']
        self.assertRefused(s, 'missing required field', kind='structure')
        self.assertEqual(self.bad([named('attribution', 'japji')]), [])        # `from` null is allowed

    def test_ids_must_be_integers(self):
        for bad in (53935.0, '53935', True):
            with self.subTest(start_id=bad):
                self.assertRefused(dict(copy.deepcopy(self.surdas), start_id=bad), 'integers')

    def test_an_entry_for_lines_not_in_the_corpus_fails(self):
        with self.assertRaises(G.GateError):
            A.apply([{'id': 1, 'ang': 1, 'comp_id': 1, 'is_header': 0, 'text': 'x', 'markers': [],
                      'author': None}], [self.surdas])

    def test_a_missing_ledger_is_an_error_not_an_empty_one(self):
        with self.assertRaises(FileNotFoundError):
            S.load_ledger(os.path.join(self.tmp.name, 'absent.json'))


class Registry(unittest.TestCase):
    """Whole-ledger rules: a G3 item cannot be renamed, dropped or invented, and an owner approval
    cannot be re-pointed."""
    def test_a_g3_item_cannot_be_dropped_or_renamed(self):
        att = real('attribution')
        dropped = [e for e in att if e['entry'] != 'surdas-line']
        self.assertTrue(any('missing from the ledger' in m for m in G.ledger_problems(dropped, 'attribution')))
        renamed = [dict(e, entry='surdas-line-2') if e['entry'] == 'surdas-line' else e for e in att]
        msgs = G.ledger_problems(renamed, 'attribution')
        self.assertTrue(any('missing' in m for m in msgs) and any('not a registered' in m for m in msgs))

    def test_the_item_label_must_match(self):
        att = [dict(e, g3=dict(e['g3'], item='A-08')) if e['entry'] == 'surdas-line' else e
               for e in real('attribution')]
        self.assertTrue(any("must carry g3.item 'A-07'" in m for m in G.ledger_problems(att, 'attribution')))

    def test_an_owner_approval_cannot_be_repointed(self):
        att = [dict(e, start_id=53935, end_id=53935, to='Bhagat Surdas Ji') if e['entry'] == 'sadu' else e
               for e in real('attribution')]
        self.assertTrue(any('owner-approved entry was edited' in m for m in G.ledger_problems(att, 'attribution')))


class CommittedLedgers(unittest.TestCase):
    """The real ledgers and corpus as committed: valid, with every G3 item awaiting its ruling."""
    def test_they_validate(self):
        for kind in G.LEDGERS:
            with self.subTest(kind=kind):
                self.assertEqual(G.problems(real(kind), kind), [])
                self.assertEqual(G.ledger_problems(real(kind), kind), [])

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
        self.assertEqual(G.artifact_problems({k: real(k) for k in G.LEDGERS}, G.CORPUS), [])

    def test_a_status_flip_without_a_rebuild_is_caught(self):
        att = [dict(e, status='proposed') if e['entry'] == 'surdas-line' else e for e in real('attribution')]
        msgs = G.artifact_problems({'attribution': att, 'structure': real('structure')}, G.CORPUS)
        self.assertTrue(any('surdas-line' in m for m in msgs), msgs)

    def test_no_committed_ledger_names_a_reviewer_or_the_fixture(self):
        for path in G.LEDGERS.values():
            with open(path, encoding='utf-8') as f:
                text = f.read()
            self.assertNotIn(G.FIXTURE_REVIEWER, text)
            for rev in G.REVIEWERS:
                self.assertNotIn(rev, text)

    def test_the_release_check_fails_today_and_the_plain_gate_passes(self):
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(G.main([]), 0)
            self.assertEqual(G.main(['--release-check']), 1)
        text = out.getvalue()
        self.assertIn('G3 release check: FAIL — 8 G3 entries without a recorded scholarly ruling '
                      '(7 held: applied only in this draft build; 1 proposed: not applied)', text)
        # every one of the eight, by name and status -- the CI log that reported "8" against "7 held"
        for kind, name, st in (('attribution', 'surdas-line', 'held'),
                               ('attribution', 'bhagat-run-heading-ang524', 'held'),
                               ('attribution', 'bhagat-run-heading-ang323', 'proposed'),
                               ('structure', 'section-salok-kabir', 'held'),
                               ('structure', 'section-salok-farid', 'held'),
                               ('structure', 'ang695-sain-opens', 'held'),
                               ('structure', 'ang695-pipa-opens', 'held'),
                               ('structure', 'ang695-dhanna-opens', 'held')):
            with self.subTest(entry=name):
                self.assertIn(f'::error::{kind}:{name} is {st}: no G3 ruling is recorded', text)

    def test_the_cli_checks_the_corpus_not_only_the_ledgers(self):
        # a valid ledger (held -> proposed, ruling still blank) that no longer matches the committed
        # corpus: the plain gate must fail on the artifact, not pass on the ledgers alone
        tmp = tempfile.mkdtemp()
        try:
            att = [dict(e, status='proposed') if e['entry'] == 'surdas-line' else e for e in real('attribution')]
            paths = {'attribution': os.path.join(tmp, 'a.json'), 'structure': G.LEDGERS['structure']}
            with open(paths['attribution'], 'w', encoding='utf-8') as f:
                json.dump({'entries': att}, f, ensure_ascii=False)
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(G.main([], ledger_paths=paths), 1)
            self.assertIn('committed corpus has', out.getvalue())
        finally:
            shutil.rmtree(tmp)

    def test_the_stripped_ledger_attack_fails_the_release_check(self):
        # adversarial review attack 1: G3 entries set proposed with g3 removed, structure emptied,
        # the DB left as built -- must fail, not pass
        tmp = tempfile.mkdtemp()
        try:
            att = []
            for e in real('attribution'):
                if e.get('g3'):
                    e = dict(e, status='proposed')
                    del e['g3']
                att.append(e)
            paths = {'attribution': os.path.join(tmp, 'a.json'), 'structure': os.path.join(tmp, 's.json')}
            for k, entries in (('attribution', att), ('structure', [])):
                with open(paths[k], 'w', encoding='utf-8') as f:
                    json.dump({'entries': entries}, f, ensure_ascii=False)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(G.main(['--release-check'], ledger_paths=paths), 1)
        finally:
            shutil.rmtree(tmp)


class WorkflowRules(unittest.TestCase):
    """Repository rules: CI runs the release check in the required job, and a second time from the base
    branch's code against the pull request's data, with nothing from the pull request executed."""
    def wf(self, name):
        with open(os.path.join(ROOT, '.github', 'workflows', name), encoding='utf-8') as f:
            return f.read()

    def test_the_base_branch_judges_the_pull_request(self):
        text = self.wf('g3-gate.yml')
        self.assertIn('pull_request_target:', text)
        self.assertNotIn('\n  pull_request:', text)
        self.assertIn('ref: ${{ github.event.pull_request.base.sha }}', text)
        self.assertIn('python3 -I base/pipeline/g3_gate.py --release-check --tree pr', text)
        self.assertEqual(text.count('persist-credentials: false'), 2)
        self.assertNotIn('secrets.', text)
        self.assertNotIn('write', text.split('permissions:')[1].split('jobs:')[0])
        # nothing under pr/ is run: the only commands are the base gate and a shell test
        cmds = [ln.strip() for ln in text.splitlines() if ln.strip().startswith('python3')]
        self.assertEqual(cmds, ['python3 -I base/pipeline/g3_gate.py --release-check --tree pr'])

    def test_the_required_integrity_job_ends_with_the_release_check(self):
        text = self.wf('data-ci.yml')
        integrity = text.split('\n  integrity:')[1].split('\n  tests:')[0]
        steps = [ln for ln in integrity.splitlines() if ln.strip().startswith('- name:')]
        self.assertIn('G3 gate', steps[-1])
        self.assertIn('run: python3 pipeline/g3_gate.py --release-check', integrity.split(steps[-1])[1])


if __name__ == '__main__':
    unittest.main()
