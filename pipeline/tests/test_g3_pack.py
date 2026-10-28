# -*- coding: utf-8 -*-
"""The G3 review pack is generated from the DB and the ledgers. It must describe the build that is
committed: the DB it was generated from is the DB in MANIFEST.json, and every G3 ledger entry is the
one it was generated for. A stale pack would show a scholar evidence for a different change."""
import glob, json, os, re, sys, unittest

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

    def test_every_cited_line_is_quoted_verbatim(self):
        # pack convention: `<Gurmukhi>` *(line N)* quotes corpus line N exactly, character for
        # character; a hand-written page may not paraphrase or retype scripture
        by_id = {}
        with open(os.path.join(ROOT, 'corpus', 'sggs.jsonl'), encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                by_id[r['id']] = r['gurmukhi']
        n = 0
        for p in sorted(glob.glob(os.path.join(PACK, '*.md'))):
            with open(p, encoding='utf-8') as f:
                text = f.read()
            for quote, lid in re.findall(r'`([^`\n]*[਀-੿][^`\n]*)` \*\(line (\d+)\)\*', text):
                n += 1
                with self.subTest(file=os.path.basename(p), line=lid):
                    self.assertEqual(quote, by_id[int(lid)])
        self.assertGreater(n, 10, 'expected the pack to cite lines in the `…` *(line N)* form')

    def test_the_readme_is_the_rendered_template(self):
        # README.md is generated: an edit to it alone (or to the template without regenerating) is stale
        import shutil, sqlite3, tempfile
        sys.path.insert(0, os.path.join(ROOT, 'scripts', 'data'))
        import g3_attribution_pack as P
        tmp = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(PACK, 'README.template.md'), tmp)
            post = sqlite3.connect(f"file:{os.path.join(ROOT, 'db', 'sggs.sqlite')}?mode=ro", uri=True)
            try:
                P.readme(post, tmp)
            finally:
                post.close()
            with open(os.path.join(tmp, 'README.md'), encoding='utf-8') as a, \
                    open(os.path.join(PACK, 'README.md'), encoding='utf-8') as b:
                self.assertEqual(a.read(), b.read(), 'README.md is stale: run scripts/data/g3_attribution_pack.py')
        finally:
            shutil.rmtree(tmp)

    def test_generated_for_these_g3_entries(self):
        now = {e['entry']: G.entry_sha256(e) for k in G.LEDGERS for e in G.read(G.LEDGERS[k]) if e.get('g3')}
        self.assertEqual(self.stamp['g3_entries'], dict(sorted(now.items())),
                         'a G3 entry changed: regenerate the pack before asking for a ruling on it')


if __name__ == '__main__':
    unittest.main()
