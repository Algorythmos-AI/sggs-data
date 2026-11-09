# -*- coding: utf-8 -*-
"""Line-id stability: an existing line `id` always names the same (ang, gurmukhi). New ids are appended.

    python3 pipeline/line_id_gate.py                     # check corpus + DB against the baseline
    python3 pipeline/line_id_gate.py --update            # record appended ids (refuses on any shift)
    python3 pipeline/line_id_gate.py --update --rebaseline "E-0012: <reason>"
                                                         # sanctioned editorial change (MAJOR bump only)

Why: clients address scripture by line id and render it from their OWN bundled copy of the
dataset — the Darbar Sahib Hukamnama push sends `first_line_id..last_line_id` and the phone draws
those ids from its DB. That is safe only if an id never moves between builds. `build_corpus.py`
numbers lines 1..N in page order, so one line split, merged, inserted or dropped anywhere would
silently shift every later id; this gate makes that a hard failure.

The baseline, audit/line-id-baseline.json, is the mapping as last released, compressed to one
block per Ang: (ang, first_id, last_id, sha256) where the hash covers
"{id}\\t{ang}\\t{gurmukhi}\\n" for every id in the block (gurmukhi as stored, UTF-8, no
normalisation). Checks (exit 1 on any failure), against corpus/sggs.jsonl AND db/sggs.sqlite:

  1. every baseline id still exists with the same ang and the same gurmukhi, byte for byte;
  2. ids are 1..N with no gap or duplicate;
  3. no id beyond the baseline's max_id is unrecorded (run --update to record appended ids, so
     they are protected from the next build on);
  4. the baseline's dataset_version is not newer than DATASET_VERSION.

On a failing block the gate names the exact ids, reading the corpus from the commit that last
wrote the baseline (best effort; the block hash alone is proof enough to fail).

--update writes the baseline from the current data and refuses while check 1 fails. The only way
past check 1 is --rebaseline with a reason (an editorial-ledger entry id), allowed only when
DATASET_VERSION's MAJOR is above the baseline's (CONTRIBUTING: any editorial change is MAJOR);
it is recorded in the baseline's `rebaselines` history. Stdlib only; Python 3.9+.
"""
import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "audit/line-id-baseline.json"
CORPUS = "corpus/sggs.jsonl"
DB = "db/sggs.sqlite"
SCHEMA = 1


def _row_bytes(i, ang, gurmukhi):
    return f"{i}\t{ang}\t{gurmukhi}\n".encode("utf-8")


def rows_from_corpus_text(text):
    """{id: (ang, gurmukhi)} from JSONL text; duplicate ids are reported by check()."""
    out, dups = {}, []
    for line in text.splitlines():
        if line.strip():
            r = json.loads(line)
            if r["id"] in out:
                dups.append(r["id"])
            out[r["id"]] = (r["ang"], r["gurmukhi"])
    return out, dups


def rows_from_db(path):
    con = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        rows = con.execute("SELECT id, ang, gurmukhi FROM lines ORDER BY id").fetchall()
    finally:
        con.close()
    return {i: (a, g) for i, a, g in rows}, []


def build_baseline(rows, dataset_version, rebaselines=()):
    """One block per Ang over ids in order. Assumes ids are 1..N (check() proves it first)."""
    blocks, cur = [], None
    whole = hashlib.sha256()
    for i in sorted(rows):
        ang, g = rows[i]
        b = _row_bytes(i, ang, g)
        whole.update(b)
        if cur is None or cur["ang"] != ang:
            if cur:
                blocks.append([cur["ang"], cur["first"], cur["last"], cur["h"].hexdigest()])
            cur = {"ang": ang, "first": i, "last": i, "h": hashlib.sha256()}
        cur["last"] = i
        cur["h"].update(b)
    if cur:
        blocks.append([cur["ang"], cur["first"], cur["last"], cur["h"].hexdigest()])
    return {
        "schema": SCHEMA,
        "about": "line id -> (ang, gurmukhi) as last released; checked by pipeline/line_id_gate.py",
        "row_hash": "sha256 over UTF-8 '{id}\\t{ang}\\t{gurmukhi}\\n' per id in the block, id order",
        "dataset_version": dataset_version,
        "max_id": max(rows) if rows else 0,
        "mapping_sha256": whole.hexdigest(),
        "rebaselines": list(rebaselines),
        "blocks": blocks,
    }


def dump_baseline(b):
    """Readable JSON with one block per line, so a review diff shows exactly which Angs moved."""
    head = {k: v for k, v in b.items() if k != "blocks"}
    text = json.dumps(head, ensure_ascii=False, indent=2)[:-2]
    rows = ",\n".join("    " + json.dumps(x) for x in b["blocks"])
    return f'{text},\n  "blocks": [\n{rows}\n  ]\n}}\n'


def _block_sha(rows, first, last):
    h = hashlib.sha256()
    for i in range(first, last + 1):
        if i not in rows:
            return None
        h.update(_row_bytes(i, *rows[i]))
    return h.hexdigest()


def shifted_blocks(baseline, rows):
    """Baseline blocks whose ids no longer map to the same (ang, gurmukhi)."""
    return [b for b in baseline["blocks"] if _block_sha(rows, b[1], b[2]) != b[3]]


def explain(bad_blocks, rows, base_rows, limit=20):
    """Exact ids for failing blocks, given the baseline's rows (or None)."""
    if base_rows is None:
        return []
    out = []
    for ang, first, last, _ in bad_blocks:
        for i in range(first, last + 1):
            if rows.get(i) != base_rows.get(i):
                was, now = base_rows.get(i), rows.get(i)
                out.append(f"id {i}: was {was!r} now {now!r}")
                if len(out) >= limit:
                    return out
    return out


def _version(v):
    return tuple(int(x) for x in v.strip().split("."))


def check(baseline, rows, dups, label, dataset_version=None, base_rows=None):
    fails = []
    if baseline.get("schema") != SCHEMA:
        return [f"{BASELINE}: unknown schema {baseline.get('schema')!r}"]
    if dups:
        fails.append(f"{label}: duplicate line ids {sorted(set(dups))[:10]}")
    n = max(rows) if rows else 0
    gaps = [i for i in range(1, n + 1) if i not in rows]
    if gaps or (rows and min(rows) < 1):
        fails.append(f"{label}: line ids are not 1..{n} — missing {gaps[:10]}")
    bad = shifted_blocks(baseline, rows)
    if bad:
        angs = [b[0] for b in bad]
        fails.append(f"{label}: {len(bad)} Ang block(s) changed an existing id -> (ang, gurmukhi) mapping "
                     f"(Angs {angs[:15]}{' …' if len(angs) > 15 else ''}); ids are never shifted, "
                     f"reused or rewritten — new lines take ids above {baseline['max_id']}")
        fails += [f"{label}:   {d}" for d in explain(bad, rows, base_rows)]
    if n > baseline["max_id"] and not bad:
        fails.append(f"{label}: ids {baseline['max_id'] + 1}..{n} are not in {BASELINE} — record the "
                     f"appended ids: python3 pipeline/line_id_gate.py --update")
    if dataset_version and _version(baseline["dataset_version"]) > _version(dataset_version):
        fails.append(f"{BASELINE} dataset_version {baseline['dataset_version']} is newer than "
                     f"DATASET_VERSION {dataset_version}")
    return fails


def _git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None


def baseline_rows_from_git():
    """The corpus at the commit that last wrote the baseline, for naming exact ids. Best effort."""
    sha = (_git("log", "-1", "--format=%H", "--", BASELINE) or "").strip()
    if not sha:
        return None
    text = _git("show", f"{sha}:{CORPUS}")
    return rows_from_corpus_text(text)[0] if text else None


def _is_real_sqlite(p):
    try:
        with open(p, "rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--update", action="store_true", help="write the baseline from the current data")
    ap.add_argument("--rebaseline", metavar="REASON",
                    help="with --update: accept a changed mapping (editorial-ledger id + reason; MAJOR bump)")
    ap.add_argument("--corpus", default=CORPUS, help=f"corpus JSONL to check (default {CORPUS})")
    ap.add_argument("--db", default=DB, help=f"database to check (default {DB})")
    ap.add_argument("--no-db", action="store_true", help="check the corpus only (DB not materialised)")
    a = ap.parse_args(argv)
    if a.update and (a.corpus != CORPUS or a.db != DB):
        print("FAIL --update records the committed corpus/DB only")
        return 1

    version = (ROOT / "DATASET_VERSION").read_text().strip()
    sources = [("corpus", *rows_from_corpus_text((ROOT / a.corpus).read_text(encoding="utf-8")))]
    if not a.no_db:
        if not _is_real_sqlite(ROOT / a.db):
            print(f"FAIL {a.db} is not a real SQLite file (git lfs pull --include {DB}, or pass --no-db)")
            return 1
        sources.append(("db", *rows_from_db(ROOT / a.db)))
    if len(sources) == 2 and sources[0][1] != sources[1][1]:
        print("FAIL corpus and db disagree on id -> (ang, gurmukhi); rebuild the DB from the corpus")
        return 1

    path = ROOT / BASELINE
    baseline = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    if a.update:
        rows, dups = sources[0][1], sources[0][2]
        history = list(baseline.get("rebaselines", [])) if baseline else []
        if baseline:
            fails = [f for f in check(baseline, rows, dups, "corpus", version) if "not in " + BASELINE not in f]
            if fails and not a.rebaseline:
                for f in fails:
                    print("FAIL", f)
                print("line-id gate: refusing to --update over a changed mapping (see --rebaseline)")
                return 1
            if fails:
                if _version(version)[0] <= _version(baseline["dataset_version"])[0]:
                    print(f"FAIL --rebaseline needs a MAJOR dataset bump: DATASET_VERSION {version} vs "
                          f"baseline {baseline['dataset_version']}")
                    return 1
                history.append({"dataset_version": version, "reason": a.rebaseline,
                                "changed_blocks": [b[0] for b in shifted_blocks(baseline, rows)]})
        new = build_baseline(rows, version, history)
        path.write_text(dump_baseline(new), encoding="utf-8")
        print(f"line-id gate: wrote {BASELINE} — {new['max_id']:,} ids in {len(new['blocks'])} Ang blocks "
              f"(dataset {version})")
        return 0

    if baseline is None:
        print(f"FAIL {BASELINE} missing — record it: python3 pipeline/line_id_gate.py --update")
        return 1
    base_rows = None
    fails = []
    for label, rows, dups in sources:
        f = check(baseline, rows, dups, label, version)
        if f and base_rows is None and shifted_blocks(baseline, rows):
            base_rows = baseline_rows_from_git()
            f = check(baseline, rows, dups, label, version, base_rows)
        fails += f
    for f in fails:
        print("FAIL", f)
    scope = " + ".join(s[0] for s in sources)
    state = "FAIL — see above" if fails else "PASS — unchanged:"
    print(f"line-id gate: {state} {baseline['max_id']:,} ids in {len(baseline['blocks'])} Ang blocks "
          f"({scope}; baseline dataset {baseline['dataset_version']})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
