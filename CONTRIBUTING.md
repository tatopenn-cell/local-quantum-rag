# Contributing

## Setup

```bash
git clone https://github.com/tatopenn-cell/local-quantum-rag.git
cd local-quantum-rag
pip install -e .
pip install pytest pytest-cov
```

## Before opening a PR

- Run the test suite: `pytest --cov=. --cov-report=term-missing`. Coverage should not drop.
- If you add a function that talks to an external model (embedder, reranker), mock it in tests the way `tests/test_query.py` and `tests/test_build_index.py` already do — don't make CI download models for every unit test. The one exception is `tests/test_quickstart_smoke.py`, which deliberately exercises the real models end-to-end and is allowed to be slower.
- Keep `docs/operational_constraints.md` and `docs/draft_verification_methodology.md` separate: the first is written to be read by an AI assistant as operating rules, the second is written for a human only. Don't merge their content or cross-link them as if they were the same kind of document.

## Where things live

- `build_index.py` / `query.py` — the tool itself.
- `tests/` — unit tests (mocked models) plus one real end-to-end smoke test.
- `examples/quickstart/` — the small, original (not copied from anywhere) corpus the smoke test and any manual try-out use.
- `docs/` — see the README's Documentation section for what each file is for.

## Reporting a bug or requesting a feature

Open a GitHub issue. Include the exact command you ran and the full output — this tool has no server or hidden state, so a bug is almost always reproducible from the command alone.
