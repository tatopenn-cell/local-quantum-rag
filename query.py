"""
Query indexes built by build_index.py.

Usage:
    python query.py "quantum relative entropy density matrix"
    python query.py --collection my_topic "your question" --top 5
    python query.py --collection all "error mitigation"
    python query.py --collection my_topic --exact "an exact phrase"
"""

import argparse
import json
import pickle
import re
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).parent
INDEX_DIR = ROOT / "index"
DEFAULT_COLLECTION = "default"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_POOL = 20

_reranker = None
_embedder = None


def get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(CROSS_ENCODER_MODEL)
    return _reranker


def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def load_collection(name: str):
    index_dir = INDEX_DIR / name
    with open(index_dir / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    with open(index_dir / "vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open(index_dir / "matrix.pkl", "rb") as f:
        matrix = pickle.load(f)
    emb_path = index_dir / "embeddings.npy"
    embeddings = np.load(emb_path) if emb_path.exists() else None
    return chunks, vectorizer, matrix, embeddings


def search(query: str, collection: str, top: int, rerank: bool, pool: int):
    chunks, vectorizer, matrix, embeddings = load_collection(collection)
    query_vec = vectorizer.transform([query])
    cosine_scores = cosine_similarity(query_vec, matrix)[0]
    tfidf_order = cosine_scores.argsort()[::-1]

    if rerank and embeddings is not None:
        query_emb = get_embedder().encode([query], normalize_embeddings=True)[0]
        dense_scores = embeddings @ query_emb
        dense_pool = dense_scores.argsort()[::-1][:pool]
        candidate_idx = sorted(set(tfidf_order[:pool]) | set(dense_pool))
    elif rerank:
        candidate_idx = list(tfidf_order[:pool])
    else:
        candidate_idx = []

    if rerank and candidate_idx:
        pairs = [(query, chunks[i]["text"][:1024]) for i in candidate_idx]
        rerank_scores = get_reranker().predict(pairs)
        order = rerank_scores.argsort()[::-1][:top]
        top_idx = [candidate_idx[j] for j in order]
        shown_scores = {candidate_idx[j]: rerank_scores[j] for j in order}
        label = "rerank"
    else:
        top_idx = list(tfidf_order[:top])
        shown_scores = {i: cosine_scores[i] for i in top_idx}
        label = "cosine"

    for rank, i in enumerate(top_idx, 1):
        # PDF text extraction often carries ligatures (fi, ff, ...) that
        # crash on Windows' default cp1252 console encoding -- normalize
        # them away here so this always prints, regardless of terminal.
        snippet = chunks[i]["text"][:800]
        snippet = snippet.encode("ascii", errors="replace").decode("ascii")
        print(f"\n[{collection}] [{rank}] {chunks[i]['source']}  ({label}={shown_scores[i]:.3f}, cosine={cosine_scores[i]:.3f})")
        print("-" * 70)
        print(snippet)


def search_exact(pattern: str, collection: str, regex: bool, max_hits: int, context: int):
    """Substring/regex search over a collection's raw chunk text -- no
    embedding, no reranker, no model download. Semantic search ranks by
    topical similarity, which can bury a short, specific, load-bearing
    phrase (an exact clause, a fixed parameter value, a named condition)
    under chunks that are merely more topically central. Use this when you
    already know roughly what wording you're looking for and semantic
    search isn't surfacing it high enough."""
    chunks, _, _, _ = load_collection(collection)
    flags = 0 if regex else re.IGNORECASE
    compiled = re.compile(pattern if regex else re.escape(pattern), flags)
    hits = 0
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        m = compiled.search(text)
        if not m:
            continue
        hits += 1
        lo = max(0, m.start() - context)
        hi = min(len(text), m.end() + context)
        snippet = text[lo:hi].encode("ascii", errors="replace").decode("ascii")
        print(f"\n[{collection}] [{hits}] {chunk['source']}  (chunk {i})")
        print("-" * 70)
        print(("..." if lo > 0 else "") + snippet + ("..." if hi < len(text) else ""))
        if hits >= max_hits:
            print(f"\n[{collection}] stopped at --max-hits {max_hits}, more may exist")
            break
    if hits == 0:
        print(f"[{collection}] no exact match for {pattern!r}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="natural-language question or keywords (or an exact phrase with --exact)")
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help=f"collection to search (subfolder under index/), or 'all'; default: {DEFAULT_COLLECTION}",
    )
    parser.add_argument("--top", type=int, default=3, help="number of chunks to return per collection")
    parser.add_argument("--no-rerank", action="store_true", help="skip cross-encoder rerank, use raw TF-IDF cosine")
    parser.add_argument("--pool", type=int, default=DEFAULT_POOL, help="stage-1 candidate pool size for reranking")
    parser.add_argument(
        "--exact", action="store_true",
        help="substring/regex search over raw chunk text instead of semantic search -- for finding a specific known phrase or value semantic ranking buries",
    )
    parser.add_argument("--regex", action="store_true", help="treat the query as a regex (only with --exact); default is a literal substring, case-insensitive")
    parser.add_argument("--max-hits", type=int, default=10, help="stop after this many exact matches per collection")
    parser.add_argument("--context", type=int, default=300, help="characters of context to show around each exact match")
    args = parser.parse_args()

    if args.collection == "all":
        collections = sorted(p.name for p in INDEX_DIR.iterdir() if p.is_dir())
    else:
        collections = [args.collection]

    for name in collections:
        if args.exact:
            search_exact(args.query, name, args.regex, args.max_hits, args.context)
        else:
            search(args.query, name, args.top, rerank=not args.no_rerank, pool=args.pool)


if __name__ == "__main__":
    main()
