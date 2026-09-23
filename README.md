<img src="assets/tao.svg" width="72" height="72" align="right" alt="quantum-rag logo">

# quantum-rag

[![CI](https://github.com/tatopenn-cell/quantum-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/tatopenn-cell/quantum-rag/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tatopenn-cell/quantum-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/tatopenn-cell/quantum-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

A small, local, hybrid RAG (retrieval-augmented generation) tool for grounding technical conversations in your own PDFs and notes — no server, no vector database, no cloud API calls except downloading the (open) embedding/reranker models once.

Built to stop an AI assistant from hallucinating citations: index your own real papers, then query them directly, or feed the retrieved passages back into whatever AI you're using as grounding context.

## How it works

1. Drop PDFs, Markdown, or text files into `papers/<collection>/`.
2. Run `build_index.py` to build a local index under `index/<collection>/`.
3. Run `query.py` to search it.

Each collection is its own independent vocabulary space — keep unrelated topics in separate collections so retrieval for one doesn't get diluted by the other.

Retrieval is hybrid and two-stage:

- **Stage 1**: pool candidates from TF-IDF cosine similarity (cheap, exact-term overlap) **union** a dense bi-encoder (`sentence-transformers/all-MiniLM-L6-v2`, catches paraphrases/synonyms TF-IDF misses — Karpukhin et al. 2020, *Dense Passage Retrieval for Open-Domain Question Answering*).
- **Stage 2**: rerank the pooled candidates with a pretrained cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) for the final top results.

There's also an **exact-match mode** (`--exact`) that does plain substring/regex search over the raw chunk text, no embeddings involved — useful when semantic ranking buries a short, specific phrase or value you already know roughly how to word.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# build all collections found under papers/
python build_index.py

# build just one
python build_index.py --collection my_topic

# semantic search (hybrid retrieval + cross-encoder rerank)
python query.py --collection my_topic "your question here"

# search every collection
python query.py --collection all "your question here"

# skip the cross-encoder, raw TF-IDF cosine only (faster, no model download)
python query.py --collection my_topic "your question" --no-rerank

# exact substring/regex search, for pinning down a specific known phrase
python query.py --collection my_topic --exact "the exact phrase you're hunting for"
python query.py --collection my_topic --exact "some \\d+ regex" --regex
```

## Layout

```
papers/<collection>/*.pdf|*.md|*.txt   # your source documents (not tracked in this repo)
index/<collection>/                    # built index (not tracked; regenerate with build_index.py)
    chunks.json
    vectorizer.pkl
    matrix.pkl
    embeddings.npy
```

No papers or built indexes ship with this repo — bring your own sources.

## Documentation

- **[The Reload Gap](https://claude.ai/artifact/QvAJ5UmaCsLcV6SEnrwSCZ)** — the case study and the operating-constraints framework, as a single page.
- [Operating constraints of an LLM agent working with this tool](docs/operational_constraints.md) — same content as source Markdown, the Context Engineering / LLMOps discipline behind how an agent's token budget, memory, and tool conventions actually activate across a session.
- [Case study: a context-reload trigger gap, found and fixed](docs/context_engineering_case_study.md) — same content as source Markdown, a concrete incident write-up grounded in the current Context Engineering literature.

**For human readers, not agent instructions:**
- [Draft and Verification: a two-phase development methodology](docs/draft_verification_methodology.md) — how a researcher, not an AI, structures work across a free-tier divergent drafting phase and a paid-tier convergent review phase. Deliberately kept separate from the constraints doc above: an AI reading both as one instruction set would receive contradictory guidance.
