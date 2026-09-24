"""pipeline/data_quality.py — the structural contract every dataset keeps."""
import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
import data_quality as dq  # noqa: E402

REAL_DB = ROOT / "db" / "sggs.sqlite"


def _is_real_sqlite(p):
    try:
        with open(p, "rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def _tiny(rows, translations=(), concept_lines=()):
    d = tempfile.mkdtemp()
    path = Path(d) / "t.sqlite"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE lines (id INTEGER PRIMARY KEY, ang INT, comp_id INT, gurmukhi TEXT, text TEXT,"
                " is_header INT, translit_norm TEXT)")
    con.execute("CREATE TABLE translations (line_id INT, text TEXT)")
    con.execute("CREATE TABLE concept_lines (concept TEXT, line_id INT)")
    con.executemany("INSERT INTO lines VALUES (?,?,?,?,?,?,?)", rows)
    con.executemany("INSERT INTO translations VALUES (?,?)", translations)
    con.executemany("INSERT INTO concept_lines VALUES (?,?)", concept_lines)
    con.commit()
    con.close()
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


GOOD = [(1, 1, 2, "ੴ ਸਤਿ ਨਾਮੁ", "ੴ ਸਤਿ ਨਾਮੁ", 1, "ik"), (2, 1, 2, "ਸੋਚੈ ਸੋਚਿ", "ਸੋਚੈ ਸੋਚਿ", 0, "soch")]


class HardRules(unittest.TestCase):
    def test_script_and_reference_violations_are_caught(self):
        con = _tiny(GOOD + [(3, 2, 4, "ਨਾਨਕ x", "ਨਾਨਕ", 0, "naanak")],
                    translations=[(2, "Thinking ਨਾਮੁ")], concept_lines=[("naam", 99)])
        p = "\n".join(dq.hard_rules(con))
        self.assertIn("Latin letters in lines.gurmukhi at ids [3]", p)
        self.assertIn("Gurmukhi in the English layer at line_ids [2]", p)
        self.assertIn("concept_lines.line_id point at a missing line", p)
        self.assertIn("shape:", p)            # a tiny database is not the Granth

    def test_isolated_signs_are_measured(self):
        con = _tiny(GOOD + [(3, 699, 5, "ਹਰਿ ੁ ਨਾਮ", "ਹਰਿ", 0, "har"), (4, 699, 5, "ਹਰਿ ਨਾਮ", "ਹਰਿ", 0, "")])
        m = dq.measure(con)["review_rows"]
        self.assertEqual(list(m["isolated_sign"]), ["3"])
        self.assertEqual(m["empty_translit_norm"], [4])


class Baseline(unittest.TestCase):
    BASE = {"comp_id": {"count": 3, "max": 5, "gaps": 2, "gaps_sha256": "g", "null": 0},
            "headers": {"count": 1, "ids_sha256": "h"},
            "review_rows": {"isolated_sign": {"7": "a", "9": "b"}, "empty_translit_norm": [35328]}}

    def test_identical_passes(self):
        self.assertEqual(dq.against_baseline(copy.deepcopy(self.BASE), self.BASE), [])

    def test_every_tracked_change_fails(self):
        now = copy.deepcopy(self.BASE)
        now["comp_id"]["gaps"], now["comp_id"]["gaps_sha256"] = 3, "g2"
        now["headers"]["ids_sha256"] = "h2"
        now["review_rows"]["isolated_sign"] = {"7": "a-changed", "11": "c"}   # 7 edited, 9 lost, 11 new
        now["review_rows"]["empty_translit_norm"] = []                         # silently "fixed"
        p = "\n".join(dq.against_baseline(now, self.BASE))
        for expected in ("comp_id: gaps is 3", "headers:", "line 7's Gurmukhi changed",
                         "line 9 no longer has its isolated sign", "line 11 newly has an isolated sign",
                         "empty translit_norm at []"):
            with self.subTest(expected=expected):
                self.assertIn(expected, p)


@unittest.skipUnless(_is_real_sqlite(REAL_DB), "needs the real db/sggs.sqlite")
class RealDataset(unittest.TestCase):
    def test_committed_dataset_meets_the_contract(self):
        con = sqlite3.connect(f"file:{REAL_DB}?mode=ro&immutable=1", uri=True)
        self.assertEqual(dq.hard_rules(con), [])
        base = json.loads(dq.BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(dq.against_baseline(dq.measure(con), base), [])


if __name__ == "__main__":
    unittest.main()
