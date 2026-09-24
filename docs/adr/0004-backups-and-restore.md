# ADR-0004: The dataset is recoverable from its private backups alone, and that is drilled

**Status:** accepted (2026-09-24)

**Context.** The source PDF, the English translation sources and the ShabadOS database (the Nitnem
input) are not in this repository. The PDF once lived on one laptop; the ShabadOS file was an
unpinned third-party download. Losing either would make the dataset impossible to rebuild.

**Decision.** Every rebuild input is backed up in the private `Algorythmos-AI/sggs-source` repository
(releases `source-pdf-v1`, `translations-en-v1`, `shabados-database-4.8.7`; never replaced), pinned
by a committed hash, restored only through verifying scripts, and refused by the rebuild when missing
or altered. `scripts/data/dr_drill.sh` restores the dataset from those backups into a fresh clone,
rebuilds with every gate and requires identical data; the `dr-drill` workflow runs it on a clean
runner every quarter with the pinned toolchain. Results are logged in `audit/dr-drills.md`.

**Consequences.** Recovery is one command and is known to work, not assumed. Copies 2 and 3 of the
3-2-1 plan (an object-lock bucket, an offline drive) remain owner decisions. The drill needs a
read-only token for `sggs-source` (`SGGS_SOURCE_TOKEN`).
