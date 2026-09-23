# Changelog

## [Unreleased]

- Pinned dependency versions in `requirements.txt` for reproducibility.
- Added `pyproject.toml` — `pip install -e .` now works, with `quantum-rag-build` / `quantum-rag-query` console scripts.
- Added `examples/quickstart/` (original content) and an end-to-end smoke test that runs the real embedding/reranker models, not mocks.
- Added `CONTRIBUTING.md`.

## [0.1.0] — 2026-09-23

- Initial public release: hybrid TF-IDF + dense bi-encoder retrieval, cross-encoder reranking, and exact-match/regex search.
- CI with pytest + coverage (94%), Codecov, MIT license, `CITATION.cff`.
- Zenodo DOI: [10.5281/zenodo.22914813](https://doi.org/10.5281/zenodo.22914813).
- Documentation: operating-constraints framework, a context-engineering case study, and the Draft/Verification methodology (human-facing, kept separate from the constraints doc).
