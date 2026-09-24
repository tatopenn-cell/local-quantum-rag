# local-quantum-rag

**Local, hybrid RAG · TF-IDF + dense bi-encoder + cross-encoder rerank · exact-match fallback**

[![CI](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tatopenn-cell/local-quantum-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/tatopenn-cell/local-quantum-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22914813.svg)](https://doi.org/10.5281/zenodo.22914813)

A small, local, hybrid RAG (retrieval-augmented generation) tool for grounding technical conversations in your own PDFs and notes — no server, no vector database, no cloud API calls except downloading the (open) embedding/reranker models once.

Built to stop an AI assistant from hallucinating citations: index your own real papers, then query them directly, or feed the retrieved passages back into whatever AI you're using as grounding context.

Using this in academic work? See [CITATION.cff](https://github.com/tatopenn-cell/local-quantum-rag/blob/main/CITATION.cff) in the repository root. Archived on Zenodo — DOI [10.5281/zenodo.22914813](https://doi.org/10.5281/zenodo.22914813) (v0.1.0, minted under the project's prior name).

## Hello world: build and search a collection

```bash
git clone https://github.com/tatopenn-cell/local-quantum-rag
cd local-quantum-rag
pip install -e .

cp -r examples/quickstart papers/quickstart
python build_index.py --collection quickstart
python query.py --collection quickstart "why does semantic search sometimes miss a specific fact"
```

That builds a local TF-IDF + dense-embedding index under `index/quickstart/` and searches it with the full hybrid pipeline. `examples/quickstart/` ships two short, original documents specifically so this runs immediately, with no papers of your own.

## What's in here

- **`build_index.py`** — walks `papers/<collection>/`, chunks PDFs/Markdown/text, fits a TF-IDF vectorizer, and computes dense bi-encoder embeddings (`sentence-transformers/all-MiniLM-L6-v2`) per chunk.
- **`query.py`** — two-stage hybrid retrieval: TF-IDF cosine ∪ dense similarity pool, reranked by a cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`); plus an `--exact` mode for plain substring/regex search over raw chunk text when semantic ranking buries a specific known phrase or value.
- **[Draft and Verification](draft_verification_methodology.md)** — a documented two-phase method for structuring AI-assisted research: a free, divergent drafting phase and a paid, convergent review phase, run by two different AIs, one point at a time.
- **[Operational constraints](operational_constraints.md)** — the rules an LLM agent follows when actually using this tool for grounding, and why they have to be re-loaded every session rather than assumed to persist.
- **[Case study: the Reload Gap](context_engineering_case_study.md)** — a concrete incident where that assumption failed, and the fix.

## Why "atomic," not just "quantum"

The name comes from the author's original domain, quantum computing — not a metaphor. The design philosophy is atomic in three literal senses: documents live in isolated `papers/<collection>/` vocabulary spaces that never merge; the pipeline slices text into small chunks and serves only the exact fragment a query needs; and the verification discipline the tool supports forces one step at a time, in order, with no room for an AI to improvise past what was asked.
