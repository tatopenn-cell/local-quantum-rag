"""End-to-end smoke test: real build_index.py + query.py over examples/quickstart/,
with real embedding/reranker models (no mocks) -- the one test that exercises the
whole pipeline instead of individual functions in isolation."""

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import build_index as bi
import query as q

ROOT = Path(__file__).parent.parent
EXAMPLE_DIR = ROOT / "examples" / "quickstart"


@pytest.fixture
def built_example_index(tmp_path, monkeypatch):
    monkeypatch.setattr(bi, "PAPERS_DIR", tmp_path / "papers")
    monkeypatch.setattr(bi, "INDEX_DIR", tmp_path / "index")
    monkeypatch.setattr(q, "INDEX_DIR", tmp_path / "index")
    collection_dir = tmp_path / "papers" / "quickstart"
    shutil.copytree(EXAMPLE_DIR, collection_dir)
    bi.build_collection("quickstart")
    return "quickstart"


def test_hybrid_search_finds_the_relevant_doc(built_example_index, capsys):
    q.search("why does semantic search sometimes miss a specific fact",
             built_example_index, top=1, rerank=True, pool=q.DEFAULT_POOL)
    out = capsys.readouterr().out
    assert "exact_match.md" in out


def test_exact_search_finds_the_magic_phrase(built_example_index, capsys):
    q.search_exact("the answer is 42 kelvin", built_example_index,
                    regex=False, max_hits=10, context=20)
    out = capsys.readouterr().out
    assert "exact_match.md" in out
    assert "42 kelvin" in out
