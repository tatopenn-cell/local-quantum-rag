"""
quantum-rag -- a small, local, hybrid RAG index builder for grounding
technical/research conversations in your own PDFs and Markdown notes,
instead of trusting an external AI's citations or memory.

How it works: put PDFs/Markdown/text files under papers/<collection>/,
run this script, and it builds a local, offline index under
index/<collection>/ that query.py can search. Each collection is its
own independent vocabulary space (TF-IDF + dense embeddings), so
unrelated topics don't dilute each other's retrieval -- keep separate
subjects in separate collections rather than one big pile.

Retrieval is hybrid, two-stage (see query.py for stage 2):
stage 1 pools candidates from TF-IDF cosine (exact-term overlap, cheap)
UNION a dense bi-encoder (sentence-transformers/all-MiniLM-L6-v2,
catches paraphrases/synonyms TF-IDF misses -- Karpukhin et al. 2020,
"Dense Passage Retrieval for Open-Domain Question Answering"), then
stage 2 reranks the pool with a pretrained cross-encoder. embeddings.npy
holds the bi-encoder vectors per chunk, one file per collection,
rebuilt whenever this script runs.

Usage:
    python build_index.py                        # rebuild all collections
    python build_index.py --collection my_topic
    python query.py --collection my_topic "your question"
    python query.py --collection my_topic --exact "an exact phrase"
"""

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

ROOT = Path(__file__).parent
PAPERS_DIR = ROOT / "papers"
INDEX_DIR = ROOT / "index"
CHUNK_SIZE_CHARS = 1200
CHUNK_OVERLAP_CHARS = 200
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


_LIGATURES = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
    "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
}


def extract_text(doc_path: Path) -> str:
    if doc_path.suffix.lower() in (".md", ".txt"):
        text = doc_path.read_text(encoding="utf-8")
    else:
        doc = fitz.open(doc_path)
        # sort=True reorders spans into natural reading order (top-to-bottom,
        # column-by-column) instead of raw geometric position -- without it,
        # a two-column paper comes back with left/right column lines interlaced.
        text = "\n".join(page.get_text(sort=True) for page in doc)
        doc.close()

    # Typographic ligatures (fi/fl/ffi/...) come through as single Unicode
    # codepoints that break both plain-ASCII printing on Windows consoles
    # and TF-IDF tokenization (e.g. "e?cient" instead of "efficient") --
    # expand them to real ASCII before anything else touches this text.
    # Applies to .md/.txt too: a note exported from a PDF or LaTeX source
    # can carry the same ligatures.
    for lig, expansion in _LIGATURES.items():
        text = text.replace(lig, expansion)
    # Collapse the extraction whitespace mess (hyphenated line wraps,
    # repeated blank lines) into something more chunk-friendly.
    text = re.sub(r"-\n(?=[a-z])", "", text)   # de-hyphenate wrapped words
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def chunk_text(text: str, source: str):
    # Split into paragraph/sentence units first, then pack units into chunks
    # up to CHUNK_SIZE_CHARS -- this never cuts a chunk mid-sentence (a fixed
    # character window does, which can split a formula or a claim in half).
    units = []
    for para in re.split(r"\n{2,}", text):
        para = para.strip()
        if not para:
            continue
        if len(para) <= CHUNK_SIZE_CHARS:
            units.append(para)
        else:
            units.extend(s.strip() for s in _SENTENCE_SPLIT.split(para) if s.strip())

    chunks = []
    buf_units, buf_len = [], 0
    for unit in units:
        if buf_units and buf_len + 1 + len(unit) > CHUNK_SIZE_CHARS:
            chunks.append({"source": source, "text": " ".join(buf_units)})
            # Overlap: carry whole trailing sentences (never a partial one)
            # into the next chunk, up to CHUNK_OVERLAP_CHARS.
            carry, carry_len = [], 0
            for u in reversed(buf_units):
                if carry_len + len(u) > CHUNK_OVERLAP_CHARS:
                    break
                carry.insert(0, u)
                carry_len += len(u) + 1
            buf_units, buf_len = carry, carry_len
        buf_units.append(unit)
        buf_len += len(unit) + 1
    if buf_units:
        chunks.append({"source": source, "text": " ".join(buf_units)})
    return chunks


def build_collection(name: str):
    papers_dir = PAPERS_DIR / name
    index_dir = INDEX_DIR / name
    if not papers_dir.is_dir():
        available = sorted(p.name for p in PAPERS_DIR.iterdir() if p.is_dir()) if PAPERS_DIR.is_dir() else []
        raise SystemExit(f"[{name}] papers/{name}/ does not exist -- available collections: {available}")
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    doc_paths = sorted(
        p for p in papers_dir.iterdir() if p.suffix.lower() in (".pdf", ".md", ".txt")
    )
    for doc_path in doc_paths:
        text = extract_text(doc_path)
        chunks = chunk_text(text, doc_path.name)
        all_chunks.extend(chunks)
        print(f"[{name}] {doc_path.name}: {len(text)} chars -> {len(chunks)} chunks")

    if not all_chunks:
        print(f"[{name}] No PDFs/Markdown found in papers/{name}/ -- nothing to index.")
        return

    texts = [c["text"] for c in all_chunks]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=20000, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)
    embeddings = get_embedder().encode(texts, normalize_embeddings=True, show_progress_bar=False)

    # Build in a temp dir first, then swap it in with a single rename --
    # a crash mid-write never leaves index/<name>/ with some files rebuilt
    # and others stale (which load_collection could not otherwise detect).
    tmp_dir = Path(tempfile.mkdtemp(prefix=f".{name}.", dir=INDEX_DIR))
    with open(tmp_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    with open(tmp_dir / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(tmp_dir / "matrix.pkl", "wb") as f:
        pickle.dump(matrix, f)
    np.save(tmp_dir / "embeddings.npy", embeddings)
    if index_dir.exists():
        shutil.rmtree(index_dir)
    tmp_dir.rename(index_dir)

    print(f"[{name}] Indexed {len(all_chunks)} chunks from {len(doc_paths)} documents -> index/{name}/\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--collection",
        help="only (re)build this collection (subfolder name under papers/); default: all collections",
    )
    args = parser.parse_args()

    if args.collection:
        build_collection(args.collection)
        return

    collections = sorted(p.name for p in PAPERS_DIR.iterdir() if p.is_dir())
    if not collections:
        print("No collections found under papers/ -- nothing to index.")
        return
    for name in collections:
        build_collection(name)


if __name__ == "__main__":
    main()
