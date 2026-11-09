"""The line-id gate: an existing id never changes its (ang, gurmukhi); new ids are only appended.

Every case runs on synthetic rows — the committed data is never touched. The committed baseline
itself is checked against the real corpus/DB at the end (skipped without the real DB).
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
import line_id_gate as g  # noqa: E402

ROWS = {1: (1, "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ"), 2: (1, "ਆਦਿ ਸਚੁ ਜੁਗਾਦਿ ਸਚੁ ॥"),
        3: (2, "ਸੋਚੈ ਸੋਚਿ ਨ ਹੋਵਈ ਜੇ ਸੋਚੀ ਲਖ ਵਾਰ ॥"), 4: (2, "ਚੁਪੈ ਚੁਪ ਨ ਹੋਵਈ ਜੇ ਲਾਇ ਰਹਾ ਲਿਵ ਤਾਰ ॥"),
        5: (3, "ਹੁਕਮੀ ਹੋਵਨਿ ਆਕਾਰ ਹੁਕਮੁ ਨ ਕਹਿਆ ਜਾਈ ॥")}
BASE = g.build_baseline(ROWS, "1.4.0")


def corpus(rows):
    return "\n".join(json.dumps({"id": i, "ang": a, "gurmukhi": t}, ensure_ascii=False)
                     for i, (a, t) in sorted(rows.items())) + "\n"


class Baseline(unittest.TestCase):
    def test_one_block_per_ang(self):
        self.assertEqual([b[:3] for b in BASE["blocks"]], [[1, 1, 2], [2, 3, 4], [3, 5, 5]])
        self.assertEqual(BASE["max_id"], 5)

    def test_unchanged_passes(self):
        self.assertEqual(g.check(BASE, dict(ROWS), [], "corpus", "1.4.0"), [])

    def test_dump_round_trips(self):
        self.assertEqual(json.loads(g.dump_baseline(BASE)), BASE)


class ShiftedIds(unittest.TestCase):
    def test_inserted_line_shifts_every_later_id_and_fails(self):
        # a rebuild that splits one line in two renumbers everything after it: 3 -> 4, 4 -> 5, ...
        texts = [t for _, (_, t) in sorted(ROWS.items())]
        angs = [a for _, (a, _) in sorted(ROWS.items())]
        texts.insert(2, "ਸੋਚੈ ਸੋਚਿ")
        angs.insert(2, 2)
        shifted = {i: (a, t) for i, (a, t) in enumerate(zip(angs, texts), 1)}
        fails = g.check(BASE, shifted, [], "corpus", "1.4.0", base_rows=ROWS)
        self.assertTrue(any("changed an existing id" in f and "Angs [2, 3]" in f for f in fails), fails)
        self.assertTrue(any("id 3: was" in f for f in fails), fails)

    def test_off_by_one_renumbering_fails(self):
        shifted = {i + 1: v for i, v in ROWS.items()}       # ids 2..6: id 1 is gone
        fails = g.check(BASE, shifted, [], "db", "1.4.0")
        self.assertTrue(any("changed an existing id" in f for f in fails))
        self.assertTrue(any("not 1..6" in f for f in fails))

    def test_rewritten_gurmukhi_fails(self):
        rows = {**ROWS, 4: (2, ROWS[4][1] + " ")}
        self.assertTrue(any("Angs [2]" in f for f in g.check(BASE, rows, [], "corpus", "1.4.0")))

    def test_moved_ang_fails(self):
        rows = {**ROWS, 5: (2, ROWS[5][1])}
        self.assertTrue(any("Angs [3]" in f for f in g.check(BASE, rows, [], "corpus", "1.4.0")))

    def test_dropped_line_fails(self):
        rows = {i: v for i, v in ROWS.items() if i != 5}
        self.assertTrue(any("changed an existing id" in f for f in g.check(BASE, rows, [], "corpus", "1.4.0")))

    def test_duplicate_id_fails(self):
        rows, dups = g.rows_from_corpus_text(corpus(ROWS) + json.dumps({"id": 2, "ang": 1, "gurmukhi": "x"}))
        self.assertTrue(any("duplicate line ids [2]" in f for f in g.check(BASE, rows, dups, "corpus", "1.4.0")))


class AppendedIds(unittest.TestCase):
    def test_appended_ids_keep_old_ids_valid_but_must_be_recorded(self):
        rows = {**ROWS, 6: (3, "ਹੁਕਮੀ ਹੋਵਨਿ ਜੀਅ")}
        fails = g.check(BASE, rows, [], "corpus", "1.4.0")
        self.assertEqual(len(fails), 1)
        self.assertIn("ids 6..6 are not in", fails[0])
        self.assertEqual(g.check(g.build_baseline(rows, "1.5.0"), rows, [], "corpus", "1.5.0"), [])

    def test_baseline_newer_than_dataset_fails(self):
        self.assertTrue(any("newer than" in f for f in g.check(BASE, dict(ROWS), [], "corpus", "1.3.9")))


def _is_real_sqlite(p):
    try:
        with open(p, "rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


@unittest.skipUnless(_is_real_sqlite(ROOT / g.DB), "needs the real db/sggs.sqlite")
class CommittedBaseline(unittest.TestCase):
    def test_committed_data_matches_the_baseline(self):
        base = json.loads((ROOT / g.BASELINE).read_text(encoding="utf-8"))
        version = (ROOT / "DATASET_VERSION").read_text().strip()
        for label, (rows, dups) in (("corpus", g.rows_from_corpus_text((ROOT / g.CORPUS).read_text(encoding="utf-8"))),
                                    ("db", g.rows_from_db(ROOT / g.DB))):
            self.assertEqual(g.check(base, rows, dups, label, version), [], label)
        self.assertEqual(base["max_id"], 60658)
        self.assertEqual(len(base["blocks"]), 1430)

    def test_a_shifted_id_in_the_real_data_would_fail(self):
        base = json.loads((ROOT / g.BASELINE).read_text(encoding="utf-8"))
        rows, _ = g.rows_from_db(ROOT / g.DB)
        ids = sorted(rows)
        k = ids.index(30000)                     # drop one line mid-Granth: every later id moves down
        shifted = {i: rows[j] for i, j in zip(ids[:k] + ids[k:-1], ids[:k] + ids[k + 1:])}
        fails = g.check(base, shifted, [], "db", "1.4.0", base_rows=rows)
        self.assertTrue(any("changed an existing id" in f for f in fails))
        self.assertTrue(any("id 30000: was" in f for f in fails), fails[:3])


if __name__ == "__main__":
    unittest.main()
