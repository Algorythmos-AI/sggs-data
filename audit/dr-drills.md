# Disaster-recovery drills

Each drill rebuilds the dataset from the backups alone and compares it with the release
(runbook: `docs/process/runbooks/data-restore.md`). Newest first. A FAIL is a P1.

| Date (UTC) | Ref | Where | Result |
|---|---|---|---|
| 2026-09-26 04:23 | `ccc22205` | GitHub Actions `dr-drill` (Linux, toolchain container), manual run [36217494673](https://github.com/Algorythmos-AI/sggs-data/actions/runs/36217494673) — the first run with `SGGS_SOURCE_TOKEN` set | **PASS**: rebuilt from the sggs-source releases alone; `corpus/sggs.jsonl` byte-identical; scripture, structure, text tables and FTS indexes identical; integrity gate PASS |
