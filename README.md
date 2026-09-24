<img src="assets/tao.svg" width="72" height="72" align="right" alt="local-quantum-rag logo">

# local-quantum-rag

[![CI](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tatopenn-cell/local-quantum-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/tatopenn-cell/local-quantum-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22914813.svg)](https://doi.org/10.5281/zenodo.22914813)
[![Docs](https://img.shields.io/badge/docs-tatopenn--cell.github.io-blue)](https://tatopenn-cell.github.io/local-quantum-rag/)

A small, local, hybrid RAG tool for grounding technical conversations in your own PDFs and notes, so an AI assistant cites what a document actually says instead of what it remembers. No server, no vector database — see the **[full documentation](https://tatopenn-cell.github.io/local-quantum-rag/)** for how it works, the design philosophy, and the two-phase verification method it exists to support.

## Install

```bash
pip install -e .
```

See the [docs](https://tatopenn-cell.github.io/local-quantum-rag/) for the quickstart, the full CLI reference, and the exact-match mode.

## Documentation

- **[Full guide and API overview](https://tatopenn-cell.github.io/local-quantum-rag/)** — install, quickstart, hybrid retrieval design, `--exact` mode.
- [Draft and Verification: a two-phase development methodology](docs/draft_verification_methodology.md) — for human readers, not agent instructions.
- [Operating constraints of an LLM agent working with this tool](docs/operational_constraints.md).
- [Case study: a context-reload trigger gap, found and fixed](docs/context_engineering_case_study.md).
