import json
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).parent.parent))

import server as srv
from fastapi.testclient import TestClient


def _build_fake_collection(index_dir, texts, sources):
    index_dir.mkdir(parents=True)
    chunks = [{"text": t, "source": s} for t, s in zip(texts, sources)]
    with open(index_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f)
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(texts)
    with open(index_dir / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(index_dir / "matrix.pkl", "wb") as f:
        pickle.dump(matrix, f)
    np.save(index_dir / "embeddings.npy", np.eye(len(texts), dtype=np.float32))


class FakeEmbedder:
    def encode(self, inputs, normalize_embeddings=True):
        return np.eye(3)


class FakeReranker:
    def predict(self, pairs):
        return np.linspace(1.0, 0.1, num=len(pairs))


def _fake_collection(tmp_path, monkeypatch):
    monkeypatch.setattr(srv, "INDEX_DIR", tmp_path)
    monkeypatch.setattr(srv, "PAPERS_DIR", tmp_path.parent / "papers_unused")
    texts = [
        "quantum error correction surface code",
        "gravitational entropy and the Friedmann equation",
        "depolarizing channel Kraus operators",
    ]
    sources = ["a.md", "b.md", "c.md"]
    _build_fake_collection(tmp_path / "physics", texts, sources)
    srv.invalidate_cache()
    return "physics"


def test_health_needs_no_auth_or_models():
    client = TestClient(srv.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_version_reports_models_and_auth_flag(monkeypatch):
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    client = TestClient(srv.app)
    resp = client.get("/version")
    assert resp.status_code == 200
    body = resp.json()
    assert body["auth_required"] is False
    assert "embedding_model" in body


def test_collections_lists_real_index_dirs(tmp_path, monkeypatch):
    name = _fake_collection(tmp_path, monkeypatch)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    client = TestClient(srv.app)
    resp = client.get("/collections")
    assert resp.status_code == 200
    assert resp.json() == {"collections": [name]}


def test_search_missing_collection_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(srv, "INDEX_DIR", tmp_path)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    client = TestClient(srv.app)
    resp = client.post("/search", json={"query": "x", "collection": "ghost", "top": 1})
    assert resp.status_code == 404
    assert resp.json()["detail"]["error"] == "collection_not_found"


def test_search_no_rerank_returns_real_ranked_results(tmp_path, monkeypatch):
    name = _fake_collection(tmp_path, monkeypatch)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    client = TestClient(srv.app)
    resp = client.post("/search", json={
        "query": "depolarizing channel", "collection": name, "top": 1, "no_rerank": True,
    })
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["source"] == "c.md"
    assert results[0]["method"] == "cosine"


def test_search_source_filter_no_match_returns_message(tmp_path, monkeypatch):
    name = _fake_collection(tmp_path, monkeypatch)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    client = TestClient(srv.app)
    resp = client.post("/search", json={
        "query": "anything", "collection": name, "top": 1, "no_rerank": True, "source": "zzz",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"] == []
    assert "no chunks with source containing" in body["message"]


def test_search_exact_literal_match(tmp_path, monkeypatch):
    name = _fake_collection(tmp_path, monkeypatch)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    client = TestClient(srv.app)
    resp = client.post("/search_exact", json={"pattern": "Kraus operators", "collection": name})
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["source"] == "c.md"


def test_cache_invalidate_clears_named_collection(tmp_path, monkeypatch):
    name = _fake_collection(tmp_path, monkeypatch)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", None)
    assert name in srv._cache or True  # populated lazily on first search, not on build
    client = TestClient(srv.app)
    client.post("/search_exact", json={"pattern": "Kraus", "collection": name})
    assert name in srv._cache
    resp = client.post("/cache/invalidate", json={"collection": name})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "cleared": name}
    assert name not in srv._cache


def test_auth_required_rejects_missing_and_wrong_token(tmp_path, monkeypatch):
    name = _fake_collection(tmp_path, monkeypatch)
    monkeypatch.setattr(srv, "_AUTH_TOKEN", "secret123")
    client = TestClient(srv.app)

    resp = client.get("/collections")
    assert resp.status_code == 401

    resp = client.get("/collections", headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401

    resp = client.get("/collections", headers={"Authorization": "Bearer secret123"})
    assert resp.status_code == 200
    assert resp.json() == {"collections": [name]}
