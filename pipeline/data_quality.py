# -*- coding: utf-8 -*-
"""Data-quality contract — the structural rules every dataset must keep.

    python3 pipeline/data_quality.py [DB]                    # check against audit/data-quality-baseline.json
    python3 pipeline/data_quality.py [DB] --write-baseline   # record the reviewed state (a reviewed PR only)

The fingerprints (sggs_integrity.py) prove the data is *the same*; this proves it is *well formed*
and that the things reviewers track are still exactly as reviewed:

  shape        60,658 lines over Angs 1–1430, every Ang present
  comp_id      no line without one; the set of unused ids (gaps: ids vacated by the heading
               regroup or burned by the v1.1.4 header fix) equals the baseline — an id is never
               reused, and a new gap is a reviewed change
  headers      the set of heading lines equals the baseline (the reviewed header list)
  script       no Latin letter in any Gurmukhi column; no Gurmukhi in the English layer
  references   no translation, concept, bani, neighbour or vaar row points at a missing line;
               PRAGMA foreign_key_check is clean
  review rows  lines with a vowel sign that has no base consonant (source-faithful, flagged for
               scholarly review) and lines with an empty translit_norm: the exact rows and their
               Gurmukhi equal the baseline, so they are never silently "fixed" or lost

A change to any baselined set fails until the baseline is re-recorded in a reviewed PR. Opens the
database read-only; stdlib only.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "audit" / "data-quality-baseline.json"
LINES, ANGS = 60658, 1430
LATIN = re.compile(r"[A-Za-z]")
GURMUKHI = re.compile(r"[\u0A00-\u0A7F]")
# A vowel sign, bindi/tippi or addak with no base consonant before it (start of line, after a
# space or a danda). The source prints these; they are kept verbatim and tracked for review.
ISOLATED_SIGN = re.compile(r"(^|[\s\u0964\u0965])[\u0A3E-\u0A4D\u0A70\u0A71]")
# (table, column) pairs that must point at an existing lines.id when not NULL.
LINE_REFERENCES = (("translations", "line_id"), ("concept_lines", "line_id"), ("bani_lines", "line_id"),
                   ("line_neighbors", "line_id"), ("line_neighbors", "neighbor_id"),
                   ("vaar_units", "first_line_id"))


def _sha(values) -> str:
    return hashlib.sha256("\n".join(map(str, values)).encode("utf-8")).hexdigest()


def measure(con) -> dict:
    q = lambda sql, *a: con.execute(sql, a).fetchall()  # noqa: E731
    n, lo, hi, distinct = q("SELECT COUNT(*), MIN(ang), MAX(ang), COUNT(DISTINCT ang) FROM lines")[0]
    comp_ids = {r[0] for r in q("SELECT DISTINCT comp_id FROM lines WHERE comp_id IS NOT NULL")}
    top = max(comp_ids) if comp_ids else 0
    gaps = sorted(set(range(1, top + 1)) - comp_ids)
    headers = [r[0] for r in q("SELECT id FROM lines WHERE is_header = 1 ORDER BY id")]
    isolated = [(i, hashlib.sha256((g or "").encode("utf-8")).hexdigest())
                for i, g in q("SELECT id, gurmukhi FROM lines ORDER BY id") if ISOLATED_SIGN.search(g or "")]
    empty_norm = [r[0] for r in q("SELECT id FROM lines WHERE COALESCE(translit_norm, '') = '' ORDER BY id")]
    return {
        "shape": {"lines": n, "min_ang": lo, "max_ang": hi, "distinct_angs": distinct},
        "comp_id": {"null": q("SELECT COUNT(*) FROM lines WHERE comp_id IS NULL")[0][0],
                    "count": len(comp_ids), "max": top, "gaps": len(gaps), "gaps_sha256": _sha(gaps)},
        "headers": {"count": len(headers), "ids_sha256": _sha(headers)},
        "review_rows": {"isolated_sign": {str(i): h for i, h in isolated},
                        "empty_translit_norm": empty_norm},
    }


def hard_rules(con) -> list[str]:
    """Rules that hold for every dataset, independent of any baseline."""
    problems = []
    m = measure(con)["shape"]
    if (m["lines"], m["min_ang"], m["max_ang"], m["distinct_angs"]) != (LINES, 1, ANGS, ANGS):
        problems.append(f"shape: {m} (expected {LINES} lines over Angs 1–{ANGS}, every Ang present)")
    if con.execute("SELECT COUNT(*) FROM lines WHERE comp_id IS NULL").fetchone()[0]:
        problems.append("comp_id: a line has no comp_id")
    cols = {r[1] for r in con.execute("PRAGMA table_info(lines)")}
    for col in ("gurmukhi", "text"):
        if col in cols:
            bad = [i for i, v in con.execute(f"SELECT id, {col} FROM lines") if LATIN.search(v or "")]
            if bad:
                problems.append(f"script: Latin letters in lines.{col} at ids {bad[:10]}")
    bad = [i for i, t in con.execute("SELECT line_id, text FROM translations") if GURMUKHI.search(t or "")]
    if bad:
        problems.append(f"script: Gurmukhi in the English layer at line_ids {bad[:10]}")
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    for table, col in LINE_REFERENCES:
        if table in tables and col in {r[1] for r in con.execute(f'PRAGMA table_info("{table}")')}:
            orphans = con.execute(f'SELECT COUNT(*) FROM "{table}" t LEFT JOIN lines l ON l.id = t."{col}" '
                                  f'WHERE t."{col}" IS NOT NULL AND l.id IS NULL').fetchone()[0]
            if orphans:
                problems.append(f"references: {orphans} row(s) of {table}.{col} point at a missing line")
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    if fk:
        problems.append(f"references: PRAGMA foreign_key_check reports {len(fk)} violation(s)")
    return problems


def against_baseline(now: dict, base: dict) -> list[str]:
    problems = []
    for key in ("count", "max", "gaps", "gaps_sha256"):
        if now["comp_id"][key] != base["comp_id"][key]:
            problems.append(f"comp_id: {key} is {now['comp_id'][key]}, baseline {base['comp_id'][key]} "
                            "(ids are never reused; a new gap is a reviewed change)")
    if now["headers"] != base["headers"]:
        problems.append(f"headers: {now['headers']['count']} heading lines, baseline {base['headers']['count']} "
                        "(the heading set changed — review it)")
    ni, bi = now["review_rows"]["isolated_sign"], base["review_rows"]["isolated_sign"]
    for lid in sorted(set(ni) | set(bi), key=int):
        if lid not in ni:
            problems.append(f"review rows: line {lid} no longer has its isolated sign — changed without review?")
        elif lid not in bi:
            problems.append(f"review rows: line {lid} newly has an isolated sign — review it")
        elif ni[lid] != bi[lid]:
            problems.append(f"review rows: line {lid}'s Gurmukhi changed")
    if now["review_rows"]["empty_translit_norm"] != base["review_rows"]["empty_translit_norm"]:
        problems.append(f"review rows: empty translit_norm at {now['review_rows']['empty_translit_norm']}, "
                        f"baseline {base['review_rows']['empty_translit_norm']}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("db", nargs="?", default=str(ROOT / "db" / "sggs.sqlite"))
    ap.add_argument("--baseline", default=str(BASELINE))
    ap.add_argument("--write-baseline", action="store_true", help="record the current state (a reviewed PR only)")
    a = ap.parse_args(argv)
    con = sqlite3.connect(f"file:{Path(a.db).resolve()}?mode=ro&immutable=1", uri=True)
    problems = hard_rules(con)
    now = measure(con)
    if a.write_baseline:
        if problems:
            for p in problems:
                print("FAIL", p)
            print("refusing to record a baseline for a dataset that breaks the hard rules")
            return 1
        Path(a.baseline).write_text(json.dumps(now, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"baseline written: {a.baseline}")
        return 0
    problems += against_baseline(now, json.loads(Path(a.baseline).read_text(encoding="utf-8")))
    for p in problems:
        print("FAIL", p)
    rr = now["review_rows"]
    print(f"data quality: {'PASS' if not problems else f'{len(problems)} problem(s)'} — "
          f"{now['shape']['lines']} lines, {now['comp_id']['count']} compositions ({now['comp_id']['gaps']} gaps), "
          f"{now['headers']['count']} headings, {len(rr['isolated_sign'])} isolated-sign + "
          f"{len(rr['empty_translit_norm'])} empty-translit_norm rows tracked for review")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
