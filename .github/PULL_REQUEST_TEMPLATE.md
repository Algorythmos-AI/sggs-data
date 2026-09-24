## What & why

## Scripture impact
- [ ] No Gurmukhi text change (`git diff -- corpus db` is empty or only regenerated derived data)
- [ ] OR every T0 change has a new, reviewed entry in `audit/editorial-ledger.jsonl`

## Verification
- [ ] `make ci` passes (invariants, guard, ledger, fingerprint, tests)
- [ ] For a rebuild: `reconcile.py` char-exact, `golden_test.py` all-pass, `compare_builds.py` proves reproducibility
