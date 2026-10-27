# -*- coding: utf-8 -*-
"""The G3 review pack is generated from the DB and the ledgers. It must describe the build that is
committed: the DB it was generated from is the DB in MANIFEST.json, and every G3 ledger entry is the
one it was generated for. A stale pack would show a scholar evidence for a different change."""
import json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import g3_gate as G  # noqa: E402

PACK = os.path.join(ROOT, 'validation', 'attribution-g3-review')


class PackIsCurrent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PACK, 'pack-inputs.json'), encoding='utf-8') as f:
            cls.stamp = json.load(f)
        with open(os.path.join(ROOT, 'MANIFEST.json'), encoding='utf-8') as f:
            cls.manifest = json.load(f)

    def test_generated_from_the_committed_db(self):
        self.assertEqual(self.stamp['post_db_sha256'], self.manifest['db_sha256'],
                         'the DB was rebuilt: regenerate the pack (scripts/data/g3_attribution_pack.py)')

    def test_generated_for_these_g3_entries(self):
        now = {e['entry']: G.entry_sha256(e) for k in G.LEDGERS for e in G.read(G.LEDGERS[k]) if e.get('g3')}
        self.assertEqual(self.stamp['g3_entries'], dict(sorted(now.items())),
                         'a G3 entry changed: regenerate the pack before asking for a ruling on it')


if __name__ == '__main__':
    unittest.main()
