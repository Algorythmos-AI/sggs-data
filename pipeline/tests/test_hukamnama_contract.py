"""contract/golden_hukamnama.ndjson: the range-hash definition and the committed vector."""
import hashlib
import json
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
import hukamnama_contract as hc  # noqa: E402


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class Definition(unittest.TestCase):
    def test_lines_joined_by_newline_without_trailing_newline(self):
        g = {7: "ਸਤਿ ਨਾਮੁ", 8: "ਕਰਤਾ ਪੁਰਖੁ ॥", 9: "ਨਿਰਭਉ"}
        self.assertEqual(hc.range_sha256(g, 7, 8), _sha("ਸਤਿ ਨਾਮੁ\nਕਰਤਾ ਪੁਰਖੁ ॥"))
        self.assertEqual(hc.range_sha256(g, 9, 9), _sha("ਨਿਰਭਉ"))

    def test_each_line_is_nfc(self):
        # U+0A59 (ਖ਼) is a composition exclusion: NFC writes it as ਖ + nukta (U+0A16 U+0A3C)
        self.assertEqual(hc.range_sha256({1: "ਖ਼"}, 1, 1), _sha("ਖ਼"))

    def test_range_is_inclusive_and_missing_id_raises(self):
        with self.assertRaises(KeyError):
            hc.range_sha256({1: "a", 3: "c"}, 1, 3)

    def test_check_flags_a_wrong_hash(self):
        g = {1: "ਸਤਿ", 2: "ਨਾਮੁ"}
        rec = {"kind": "shabad", "first_line_id": 1, "last_line_id": 2, "ang": 1, "range_sha256": "0" * 64}
        self.assertTrue(any("hashes to" in f for f in hc.check([rec], {"db": g})))


def _is_real_sqlite(p):
    try:
        with open(p, "rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


@unittest.skipUnless(_is_real_sqlite(ROOT / hc.DB), "needs the real db/sggs.sqlite")
class CommittedContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = sqlite3.connect(f"file:{ROOT / hc.DB}?mode=ro&immutable=1", uri=True)
        cls.db_g = dict(cls.con.execute("SELECT id, gurmukhi FROM lines"))
        cls.text = (ROOT / hc.OUT).read_text(encoding="utf-8")
        cls.recs = [json.loads(x) for x in cls.text.splitlines() if x.strip()]

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_hashes_reproduce_from_corpus_and_db(self):
        self.assertEqual(hc.check(self.recs, {"corpus": hc.corpus_gurmukhi(), "db": self.db_g}), [])

    def test_file_is_what_the_script_generates(self):
        self.assertEqual(self.text, hc.dump(hc.records(self.con, self.db_g)))

    def test_coverage(self):
        self.assertEqual(len(self.recs), 40)
        ang = dict(self.con.execute("SELECT id, ang FROM lines"))
        comp = dict(self.con.execute("SELECT id, comp_id FROM lines"))
        for r in self.recs:
            lo, hi = r["first_line_id"], r["last_line_id"]
            angs = {ang[i] for i in range(lo, hi + 1)}
            comps = {comp[i] for i in range(lo, hi + 1)}
            if r["kind"] == "shabad":
                self.assertEqual(len(angs), 1, r)
            if r["kind"] == "two-ang":
                self.assertEqual(len(angs), 2, r)
            if r["kind"] in ("shabad", "two-ang"):
                self.assertEqual(len(comps), 1, r)       # exactly one whole composition
                self.assertEqual(lo, min(i for i in comp if comp[i] == comp[lo]))
                self.assertEqual(hi, max(i for i in comp if comp[i] == comp[lo]))
            if r["kind"] == "vaar":
                kinds = [k for (k,) in self.con.execute(
                    "SELECT kind FROM vaar_units WHERE comp_id IN (%s) ORDER BY seq" % ",".join("?" * len(comps)),
                    sorted(comps))]
                self.assertEqual(kinds[-1], "pauri", r)
                self.assertGreaterEqual(kinds.count("salok"), 1, r)
                self.assertEqual(kinds.count("pauri"), 1, r)


if __name__ == "__main__":
    unittest.main()
