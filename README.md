<img src="assets/tao.svg" width="72" height="72" align="right" alt="local-quantum-rag logo">

# local-quantum-rag

[![CI](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tatopenn-cell/local-quantum-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/tatopenn-cell/local-quantum-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22914813.svg)](https://doi.org/10.5281/zenodo.22914813)
[![Docs](https://img.shields.io/badge/docs-tatopenn--cell.github.io-blue)](https://tatopenn-cell.github.io/local-quantum-rag/)

A small, local, hybrid RAG tool for grounding technical conversations in your own PDFs and notes, so an AI assistant cites what a document actually says instead of what it remembers. A CLI (`query.py`) covers everyday use; an optional local FastAPI server (`server.py`) keeps the embedding/reranker models warm across repeated queries. See the **[full documentation](https://tatopenn-cell.github.io/local-quantum-rag/)** for how it works, the design philosophy, and the two-phase verification method it exists to support.

## Install

```bash
pip install -e .
```

See the [docs](https://tatopenn-cell.github.io/local-quantum-rag/) for the quickstart, the full CLI reference, and the exact-match mode.

## Optional server

```bash
pip install -e ".[server]"
python server.py --port 8000
```

Exposes `/search`, `/search_exact`, `/collections` over HTTP with an in-process, mtime-invalidated cache, so repeated queries skip reloading the embedding/reranker models. See [the server docs](https://tatopenn-cell.github.io/local-quantum-rag/server/) for endpoints, auth (`QUANTUM_RAG_TOKEN`), and deployment notes.

## Documentation

- **[Full guide and API overview](https://tatopenn-cell.github.io/local-quantum-rag/)** — install, quickstart, hybrid retrieval design, `--exact` mode.
- **[Four-phase methodology](docs/four_phase_methodology.md)** — start here if you want the shape of the whole architecture before the details.
- [Optional server](https://tatopenn-cell.github.io/local-quantum-rag/server/) — HTTP endpoints, auth, caching.
- [Draft and Verification: a two-phase development methodology](docs/draft_verification_methodology.md) — for human readers, not agent instructions.
- [Verification layers: Discovery and Evolving Software repositories](docs/verification_layers.md).
- [Operating constraints of an LLM agent working with this tool](docs/operational_constraints.md).
- [Case study: a context-reload trigger gap, found and fixed](docs/context_engineering_case_study.md).
