# -*- coding: utf-8 -*-
"""Hukamnama range contract: line-id ranges whose text hash every client must reproduce.

    python3 pipeline/hukamnama_contract.py           # check contract/golden_hukamnama.ndjson
    python3 pipeline/hukamnama_contract.py --write   # regenerate it from db/sggs.sqlite

The Darbar Sahib Hukamnama push names the day's shabad as a corpus line-id range plus a hash of
its text; the phone renders those ids from its own bundled DB and shows them only if its hash
agrees. This file pins that definition with real ranges, so the server, the platform and the iOS
app can each prove they compute the same hash from the same ids.

    range_sha256 = sha256( UTF-8( "\\n".join( NFC(gurmukhi) for id in first_line_id..last_line_id ) ) )

i.e. the `gurmukhi` column of `lines`, ids ascending and inclusive at both ends, each line
Unicode-NFC-normalised, joined by a single U+000A with no trailing newline, hex lowercase.

A range is a whole composition as printed, its heading run included (`comp_id` groups it). The 40
records cover: 32 ordinary shabads on one Ang (spread across the Granth, each with a ਰਹਾਉ line),
4 shabads that run across two Angs, and 4 Vaar readings (the saloks before a pauri plus the pauri,
from four different Vaars). Selection is deterministic: ids only ever grow at the end
(pipeline/line_id_gate.py), so regenerating gives the same file.

The check recomputes every hash from corpus/sggs.jsonl and db/sggs.sqlite and requires the file to
equal what --write produces. Stdlib only; Python 3.9+.
"""
import argparse
import hashlib
import json
import sqlite3
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = "contract/golden_hukamnama.ndjson"
DB = "db/sggs.sqlite"
CORPUS = "corpus/sggs.jsonl"
N_SHABAD, N_TWO_ANG, N_VAAR = 32, 4, 4
FIRST_RAAG_ANG, POST_RAAG_ANG = 14, 1353


def range_sha256(gurmukhi_by_id, first, last):
    """The one definition (see module docstring). Raises KeyError for a missing id."""
    text = "\n".join(unicodedata.normalize("NFC", gurmukhi_by_id[i]) for i in range(first, last + 1))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _spread(items, n):
    """n items evenly spaced through a list, first and last included (deterministic)."""
    if len(items) <= n:
        return list(items)
    return [items[round(k * (len(items) - 1) / (n - 1))] for k in range(n)]


def select(con):
    comps = con.execute(
        "SELECT comp_id, MIN(id), MAX(id), COUNT(*), MIN(ang), MAX(ang), SUM(is_rahao) "
        "FROM lines GROUP BY comp_id ORDER BY MIN(id)").fetchall()
    vaar_comps = {c for (c,) in con.execute("SELECT DISTINCT comp_id FROM vaar_units")}
    span = {c: (lo, hi) for c, lo, hi, *_ in comps}
    shabads = [c for c in comps
               if c[0] not in vaar_comps and c[3] == c[2] - c[1] + 1 and c[6] >= 1
               and c[3] >= 4 and FIRST_RAAG_ANG <= c[4] and c[5] < POST_RAAG_ANG]
    one_ang = [c for c in shabads if c[4] == c[5]]
    two_ang = [c for c in shabads if c[5] == c[4] + 1]
    recs = [("shabad", c[1], c[2]) for c in _spread(one_ang, N_SHABAD)]
    recs += [("two-ang", c[1], c[2]) for c in _spread(two_ang, N_TWO_ANG)]

    # Vaar reading: the run of saloks immediately before one pauri, plus that pauri.
    readings = []
    vaars = [v for (v,) in con.execute("SELECT vaar_id FROM vaars WHERE n_saloks > 0 ORDER BY vaar_id")]
    for v in _spread(vaars, N_VAAR):
        units = con.execute("SELECT seq, kind, comp_id FROM vaar_units WHERE vaar_id = ? ORDER BY seq",
                            (v,)).fetchall()
        pauris = [k for k, u in enumerate(units) if u[1] == "pauri"
                  and k > 0 and units[k - 1][1] == "salok"]
        k = pauris[len(pauris) // 2]                       # a pauri from the middle of the Vaar
        j = k
        while j > 0 and units[j - 1][1] == "salok":
            j -= 1
        lo, hi = span[units[j][2]][0], span[units[k][2]][1]
        readings.append(("vaar", lo, hi))
    return recs + readings


def records(con, gurmukhi_by_id):
    ang = dict(con.execute("SELECT id, ang FROM lines"))
    out = []
    for kind, lo, hi in select(con):
        out.append({"kind": kind, "first_line_id": lo, "last_line_id": hi, "ang": ang[lo],
                    "range_sha256": range_sha256(gurmukhi_by_id, lo, hi)})
    return out


def dump(recs):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)


def corpus_gurmukhi():
    out = {}
    for line in (ROOT / CORPUS).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r["gurmukhi"]
    return out


def check(committed, sources):
    """committed: parsed records; sources: {label: {id: gurmukhi}} -> list of failures."""
    fails = []
    kinds = [r.get("kind") for r in committed]
    for kind, n in (("shabad", N_SHABAD), ("two-ang", N_TWO_ANG), ("vaar", N_VAAR)):
        if kinds.count(kind) != n:
            fails.append(f"{OUT}: expected {n} '{kind}' records, found {kinds.count(kind)}")
    for r in committed:
        lo, hi = r["first_line_id"], r["last_line_id"]
        if not (isinstance(lo, int) and isinstance(hi, int) and 1 <= lo <= hi):
            fails.append(f"{OUT}: bad range {lo}..{hi}")
            continue
        for label, g in sources.items():
            try:
                got = range_sha256(g, lo, hi)
            except KeyError as e:
                fails.append(f"{label}: range {lo}..{hi} names missing id {e}")
                continue
            if got != r["range_sha256"]:
                fails.append(f"{label}: range {lo}..{hi} (Ang {r['ang']}) hashes to {got[:12]}…, "
                             f"contract says {r['range_sha256'][:12]}…")
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help=f"regenerate {OUT}")
    ap.add_argument("--db", default=DB, help=f"database to check (default {DB})")
    a = ap.parse_args(argv)
    if a.write and a.db != DB:
        print(f"FAIL --write generates from the committed {DB} only")
        return 1
    con = sqlite3.connect(f"file:{ROOT / a.db}?mode=ro&immutable=1", uri=True)
    try:
        db_g = dict(con.execute("SELECT id, gurmukhi FROM lines"))
        fresh = dump(records(con, db_g))
    finally:
        con.close()
    path = ROOT / OUT
    if a.write:
        path.parent.mkdir(exist_ok=True)
        path.write_text(fresh, encoding="utf-8")
        print(f"hukamnama contract: wrote {OUT} ({fresh.count(chr(10))} ranges)")
        return 0
    if not path.exists():
        print(f"FAIL {OUT} missing — python3 pipeline/hukamnama_contract.py --write")
        return 1
    text = path.read_text(encoding="utf-8")
    committed = [json.loads(x) for x in text.splitlines() if x.strip()]
    fails = check(committed, {"corpus": corpus_gurmukhi(), "db": db_g})
    if text != fresh:
        fails.append(f"{OUT} differs from what --write generates from the current DB")
    for f in fails:
        print("FAIL", f)
    print(f"hukamnama contract: {'FAIL' if fails else 'PASS'} — {len(committed)} ranges, "
          f"hashes reproduced from corpus + db")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
