"""The numbers docs/architecture/database-schema.md states about comp_id are the database's numbers.

The page is published on the engineering wiki (docs.gurbanisoul.com/data/…); its counts drifted once
(4,706 / 5,380, from before the v1.1.4 header fix). A rebuild that changes them now fails here until
the page says the same thing.
"""
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL_DB = ROOT / "db" / "sggs.sqlite"
PAGE = ROOT / "docs" / "architecture" / "database-schema.md"


def _is_real_sqlite(p):
    try:
        with open(p, "rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def _stated(pattern: str) -> int:
    m = re.search(pattern, PAGE.read_text(encoding="utf-8"))
    if not m:
        raise AssertionError(f"database-schema.md no longer states {pattern!r}; update this test with the page")
    return int(m.group(1).replace(",", ""))


@unittest.skipUnless(_is_real_sqlite(REAL_DB), "needs the real db/sggs.sqlite")
class SchemaPageFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(f"file:{REAL_DB}?mode=ro&immutable=1", uri=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def q(self, sql):
        return self.db.execute(sql).fetchone()[0]

    def test_distinct_compositions(self):
        self.assertEqual(_stated(r"distinct compositions \*\*([\d,]+)\*\*"), self.q("SELECT COUNT(DISTINCT comp_id) FROM lines"))

    def test_max_comp_id(self):
        self.assertEqual(_stated(r"`max\(comp_id\)` \*\*([\d,]+)\*\*"), self.q("SELECT MAX(comp_id) FROM lines"))

    def test_comp_id_1_is_a_gap(self):
        self.assertIn("`comp_id` 1 is a gap", PAGE.read_text(encoding="utf-8"))
        self.assertEqual(self.q("SELECT COUNT(*) FROM lines WHERE comp_id = 1"), 0)

    def test_header_only_compositions(self):
        self.assertEqual(_stated(r"Exactly \*\*(\d+)\*\* header-only compositions"),
                         self.q("SELECT COUNT(*) FROM (SELECT comp_id FROM lines GROUP BY comp_id HAVING MIN(is_header) = 1)"))


if __name__ == "__main__":
    unittest.main()
