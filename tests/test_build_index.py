import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from build_index import chunk_text, extract_text, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS


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
