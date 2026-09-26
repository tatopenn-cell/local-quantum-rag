import json
import pickle
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).parent.parent))

import query as q


class FakeEmbedder:
    def encode(self, inputs, normalize_embeddings=True):
        return np.eye(3)


class FakeReranker:
    def predict(self, pairs):
        return np.linspace(1.0, 0.1, num=len(pairs))


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


@pytest.fixture
def fake_collection(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "INDEX_DIR", tmp_path)
    texts = [
        "quantum error correction surface code",
        "gravitational entropy and the Friedmann equation",
        "depolarizing channel Kraus operators",
    ]
    sources = ["a.md", "b.md", "c.md"]
    _build_fake_collection(tmp_path / "physics", texts, sources)
    return "physics"


def test_load_collection_reads_chunks_vectorizer_matrix_embeddings(fake_collection):
    chunks, vectorizer, matrix, embeddings = q.load_collection(fake_collection)
    assert [c["source"] for c in chunks] == ["a.md", "b.md", "c.md"]
    assert matrix.shape[0] == 3
    assert embeddings.shape == (3, 3)


def test_search_no_rerank_uses_tfidf_cosine_only(fake_collection, capsys):
    q.search("depolarizing channel", fake_collection, top=1, rerank=False, pool=q.DEFAULT_POOL)
    out = capsys.readouterr().out
    assert "c.md" in out
    assert "cosine=" in out
    assert "rerank=" not in out


def test_search_with_rerank_uses_embedder_and_reranker(fake_collection, capsys):
    with patch.object(q, "get_reranker", return_value=FakeReranker()), \
         patch.object(q, "get_embedder", return_value=FakeEmbedder()):
        q.search("quantum error correction", fake_collection, top=1, rerank=True, pool=3)
    out = capsys.readouterr().out
    assert "rerank=" in out


def test_search_exact_literal_match(fake_collection, capsys):
    q.search_exact("Kraus operators", fake_collection, regex=False, max_hits=10, context=20)
    out = capsys.readouterr().out
    assert "c.md" in out
    assert "[1]" in out


def test_search_exact_no_match_reports_zero_hits(fake_collection, capsys):
    q.search_exact("nonexistent phrase xyz", fake_collection, regex=False, max_hits=10, context=20)
    out = capsys.readouterr().out
    assert "no exact match" in out


def test_search_exact_regex_mode(fake_collection, capsys):
    q.search_exact(r"\bcode\b", fake_collection, regex=True, max_hits=10, context=10)
    out = capsys.readouterr().out
    assert "a.md" in out


def test_search_exact_respects_max_hits(fake_collection, capsys):
    q.search_exact("t", fake_collection, regex=False, max_hits=1, context=5)
    out = capsys.readouterr().out
    assert "stopped at --max-hits 1" in out


def test_main_exact_flag_dispatches_to_search_exact(fake_collection, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["query.py", "--collection", fake_collection, "--exact", "Kraus"])
    calls = []

    def fake_search_exact(*a):
        calls.append(a)
        return 0

    monkeypatch.setattr(q, "search_exact", fake_search_exact)
    q.main()
    assert calls == [("Kraus", fake_collection, False, 10, 300, None)]


def test_main_default_dispatches_to_search(fake_collection, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["query.py", "--collection", fake_collection, "some query"])
    calls = []
    monkeypatch.setattr(q, "search", lambda *a, **kw: calls.append((a, kw)))
    q.main()
    assert calls == [(("some query", fake_collection, 3), {"rerank": True, "pool": q.DEFAULT_POOL, "source": None})]


def test_main_collection_all_iterates_every_index_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "INDEX_DIR", tmp_path)
    (tmp_path / "alpha").mkdir()
    (tmp_path / "beta").mkdir()
    monkeypatch.setattr(sys, "argv", ["query.py", "--collection", "all", "some query"])
    calls = []
    monkeypatch.setattr(q, "search", lambda *a, **kw: calls.append(a[1]))
    q.main()
    assert calls == ["alpha", "beta"]
