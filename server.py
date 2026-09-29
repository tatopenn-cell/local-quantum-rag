"""
FastAPI wrapper around the same retrieval logic as query.py.

Run:
    python server.py --port 8000
    python server.py --port 8000 --log-level DEBUG
    QUANTUM_RAG_TOKEN=secret python server.py --host 0.0.0.0

Endpoints:
    GET  /health                    liveness probe (no auth, no models)
    GET  /version                   model ids + flags
    GET  /collections               list available index/<name>/ collections
    POST /search                    semantic / hybrid search
    POST /search_exact              substring / regex search over raw chunk text
    POST /cache/invalidate          drop the in-process collection cache
                                    body optional: {"collection": "name"}

Environment:
    QUANTUM_RAG_TOKEN    if set, every endpoint except /health and /version
                         requires "Authorization: Bearer <token>"
    QUANTUM_RAG_WARMUP   "0"/"false" to skip model warmup at startup

NOTE ON DUPLICATION
    This file intentionally mirrors the retrieval pipeline of query.py
    (TF-IDF UNION dense -> cross-encoder rerank) instead of importing it,
    so it stays runnable as a single self-contained unit. If you change
    the pipeline in query.py, mirror the change here -- or extract a
    rag_core.py and have both import it.
"""

import argparse
import functools
import hmac
import json
import logging
import os
import pickle
import re
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

ROOT = Path(__file__).parent
INDEX_DIR = ROOT / "index"
PAPERS_DIR = ROOT / "papers"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_POOL = 20
SNIPPET_CHARS = 800

log = logging.getLogger("quantum-rag.server")

_AUTH_TOKEN = os.environ.get("QUANTUM_RAG_TOKEN") or None
_WARMUP = os.environ.get("QUANTUM_RAG_WARMUP", "1").lower() not in ("0", "false", "no")


# --------------------------------------------------------------------------
# Lazy, thread-safe model loading
# --------------------------------------------------------------------------

_embedder = None
_reranker = None
_model_lock = threading.Lock()


def _load_model(kind):
    try:
        if kind == "embedder":
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer(EMBEDDING_MODEL)
        from sentence_transformers import CrossEncoder
        return CrossEncoder(CROSS_ENCODER_MODEL)
    except ImportError as e:
        raise RuntimeError(
            "sentence-transformers is not installed; install it or call "
            "/search with no_rerank=true to use TF-IDF only"
        ) from e


def get_embedder():
    global _embedder
    if _embedder is None:
        with _model_lock:
            if _embedder is None:
                _embedder = _load_model("embedder")
    return _embedder


def get_reranker():
    global _reranker
    if _reranker is None:
        with _model_lock:
            if _reranker is None:
                _reranker = _load_model("reranker")
    return _reranker


# --------------------------------------------------------------------------
# Collection loading (cached, mtime-invalidated)
# --------------------------------------------------------------------------

_cache = {}                      # name -> (chunks_json_mtime, (chunks, vec, matrix, emb))
_cache_lock = threading.Lock()


class CollectionNotFound(Exception):
    def __init__(self, name, available):
        self.name = name
        self.available = available
        super().__init__(f"collection {name!r} not found; available: {available}")


class IndexInconsistent(Exception):
    def __init__(self, name, detail):
        self.name = name
        self.detail = detail
        super().__init__(f"index/{name}/ {detail}")


def invalidate_cache(collection=None):
    with _cache_lock:
        if collection is None:
            _cache.clear()
            log.info("cache: cleared all collections")
        else:
            _cache.pop(collection, None)
            log.info("cache: cleared %s", collection)


def _warn_if_stale(name, chunks_path):
    papers_dir = PAPERS_DIR / name
    if not papers_dir.is_dir():
        return
    try:
        newest = max((p.stat().st_mtime for p in papers_dir.iterdir()), default=0)
        idx_mtime = chunks_path.stat().st_mtime
    except OSError:
        return
    if newest > idx_mtime:
        log.warning(
            "[%s] papers/%s/ has files newer than the index -- rebuild with: "
            "python build_index.py --collection %s",
            name, name, name,
        )


def load_collection(name):
    index_dir = INDEX_DIR / name
    chunks_path = index_dir / "chunks.json"
    if not chunks_path.exists():
        available = (
            sorted(p.name for p in INDEX_DIR.iterdir() if p.is_dir())
            if INDEX_DIR.is_dir() else []
        )
        raise CollectionNotFound(name, available)

    try:
        mtime = chunks_path.stat().st_mtime
    except OSError as e:
        raise CollectionNotFound(name, []) from e

    with _cache_lock:
        cached = _cache.get(name)
        if cached is not None and cached[0] == mtime:
            return cached[1]

        try:
            with open(chunks_path, encoding="utf-8") as f:
                chunks = json.load(f)
            with open(index_dir / "vectorizer.pkl", "rb") as f:
                vectorizer = pickle.load(f)
            with open(index_dir / "matrix.pkl", "rb") as f:
                matrix = pickle.load(f)
            emb_path = index_dir / "embeddings.npy"
            embeddings = np.load(emb_path) if emb_path.exists() else None
        except (OSError, pickle.UnpicklingError, json.JSONDecodeError, ValueError) as e:
            raise IndexInconsistent(name, f"unreadable ({type(e).__name__}: {e})") from e

        emb_rows = None if embeddings is None else embeddings.shape[0]
        if matrix.shape[0] != len(chunks) or (
            embeddings is not None and emb_rows != len(chunks)
        ):
            raise IndexInconsistent(
                name,
                f"is inconsistent (chunks={len(chunks)}, matrix={matrix.shape[0]}, "
                f"embeddings={'n/a' if emb_rows is None else emb_rows})",
            )

        _warn_if_stale(name, chunks_path)
        _cache[name] = (mtime, (chunks, vectorizer, matrix, embeddings))
        return _cache[name][1]


# --------------------------------------------------------------------------
# Retrieval (same pipeline as query.py)
# --------------------------------------------------------------------------

def search(query, collection, top=3, rerank=True, pool=DEFAULT_POOL, source=None):
    # A rerank pool smaller than `top` would silently return fewer than `top`
    # results -- the cross-encoder can only reorder what stage 1 handed it.
    pool = max(pool, top)

    chunks, vectorizer, matrix, embeddings = load_collection(collection)
    cosine_scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]

    allowed = None
    if source:
        allowed = np.array([source.lower() in c["source"].lower() for c in chunks])
        if not allowed.any():
            return []   # caller reports "no source match"

    tfidf_order = cosine_scores.argsort()[::-1]
    if allowed is not None:
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
        pairs = [(query, chunks[i]["text"]) for i in candidate_idx]
        rerank_scores = get_reranker().predict(pairs)
        order = rerank_scores.argsort()[::-1][:top]
        top_idx = [candidate_idx[j] for j in order]
        shown = {candidate_idx[j]: float(rerank_scores[j]) for j in order}
        label = "rerank"
    else:
        top_idx = list(tfidf_order[:top])
        shown = {i: float(cosine_scores[i]) for i in top_idx}
        label = "cosine"

    return [
        {
            "rank": rank,
            "collection": collection,
            "source": chunks[i]["source"],
            "text": chunks[i]["text"],
            "score": shown[i],
            "cosine": float(cosine_scores[i]),
            "method": label,
        }
        for rank, i in enumerate(top_idx, 1)
    ]


def search_exact(pattern, collection, regex=False, max_hits=10, context=300, source=None):
    chunks, _, _, _ = load_collection(collection)
    flags = 0 if regex else re.IGNORECASE
    compiled = re.compile(pattern if regex else re.escape(pattern), flags)

    hits = []
    for i, chunk in enumerate(chunks):
        if source and source.lower() not in chunk["source"].lower():
            continue
        text = chunk["text"]
        m = compiled.search(text)
        if not m:
            continue
        lo = max(0, m.start() - context)
        hi = min(len(text), m.end() + context)
        hits.append({
            "rank": len(hits) + 1,
            "collection": collection,
            "source": chunk["source"],
            "chunk_index": i,
            "match_start": m.start(),
            "match_end": m.end(),
            "snippet": text[lo:hi],
            "truncated_left": lo > 0,
            "truncated_right": hi < len(text),
        })
        if len(hits) >= max_hits:
            break
    return hits


# --------------------------------------------------------------------------
# FastAPI
# --------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app):
    if _WARMUP:
        log.info("warming up models...")
        try:
            get_embedder()
            get_reranker()
            log.info("models ready")
        except RuntimeError as e:
            log.warning("model warmup failed: %s", e)
            log.warning("server will run in TF-IDF-only mode; pass no_rerank=true")
    else:
        log.info("warmup disabled (QUANTUM_RAG_WARMUP=0)")

    if INDEX_DIR.is_dir():
        for p in sorted(INDEX_DIR.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                cp = p / "chunks.json"
                if cp.exists():
                    _warn_if_stale(p.name, cp)

    yield


app = FastAPI(
    title="Quantum-RAG API Server",
    description="Local server for indexes built by build_index.py",
    version="1.2",
    lifespan=lifespan,
)
app.add_middleware(GZipMiddleware, minimum_size=1024)


# --- auth -----------------------------------------------------------------

def require_auth(authorization: Optional[str] = Header(None)):
    if _AUTH_TOKEN is None:
        return
    expected = f"Bearer {_AUTH_TOKEN}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(401, {"error": "unauthorized"})


# --- request models -------------------------------------------------------

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    collection: str = Field(..., min_length=1, max_length=128)
    top: int = Field(3, ge=1, le=100)
    pool: int = Field(DEFAULT_POOL, ge=1, le=500)
    no_rerank: bool = False
    source: Optional[str] = Field(None, max_length=256)


class ExactRequest(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=1000)
    collection: str = Field(..., min_length=1, max_length=128)
    regex: bool = False
    max_hits: int = Field(10, ge=1, le=500)
    context: int = Field(300, ge=0, le=5000)
    source: Optional[str] = Field(None, max_length=256)


class InvalidateRequest(BaseModel):
    collection: Optional[str] = Field(None, max_length=128)


# --- error translation ----------------------------------------------------

def _translate(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except CollectionNotFound as e:
            raise HTTPException(404, {
                "error": "collection_not_found",
                "collection": e.name,
                "available": e.available,
            })
        except IndexInconsistent as e:
            raise HTTPException(409, {
                "error": "index_inconsistent",
                "detail": e.detail,
                "hint": f"rebuild with: python build_index.py --collection {e.name}",
            })
        except RuntimeError as e:
            raise HTTPException(503, {"error": "model_unavailable", "detail": str(e)})
        except FileNotFoundError as e:
            raise HTTPException(404, {"error": "not_found", "detail": str(e)})
        except ValueError as e:
            raise HTTPException(400, {"error": "bad_request", "detail": str(e)})
    return wrapper


# --- middleware -----------------------------------------------------------

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    dt_ms = (time.perf_counter() - t0) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{dt_ms:.1f}"
    if request.url.path not in ("/health", "/version"):
        log.info("%s %s -> %s (%.1f ms)",
                 request.method, request.url.path, response.status_code, dt_ms)
    return response


# --- endpoints ------------------------------------------------------------

@app.get("/health")
def health():
    return {"ok": True}


@app.get("/version")
def version():
    return {
        "embedding_model": EMBEDDING_MODEL,
        "cross_encoder_model": CROSS_ENCODER_MODEL,
        "default_pool": DEFAULT_POOL,
        "warmup": _WARMUP,
        "auth_required": _AUTH_TOKEN is not None,
    }


@app.get("/collections", dependencies=[Depends(require_auth)])
def list_collections():
    if not INDEX_DIR.is_dir():
        return {"collections": []}
    names = sorted(
        p.name for p in INDEX_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )
    return {"collections": names}


@app.post("/search", dependencies=[Depends(require_auth)])
@_translate
def search_api(req: SearchRequest):
    results = search(
        req.query, req.collection, req.top,
        rerank=not req.no_rerank, pool=req.pool, source=req.source,
    )
    if req.source and not results:
        return {"results": [], "message": f"no chunks with source containing {req.source!r}"}
    for r in results:
        r["snippet"] = r["text"][:SNIPPET_CHARS]
    return {"results": results}


@app.post("/search_exact", dependencies=[Depends(require_auth)])
@_translate
def search_exact_api(req: ExactRequest):
    hits = search_exact(
        req.pattern, req.collection, req.regex,
        req.max_hits, req.context, req.source,
    )
    return {"results": hits}


@app.post("/cache/invalidate", dependencies=[Depends(require_auth)])
def invalidate(req: Optional[InvalidateRequest] = None):
    collection = req.collection if req else None
    invalidate_cache(collection)
    return {"ok": True, "cleared": collection or "all"}


# --- CLI ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="porta locale del server")
    parser.add_argument("--host", default="127.0.0.1", help="host di bind (default: 127.0.0.1)")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--allow-public", action="store_true",
                        help="consenti il bind su un host non-loopback senza QUANTUM_RAG_TOKEN")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    loopback = args.host in ("127.0.0.1", "localhost", "::1")
    if not loopback and _AUTH_TOKEN is None and not args.allow_public:
        parser.error(
            f"refusing to bind to {args.host} without authentication; "
            "set QUANTUM_RAG_TOKEN or pass --allow-public"
        )

    log.info("auth: %s", "bearer token required" if _AUTH_TOKEN else "disabled")
    log.info("warmup: %s", "enabled" if _WARMUP else "disabled")
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())


if __name__ == "__main__":
    main()