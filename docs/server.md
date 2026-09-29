# Optional server

`query.py` opens a fresh process per call: every invocation reloads the embedding and cross-encoder models from disk, which is fine for one question but wasteful for many in a row. `server.py` wraps the same retrieval pipeline in a small FastAPI app that loads each model once and keeps it warm in memory, so repeated queries only pay the retrieval cost, not the model-load cost.

## Step 1. Install and start it

```bash
pip install -e ".[server]"
python server.py --port 8000
```

By default the server binds to `127.0.0.1` only (not reachable from other machines) and warms up the embedding/reranker models at startup, so the first real request is already fast.

## Step 2. Ask a question over HTTP

```bash
curl -s -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "zero noise extrapolation", "collection": "zne_mitigation", "top": 3}'
```

The response is the same ranked-chunk data `query.py` prints to the terminal, as JSON:

```json
{"results": [{"rank": 1, "collection": "zne_mitigation", "source": "...", "text": "...", "score": 5.59, "cosine": 0.22, "method": "rerank"}]}
```

`no_rerank: true` skips the cross-encoder and returns raw TF-IDF cosine ranking, same as `query.py --no-rerank`. `source` restricts results to chunks whose filename contains that string, same as `query.py --source`.

## Step 3. Exact/regex search over HTTP

```bash
curl -s -X POST http://127.0.0.1:8000/search_exact \
  -H "Content-Type: application/json" \
  -d '{"pattern": "Richardson extrapolation", "collection": "zne_mitigation", "max_hits": 5}'
```

Mirrors `query.py --exact`: a literal substring match by default, `"regex": true` to treat `pattern` as a regular expression.

## Step 4. Keep results fresh after rebuilding an index

The server caches a collection's `chunks.json`/`vectorizer.pkl`/`matrix.pkl`/`embeddings.npy` in memory, invalidated automatically by `chunks.json`'s mtime — running `build_index.py` again and then querying the same collection picks up the new index without a restart. To force it immediately (e.g. right after a build, before the next query would naturally trigger the mtime check):

```bash
curl -s -X POST http://127.0.0.1:8000/cache/invalidate -d '{"collection": "zne_mitigation"}'
```

Omit `"collection"` to clear every cached collection at once.

## Reference

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/health` | GET | no | liveness probe, no models involved |
| `/version` | GET | no | model ids and server flags |
| `/collections` | GET | yes | list available `index/<name>/` collections |
| `/search` | POST | yes | semantic / hybrid search |
| `/search_exact` | POST | yes | substring / regex search over raw chunk text |
| `/cache/invalidate` | POST | yes | drop the in-process collection cache |

## Details

**Authentication.** Set `QUANTUM_RAG_TOKEN` before starting the server to require `Authorization: Bearer <token>` on every endpoint except `/health` and `/version`. Binding to a non-loopback host without a token set refuses to start (`--allow-public` overrides this for a deliberately open, unauthenticated deployment — e.g. behind a reverse proxy that adds its own auth).

**Errors.** A missing collection returns `404` with the list of collections that do exist; an index left inconsistent by an interrupted build (`chunks.json`/`matrix.pkl`/`embeddings.npy` out of sync) returns `409` with a rebuild hint, rather than a raw stack trace.

**Why this file duplicates `query.py`'s retrieval logic instead of importing it**: it's intentional, so the server stays a single self-contained file that runs without the CLI module also being on the path. If the retrieval pipeline changes in `query.py`, mirror the change here.
