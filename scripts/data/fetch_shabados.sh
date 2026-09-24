#!/usr/bin/env bash
# fetch_shabados.sh [TAG] — restore the ShabadOS open database (database.sqlite, release 4.8.7) that
# the Nitnem layer is built from (pipeline/banis/build_banis.py) from the PRIVATE backup
# Algorythmos-AI/sggs-source, so a rebuild never depends on a third-party release staying available.
# The file is verified against the committed pipeline/shabados.SHA256SUMS before it is installed at
# the repository root; a mismatch installs nothing. Needs `gh` with read access to sggs-source.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
TAG="${1:-shabados-database-4.8.7}"
if shasum -a 256 -c pipeline/shabados.SHA256SUMS >/dev/null 2>&1; then
  echo "database.sqlite already present and verified"; exit 0
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
gh release download "$TAG" --repo Algorythmos-AI/sggs-source --dir "$TMP" --pattern database.sqlite
(cd "$TMP" && shasum -a 256 -c "$OLDPWD/pipeline/shabados.SHA256SUMS" >/dev/null) \
  || { echo "fetched database.sqlite does not match pipeline/shabados.SHA256SUMS — nothing installed" >&2; exit 1; }
mv "$TMP/database.sqlite" database.sqlite.tmp && mv database.sqlite.tmp database.sqlite
shasum -a 256 -c pipeline/shabados.SHA256SUMS >/dev/null
echo "database.sqlite restored and verified ($TAG)"
