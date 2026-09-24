# Contributing to sggs-data

1. **Never edit Gurmukhi text** in `corpus/` or `db/`. Flag suspected issues with a *scripture fidelity*
   issue; a Granthi/scholar decides. A sanctioned correction is a new entry in
   `audit/editorial-ledger.jsonl` with its evidence and two reviews.
2. Branch from `main`, open a PR, and keep `make ci` green. Conventional-commit PR titles
   (`data: …`, `fix(pipeline): …`).
3. A rebuild must pass `reconcile.py` (char-exact) and `golden_test.py`, keep every fingerprint
   in `audit/dataset-fingerprint.json` explained, and be reproducible (`make compare-builds`).
4. Bump `DATASET_VERSION` for a data release (SemVer: MAJOR = schema break or any editorial change,
   MINOR = new/changed derived tables, PATCH = metadata). Authorship is the contributor's own.
