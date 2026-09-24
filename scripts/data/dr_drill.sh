#!/usr/bin/env bash
# dr_drill.sh — disaster-recovery drill: rebuild the dataset from the off-site backups alone and
# prove it is the same data. Runbook: docs/process/runbooks/data-restore.md.
#
#   bash scripts/data/dr_drill.sh [--ref REF] [--workdir DIR] [--allow-float-tables]
#
# 1. a FRESH clone of Algorythmos-AI/sggs-data at REF (default: main) — nothing from this checkout;
# 2. every input restored from the private backup Algorythmos-AI/sggs-source, each hash-verified:
#    the source PDF (source-pdf-v1), the English translation sources (translations-en-v1) and the
#    ShabadOS database (shabados-database-4.8.7);
# 3. the full fail-hard rebuild (pipeline/rebuild_all.sh: reconcile char-exact, golden checks, every
#    gate, atomic install);
# 4. the rebuilt corpus must be byte-identical to the committed one, and the rebuilt database's
#    fingerprint must equal the committed audit/dataset-fingerprint.json.
#
# Pass = scripture (scripture_sha256, t0_sha256), every table and every FTS index identical.
# --allow-float-tables (for a drill on a different platform than the one that built the release,
# e.g. a Linux runner vs macOS): a difference confined to tables whose values include floats
# (computed analytics such as neighbour cosines) is reported as WARN instead of FAIL. Scripture,
# structure, text and index differences always fail.
set -euo pipefail
REF=main; WORK=""; ALLOW_FLOAT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --ref) REF="$2"; shift 2 ;;
    --workdir) WORK="$2"; shift 2 ;;
    --allow-float-tables) ALLOW_FLOAT=1; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
WORK="${WORK:-$(mktemp -d)}"
PY="${PIPELINE_PY:-python3}"
say() { printf '\n== %s\n' "$*"; }

say "1/4 fresh clone of sggs-data at $REF → $WORK/sggs-data"
rm -rf "$WORK/sggs-data" "$WORK/input"; mkdir -p "$WORK/input"
GIT_LFS_SKIP_SMUDGE=1 git clone -q https://github.com/Algorythmos-AI/sggs-data.git "$WORK/sggs-data"
cd "$WORK/sggs-data"
git -c advice.detachedHead=false checkout -q "$REF"
SHA="$(git rev-parse HEAD)"
echo "  commit $SHA"

say "2/4 restore every input from the private backup (hash-verified)"
gh release download source-pdf-v1 --repo Algorythmos-AI/sggs-source --dir "$WORK/input"
(cd "$WORK/input" && shasum -a 256 -c SHA256SUMS)
PDF="$WORK/input/Siri-Guru-Granth-Sahib-in-Gurmukhi-with-Index.pdf"
bash scripts/data/fetch_translations.sh
bash scripts/data/fetch_shabados.sh

say "3/4 full rebuild from the PDF (fail-hard; every gate)"
"$PY" -c "import fitz, numpy, scipy" || { echo "the rebuild needs PyMuPDF, numpy and scipy in $PY" >&2; exit 1; }
PATH="$(dirname "$(command -v "$PY")"):$PATH" bash pipeline/rebuild_all.sh "$PDF"

say "4/4 prove it is the same data"
git diff --quiet -- corpus/sggs.jsonl || { echo "FAIL: the rebuilt corpus differs from the committed corpus" >&2; exit 1; }
echo "  corpus/sggs.jsonl byte-identical"
set +e
DIFFS="$(python3 pipeline/sggs_integrity.py db/sggs.sqlite --compare audit/dataset-fingerprint.json | grep '^DIFF ' | sed 's/^DIFF //')"
set -e
python3 - "$ALLOW_FLOAT" "$SHA" "$(uname -s)" <<PY
import sqlite3, sys
allow, sha, platform = sys.argv[1] == "1", sys.argv[2], sys.argv[3]
diffs = [d for d in """$DIFFS""".split() if d]
con = sqlite3.connect("file:db/sggs.sqlite?mode=ro", uri=True)
def has_floats(table):
    cols = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]
    return any(con.execute(f'SELECT 1 FROM "{table}" WHERE typeof("{c}") = \'real\' LIMIT 1').fetchone()
               for c in cols)
hard, soft = [], []
for d in diffs:
    kind, _, name = d.partition(".")
    (soft if kind == "tables" and has_floats(name) else hard).append(d)
if hard or (soft and not allow):
    for d in hard + soft:
        print("  DIFF", d)
    print(f"RESULT: FAIL — {len(hard) + len(soft)} difference(s) · sggs-data@{sha[:12]} · {platform}")
    sys.exit(1)
for d in soft:
    print("  WARN", d, "(float-valued analytics; cross-platform arithmetic)")
note = f"; {len(soft)} float-valued table(s) differ (cross-platform)" if soft else ""
print(f"RESULT: PASS — scripture, structure, text tables and FTS indexes identical{note} · "
      f"sggs-data@{sha[:12]} · {platform}")
PY
