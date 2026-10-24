# -*- coding: utf-8 -*-
"""crosscheck_authors.py: the alignment keys and the flag coverage the gate depends on (the
ShabadOS database itself is not in CI; `make crosscheck-authors` and rebuild_all run the gate)."""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import crosscheck_authors as cc


class Keys(unittest.TestCase):
    def test_gurbani_akhar_first_letters_match_ours(self):
        # Ang 695 "ਧਨਾਸਰੀ ਬਾਣੀ ਭਗਤਾਂ ਕੀ ਤ੍ਰਿਲੋਚਨ": ShabadOS "DbBkq", ours "ਧ ਬ ਭ ਕ ਤ"
        self.assertEqual(cc.key_sos('DbBkq'), cc.key_ours({'fl_g': 'ਧ ਬ ਭ ਕ ਤ'}))
        self.assertEqual(cc.key_sos('<>sp'), cc.key_ours({'fl_g': 'ੴ ਸ ਪ'}))

    def test_vowel_carriers_and_nukta_fold(self):
        self.assertEqual(cc.key_ours({'fl_g': 'ਇ ਆ ਊ'}), cc.key_sos('eAa'))
        self.assertEqual(cc.key_ours({'fl_g': 'ਸ਼'}), cc.key_sos('s'))


class Flags(unittest.TestCase):
    FLAGS = os.path.join(ROOT, 'pipeline', 'shabados_crosscheck_flags.json')

    def test_flags_file_is_well_formed(self):
        with open(self.FLAGS, encoding='utf-8') as f:
            flags = json.load(f)['flags']
        keys = [x['key'] for x in flags]
        self.assertEqual(len(keys), len(set(keys)))
        for x in flags:
            self.assertTrue(('ids' in x) != ('ang' in x), f"{x['key']}: exactly one of ids / ang")
            r = x.get('ids') or x.get('ang')
            self.assertLessEqual(r[0], r[1])
            self.assertTrue(x.get('note'), f"{x['key']}: a flag must say why")

    def test_coverage_by_id_and_by_ang(self):
        flags = [{'key': 'a', 'ids': [10, 12]}, {'key': 'b', 'ang': [1429, 1430]}]
        self.assertEqual(cc.covered((11, 5, 'x', 'y', 0, ''), flags), 'a')
        self.assertEqual(cc.covered((99, 1430, 'x', 'y', 0, ''), flags), 'b')
        self.assertIsNone(cc.covered((13, 6, 'x', 'y', 0, ''), flags))


if __name__ == '__main__':
    unittest.main()
