# Changelog

## [0.2.0] — 2026-09-26

- Fixed multi-column PDF extraction (`page.get_text(sort=True)`) — text from two-column papers no longer comes back with left/right columns interlaced.
- Chunking now respects sentence/paragraph boundaries instead of cutting at a fixed character offset, and overlap carries whole sentences.
- `build_index.py` writes each collection's index atomically (temp dir + rename), so a crash mid-build can no longer leave `index/<name>/` with some files rebuilt and others stale.
- `query.py` now validates that a collection's index exists and that `chunks.json`/`matrix.pkl`/`embeddings.npy` are mutually consistent, and warns when `papers/<name>/` has files newer than the index.
- Added `--source` to restrict a query to chunks from a specific document.
- `--regex` without `--exact` is now a hard argument error instead of a silent no-op.
- `--max-hits` is a global budget across collections when `--collection all` (was silently per-collection).
- Cross-encoder reranking no longer hand-truncates chunk text to 1024 characters before tokenization; the model's own tokenizer truncates on token boundaries.
- Ligature/whitespace normalization now applies to `.md`/`.txt` sources too, not just PDFs.
- Pinned dependency versions in `requirements.txt` for reproducibility.
- Added `pyproject.toml` — `pip install -e .` now works, with `quantum-rag-build` / `quantum-rag-query` console scripts.
- Added `examples/quickstart/` (original content) and an end-to-end smoke test that runs the real embedding/reranker models, not mocks.
- Added `CONTRIBUTING.md`.

## [0.1.0] — 2026-09-23

- Initial public release: hybrid TF-IDF + dense bi-encoder retrieval, cross-encoder reranking, and exact-match/regex search.
- CI with pytest + coverage (94%), Codecov, MIT license, `CITATION.cff`.
- Zenodo DOI: [10.5281/zenodo.22914813](https://doi.org/10.5281/zenodo.22914813).
- Documentation: operating-constraints framework, a context-engineering case study, and the Draft/Verification methodology (human-facing, kept separate from the constraints doc).
