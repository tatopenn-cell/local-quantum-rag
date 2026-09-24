# local-quantum-rag

[![CI](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/tatopenn-cell/local-quantum-rag/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tatopenn-cell/local-quantum-rag/branch/main/graph/badge.svg)](https://codecov.io/gh/tatopenn-cell/local-quantum-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22914813.svg)](https://doi.org/10.5281/zenodo.22914813)

local-quantum-rag is a small, local, hybrid RAG (retrieval-augmented generation) tool: it indexes your own PDFs and Markdown notes on disk, then answers a question by returning the passages that actually contain the answer — no server, no vector database, no cloud calls beyond downloading the (open) embedding/reranker models once.

Install it, then follow the four steps below with the two short example documents shipped in the repo.

```bash
git clone https://github.com/tatopenn-cell/local-quantum-rag
cd local-quantum-rag
pip install -e .
```

## Step 1. Index a folder of documents

Every document lives under `papers/<collection>/`. A collection is its own independent vocabulary space, so unrelated topics never dilute each other's retrieval. Start from the two example documents shipped in `examples/quickstart/`.

```bash
cp -r examples/quickstart papers/quickstart
python build_index.py --collection quickstart
```

```text
[quickstart] exact_match.md: 825 chars -> 1 chunks
[quickstart] retrieval.md: 927 chars -> 1 chunks
[quickstart] Indexed 2 chunks from 2 documents -> index/quickstart/
```

This reads every `.pdf`/`.md`/`.txt` file in the collection, splits it into chunks, fits a TF-IDF vectorizer over them, and computes a dense embedding per chunk (`sentence-transformers/all-MiniLM-L6-v2`). Everything is written to `index/quickstart/` — a vectorizer, a TF-IDF matrix, the chunk text, and the embedding matrix — so this step only needs to run again when the source documents change.

## Step 2. Ask a question in plain language

```bash
python query.py --collection quickstart "why does semantic search sometimes miss a specific fact"
```

```text
[quickstart] [1] exact_match.md  (rerank=4.139, cosine=0.344)
----------------------------------------------------------------------
# Why exact-match search exists alongside semantic search

Semantic search ranks passages by topical similarity, not by literal wording...
```

The query is scored two ways at once, then combined: TF-IDF cosine similarity (rewards exact word overlap) and dense-embedding similarity (catches paraphrases and synonyms the TF-IDF pass misses — Karpukhin et al. 2020, *Dense Passage Retrieval for Open-Domain Question Answering*). The union of both candidate pools is reranked by a cross-encoder, which reads the query and each passage together rather than comparing precomputed vectors, and that final ranking is what gets printed.

## Step 3. Pin down an exact fact the ranking buries

Step 2's top result talks *about* exact-match search, but the specific fact it exists to demonstrate — "the answer is 42 kelvin" — is a short, non-central sentence a purely topical ranking has no reason to place first. `--exact` skips retrieval entirely and searches the raw chunk text directly:

```bash
python query.py --collection quickstart --exact "the answer is 42 kelvin"
```

```text
[quickstart] [1] exact_match.md  (chunk 0)
----------------------------------------------------------------------
...The magic phrase for this example is
"the answer is 42 kelvin" -- a specific value that a purely semantic query would likely never
surface first, because nothing about the surrounding sentence is topically distinctive.
```

Literal mode is case-insensitive substring matching. Pass `--regex` to treat the pattern as a real, case-sensitive regular expression instead — useful for a fixed value with a known shape (`\d+\.\d+ mg/kg`) rather than an exact phrase.

## Step 4. Skip the reranker when speed matters more than precision

The cross-encoder in Step 2 is the slowest part of the pipeline, since it re-reads every candidate passage. `--no-rerank` returns the raw TF-IDF ranking instead:

```bash
python query.py --collection quickstart "why does semantic search sometimes miss a specific fact" --no-rerank
```

```text
[quickstart] [1] exact_match.md  (cosine=0.344, cosine=0.344)
[quickstart] [2] retrieval.md  (cosine=0.080, cosine=0.080)
```

No embedding model and no cross-encoder are loaded at all in this mode — only the TF-IDF vectorizer from Step 1 — so it starts faster and needs no model download on a machine that has never run this tool before.

## Details

**Why "atomic," not just "quantum."** The name comes from the author's original domain, quantum computing, not a metaphor — but the design is atomic in three literal senses: collections are isolated vocabulary spaces that never merge; each query is served the smallest chunk that answers it, not a whole document; and the tool exists specifically to support a verification method (below) that proceeds one step at a time, never beyond what was asked.

**The method, not just the tool.** [Draft and Verification](draft_verification_methodology.md) documents how a researcher structures AI-assisted work across a free-tier divergent drafting phase and a paid-tier convergent review phase — this tool is what the review phase uses to check a draft against the literature instead of trusting it from memory. [Operating constraints](operational_constraints.md) and the [Reload Gap case study](context_engineering_case_study.md) cover the agent-facing side: how the rule "ground every claim through this tool" is kept active across an AI agent's sessions instead of quietly lapsing.

**Console scripts**, after `pip install -e .`: `local-quantum-rag-build` and `local-quantum-rag-query`, equivalent to `python build_index.py` / `python query.py`.

**Layout:**

```
papers/<collection>/*.pdf|*.md|*.txt   # your source documents (not tracked in this repo)
index/<collection>/                    # built index (not tracked; regenerate with build_index.py)
    chunks.json
    vectorizer.pkl
    matrix.pkl
    embeddings.npy
```

No papers or built indexes ship with this repo beyond `examples/quickstart/` — bring your own sources.

**Citation.** See [CITATION.cff](https://github.com/tatopenn-cell/local-quantum-rag/blob/main/CITATION.cff) in the repository root. Archived on Zenodo, DOI [10.5281/zenodo.22914813](https://doi.org/10.5281/zenodo.22914813) (v0.1.0, minted under the project's prior name, quantum-rag).
