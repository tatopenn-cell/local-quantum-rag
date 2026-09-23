import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

import build_index as bi
from build_index import chunk_text, extract_text, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS


class FakeEmbedder:
    def encode(self, texts, normalize_embeddings=True, show_progress_bar=False):
        return np.zeros((len(texts), 4))


def test_chunk_text_short_text_single_chunk():
    chunks = chunk_text("hello world", "doc.md")
    assert len(chunks) == 1
    assert chunks[0]["text"] == "hello world"
    assert chunks[0]["source"] == "doc.md"


def test_chunk_text_empty_text_no_chunks():
    assert chunk_text("", "doc.md") == []


def test_chunk_text_long_text_overlaps():
    text = "a" * (CHUNK_SIZE_CHARS * 2 + 100)
    chunks = chunk_text(text, "doc.md")
    assert len(chunks) > 1
    # consecutive chunks overlap by CHUNK_OVERLAP_CHARS characters
    first_tail = chunks[0]["text"][-CHUNK_OVERLAP_CHARS:]
    second_head = chunks[1]["text"][:CHUNK_OVERLAP_CHARS]
    assert first_tail == second_head


def test_chunk_text_covers_whole_input():
    text = "x" * (CHUNK_SIZE_CHARS + 50)
    chunks = chunk_text(text, "doc.md")
    assert chunks[-1]["text"][-1] == "x"
    total_unique_span = chunks[0]["text"] + chunks[-1]["text"][CHUNK_OVERLAP_CHARS:]
    assert len(total_unique_span) == len(text)


def test_extract_text_markdown(tmp_path):
    p = tmp_path / "note.md"
    p.write_text("# Title\n\nSome content.", encoding="utf-8")
    assert extract_text(p) == "# Title\n\nSome content."


def test_extract_text_txt_strips_whitespace(tmp_path):
    p = tmp_path / "note.txt"
    p.write_text("  padded text  \n", encoding="utf-8")
    assert extract_text(p) == "padded text"


def test_build_collection_writes_index_files(tmp_path, monkeypatch):
    papers_dir = tmp_path / "papers"
    index_dir = tmp_path / "index"
    monkeypatch.setattr(bi, "PAPERS_DIR", papers_dir)
    monkeypatch.setattr(bi, "INDEX_DIR", index_dir)
    coll_dir = papers_dir / "physics"
    coll_dir.mkdir(parents=True)
    (coll_dir / "a.md").write_text("quantum gravity and entropy", encoding="utf-8")
    (coll_dir / "b.txt").write_text("depolarizing channel noise model", encoding="utf-8")

    with patch.object(bi, "get_embedder", return_value=FakeEmbedder()):
        bi.build_collection("physics")

    out_dir = index_dir / "physics"
    assert (out_dir / "chunks.json").exists()
    assert (out_dir / "vectorizer.pkl").exists()
    assert (out_dir / "matrix.pkl").exists()
    assert (out_dir / "embeddings.npy").exists()


def test_build_collection_empty_dir_writes_nothing(tmp_path, monkeypatch, capsys):
    papers_dir = tmp_path / "papers"
    index_dir = tmp_path / "index"
    monkeypatch.setattr(bi, "PAPERS_DIR", papers_dir)
    monkeypatch.setattr(bi, "INDEX_DIR", index_dir)
    (papers_dir / "empty").mkdir(parents=True)

    bi.build_collection("empty")

    assert not (index_dir / "empty" / "chunks.json").exists()
    assert "nothing to index" in capsys.readouterr().out


def test_main_with_collection_arg_builds_only_that_one(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["build_index.py", "--collection", "physics"])
    calls = []
    monkeypatch.setattr(bi, "build_collection", lambda name: calls.append(name))
    bi.main()
    assert calls == ["physics"]


def test_main_no_arg_builds_every_collection_under_papers(tmp_path, monkeypatch):
    papers_dir = tmp_path / "papers"
    (papers_dir / "alpha").mkdir(parents=True)
    (papers_dir / "beta").mkdir(parents=True)
    monkeypatch.setattr(bi, "PAPERS_DIR", papers_dir)
    monkeypatch.setattr(sys, "argv", ["build_index.py"])
    calls = []
    monkeypatch.setattr(bi, "build_collection", lambda name: calls.append(name))
    bi.main()
    assert calls == ["alpha", "beta"]


def test_main_no_collections_found_prints_message(tmp_path, monkeypatch, capsys):
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir(parents=True)
    monkeypatch.setattr(bi, "PAPERS_DIR", papers_dir)
    monkeypatch.setattr(sys, "argv", ["build_index.py"])
    bi.main()
    assert "No collections found" in capsys.readouterr().out
