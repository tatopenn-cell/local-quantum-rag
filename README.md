<img src="assets/tao.svg" width="72" height="72" align="right" alt="local-quantum-rag logo">

# local-quantum-rag

[![CI](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tatopenn-cell/local-quantum-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/tatopenn-cell/local-quantum-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22914813.svg)](https://doi.org/10.5281/zenodo.22914813)

A small, local, hybrid RAG (retrieval-augmented generation) tool for grounding technical conversations in your own PDFs and notes — no server, no vector database, no cloud API calls except downloading the (open) embedding/reranker models once.

Built to stop an AI assistant from hallucinating citations: index your own real papers, then query them directly, or feed the retrieved passages back into whatever AI you're using as grounding context.

## Why "atomic," not just "quantum"

The name comes from the author's original domain, quantum computing — not a metaphor. But the design philosophy that grew around the code is genuinely atomic, in three specific, literal senses:

- **Isolated knowledge spaces.** Documents live in separate `papers/<collection>/` folders by design, never merged. One topic's vocabulary never dilutes another's retrieval.
- **Millimetric context control.** Instead of handing an AI a whole document, the pipeline slices it into small chunks and serves only the exact fragment a query needs — nothing more spent than necessary.
- **Indivisible execution steps.** The verification discipline this tool exists to support (see *Draft and Verification* below) forces one step at a time, in order, with no room for an AI to improvise past what was asked.

Cutting a workflow down to its smallest atomic units is exactly what removes the room an AI needs to invent something.

## Also: a documented method, not just a tool

The code here is small on purpose. What this repository actually holds, beyond `build_index.py` and `query.py`, is the working method built around them for doing AI-assisted scientific research without the AI inventing its sources:

- **How grounding is enforced** — the rule that every technical claim passes through this retrieval layer before being written down, and how that rule is kept active across an AI agent's sessions instead of quietly lapsing (see *The Reload Gap* below).
- **How the work itself is structured** — a separate methodology for splitting AI-assisted development into a free, divergent drafting phase and a paid, convergent verification phase, with the literature it happens to converge with.

Read together, the code and the docs are one artifact: a small RAG tool plus a record of the process discipline that makes AI-assisted research results trustworthy rather than merely plausible.

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
pip install -e .
```

Or without installing, just the pinned dependencies: `pip install -r requirements.txt`.

## Try it without your own papers first

`examples/quickstart/` ships two short, original (not copied from anywhere) documents specifically so you can try the whole pipeline immediately:

```bash
cp -r examples/quickstart papers/quickstart
python build_index.py --collection quickstart
python query.py --collection quickstart "why does semantic search sometimes miss a specific fact"
python query.py --collection quickstart --exact "the answer is 42 kelvin"
```

(`tests/test_quickstart_smoke.py` runs this exact flow, with the real models, as part of CI.)

## Usage

```bash
# build all collections found under papers/ (or use the installed console scripts below)
python build_index.py
local-quantum-rag-build   # same thing, after `pip install -e .`

# build just one
python build_index.py --collection my_topic

# semantic search (hybrid retrieval + cross-encoder rerank)
python query.py --collection my_topic "your question here"
local-quantum-rag-query --collection my_topic "your question here"   # same thing, installed

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

- [Operating constraints of an LLM agent working with this tool](docs/operational_constraints.md) — same content as source Markdown, the Context Engineering / LLMOps discipline behind how an agent's token budget, memory, and tool conventions actually activate across a session.
- [Case study: a context-reload trigger gap, found and fixed](docs/context_engineering_case_study.md) — same content as source Markdown, a concrete incident write-up grounded in the current Context Engineering literature.

**For human readers, not agent instructions:**
- [Draft and Verification: a two-phase development methodology](docs/draft_verification_methodology.md) — how a researcher, not an AI, structures work across a free-tier divergent drafting phase and a paid-tier convergent review phase. Deliberately kept separate from the constraints doc above: an AI reading both as one instruction set would receive contradictory guidance.
