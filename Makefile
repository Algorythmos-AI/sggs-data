# sggs-data — the verbatim corpus, the SQLite dataset and the pipeline that builds and proves them.
# `make help` lists targets. PIPELINE_PY is the interpreter with PyMuPDF/numpy/scipy.
PIPELINE_PY ?= /usr/bin/python3
PDF ?= ../Siri-Guru-Granth-Sahib-in-Gurmukhi-with-Index.pdf

.PHONY: help doctor ci test-data verify guard ledger-check fingerprint fetch-translations reconcile rebuild ios-db scripture-diff compare-builds
help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n",$$1,$$2}'

doctor: ## check the local toolchain (PyMuPDF/numpy/scipy interpreter, git-lfs, DB, PDF)
	@echo "pipeline python: $(PIPELINE_PY)"; $(PIPELINE_PY) -c "import sys,fitz,numpy,scipy;print('  ok', sys.version.split()[0], '+ PyMuPDF/numpy/scipy')" || echo "  MISSING PyMuPDF/numpy/scipy — set PIPELINE_PY=..."
	@command -v git-lfs >/dev/null && echo "git-lfs: ok" || echo "  git-lfs missing"
	@test -f db/sggs.sqlite && head -c 16 db/sggs.sqlite | grep -q "SQLite format 3" && echo "db: real SQLite" || echo "  db/sggs.sqlite missing or an LFS pointer — run: git lfs pull"
	@test -f "$(PDF)" && echo "pdf: present" || echo "  source PDF not at $(PDF) (needed only for reconcile/rebuild)"

ci: verify guard ledger-check fingerprint test-data ## run the gates CI runs (no PDF needed)
	@echo "make ci: PASS"

test-data: ## data-integrity tests: install safety, fingerprints, editorial ledger, reproducibility
	python3 -m unittest discover -s pipeline/tests -v

verify: ## structural regroup invariants on the current DB
	python3 pipeline/verify_regroup.py --invariants db/sggs.sqlite

guard: ## pre-existing tables byte-identical to the committed baseline (+ bani registry invariants)
	python3 pipeline/timing/guard_scripture.py
	python3 pipeline/banis/guard_banis.py

ledger-check: ## editorial ledger: fix_text rules == register; scripture diffs vs main covered by new entries
	python3 pipeline/ledger_check.py --base $$(git merge-base HEAD origin/main)

fingerprint: ## db/sggs.sqlite content == audit/dataset-fingerprint.json (per table, FTS index, scripture)
	python3 pipeline/sggs_integrity.py db/sggs.sqlite --compare audit/dataset-fingerprint.json

fetch-translations: ## restore the private English translation sources (checksum-verified; needs access)
	bash scripts/data/fetch_translations.sh

reconcile: ## prove corpus == PDF char-for-char and write the attestation (needs PDF)
	$(PIPELINE_PY) pipeline/reconcile.py "$(PDF)" corpus/sggs.jsonl
	$(PIPELINE_PY) pipeline/golden_test.py "$(PDF)" >/dev/null && echo "golden PASS"
	$(PIPELINE_PY) scripts/release/write_attestation.py "$(PDF)"

rebuild: ## full deterministic rebuild from the PDF (needs PIPELINE_PY, the PDF and fetched translations)
	rm -rf corpus/by-raag/*
	PATH=$$(dirname $(PIPELINE_PY)):$$PATH bash pipeline/rebuild_all.sh "$(PDF)"

ios-db: ## derive both iOS database profiles into dist/ios/ (the app repo pins and verifies them)
	mkdir -p dist/ios
	python3 pipeline/build_ios_db.py --profile personal db/sggs.sqlite dist/ios/sggs-ios.sqlite
	python3 pipeline/build_ios_db.py --profile public db/sggs.sqlite dist/ios/sggs-ios-public.sqlite

scripture-diff: ## byte-level scripture diff vs a previous DB: make scripture-diff PRE=<old.sqlite>
	@test -n "$(PRE)" || { echo "usage: make scripture-diff PRE=<old.sqlite>"; exit 2; }
	python3 scripts/data/diff_scripture.py "$(PRE)" db/sggs.sqlite $(ARGS)

compare-builds: ## prove two builds identical table by table: make compare-builds A=<a.sqlite> B=<b.sqlite>
	@test -n "$(A)" -a -n "$(B)" || { echo "usage: make compare-builds A=<a.sqlite> B=<b.sqlite>"; exit 2; }
	python3 scripts/data/compare_builds.py "$(A)" "$(B)"
