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
    chunks_path = index_dir / "chunks.json"
    if not chunks_path.exists():
        available = sorted(p.name for p in INDEX_DIR.iterdir() if p.is_dir()) if INDEX_DIR.is_dir() else []
        raise SystemExit(f"[{name}] no index at index/{name}/ -- run build_index.py first. Available: {available}")

    with open(chunks_path, encoding="utf-8") as f:
        chunks = json.load(f)
    with open(index_dir / "vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open(index_dir / "matrix.pkl", "rb") as f:
        matrix = pickle.load(f)
    emb_path = index_dir / "embeddings.npy"
    embeddings = np.load(emb_path) if emb_path.exists() else None

    if matrix.shape[0] != len(chunks) or (embeddings is not None and embeddings.shape[0] != len(chunks)):
        raise SystemExit(
            f"[{name}] index is inconsistent (chunks={len(chunks)}, matrix={matrix.shape[0]}, "
            f"embeddings={'n/a' if embeddings is None else embeddings.shape[0]}) "
            f"-- rebuild with: python build_index.py --collection {name}"
        )

    papers_dir = ROOT / "papers" / name
    if papers_dir.is_dir():
        newest_src = max((p.stat().st_mtime for p in papers_dir.iterdir()), default=0)
        if newest_src > chunks_path.stat().st_mtime:
            print(f"[{name}] warning: papers/{name}/ has files newer than the index -- "
                  f"rebuild with: python build_index.py --collection {name}")

    return chunks, vectorizer, matrix, embeddings


def search(query: str, collection: str, top: int, rerank: bool, pool: int, source: str = None):
    chunks, vectorizer, matrix, embeddings = load_collection(collection)
    query_vec = vectorizer.transform([query])
    cosine_scores = cosine_similarity(query_vec, matrix)[0]

    allowed = None
    if source:
        allowed = np.array([source.lower() in c["source"].lower() for c in chunks])
        if not allowed.any():
            print(f"[{collection}] no chunks with source containing {source!r}")
            return

    tfidf_order = cosine_scores.argsort()[::-1]
    if allowed is not None:
        # Drop disallowed indices entirely (not just deprioritize them) so a
        # --source filter never pads results out to `top` with non-matches.
        tfidf_order = tfidf_order[allowed[tfidf_order]]

    if rerank and embeddings is not None:
        query_emb = get_embedder().encode([query], normalize_embeddings=True)[0]
        dense_scores = embeddings @ query_emb
        dense_pool = dense_scores.argsort()[::-1]
        if allowed is not None:
            dense_pool = dense_pool[allowed[dense_pool]]
        dense_pool = dense_pool[:pool]
        candidate_idx = sorted(set(tfidf_order[:pool]) | set(dense_pool))
    elif rerank:
        candidate_idx = list(tfidf_order[:pool])
    else:
        candidate_idx = []

    if rerank and candidate_idx:
        # Full chunk text, not a hand-cut [:1024] char slice: the cross-encoder's
        # own tokenizer truncates on token boundaries (its real max_length), so a
        # manual char cut only risked cutting a formula or word for no benefit.
        pairs = [(query, chunks[i]["text"]) for i in candidate_idx]
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


def search_exact(pattern: str, collection: str, regex: bool, max_hits: int, context: int, source: str = None) -> int:
    """Substring/regex search over a collection's raw chunk text -- no
    embedding, no reranker, no model download. Semantic search ranks by
    topical similarity, which can bury a short, specific, load-bearing
    phrase (an exact clause, a fixed parameter value, a named condition)
    under chunks that are merely more topically central. Use this when you
    already know roughly what wording you're looking for and semantic
    search isn't surfacing it high enough. Returns the number of hits printed,
    so a caller can enforce a global --max-hits budget across collections."""
    chunks, _, _, _ = load_collection(collection)
    flags = 0 if regex else re.IGNORECASE
    compiled = re.compile(pattern if regex else re.escape(pattern), flags)
    hits = 0
    for i, chunk in enumerate(chunks):
        if source and source.lower() not in chunk["source"].lower():
            continue
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
    return hits


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
    parser.add_argument("--max-hits", type=int, default=10,
                         help="stop after this many exact matches -- a global budget across collections when --collection all, per-collection otherwise")
    parser.add_argument("--context", type=int, default=300, help="characters of context to show around each exact match")
    parser.add_argument("--source", help="restrict results to chunks whose source filename contains this (case-insensitive)")
    args = parser.parse_args()

    if args.regex and not args.exact:
        parser.error("--regex only makes sense together with --exact")

    if args.collection == "all":
        collections = sorted(p.name for p in INDEX_DIR.iterdir() if p.is_dir())
    else:
        collections = [args.collection]

    if args.exact:
        remaining = args.max_hits
        for name in collections:
            if remaining <= 0:
                print(f"[{name}] skipped -- global --max-hits {args.max_hits} budget already spent")
                continue
            remaining -= search_exact(args.query, name, args.regex, remaining, args.context, args.source)
    else:
        for name in collections:
            search(args.query, name, args.top, rerank=not args.no_rerank, pool=args.pool, source=args.source)


if __name__ == "__main__":
    main()
