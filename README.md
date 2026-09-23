# quantum-rag

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
