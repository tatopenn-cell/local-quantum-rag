import json
import os
import pickle
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

from stem_tok import analyze

INDEX_DIR = Path(__file__).parent / "index"


def refit(name):
    d = INDEX_DIR / name
    with open(d / "chunks.json", encoding="utf-8") as f:
        texts = [c["text"] for c in json.load(f)]
    vec = TfidfVectorizer(analyzer=analyze, max_features=20000)
    mat = vec.fit_transform(texts)
    for fn, obj in (("vectorizer.pkl", vec), ("matrix.pkl", mat)):
        p = d / fn
        bak = d / (fn + ".bak")
        if p.exists() and not bak.exists():
            os.replace(p, bak)
        with open(p, "wb") as f:
            pickle.dump(obj, f)
    print(f"{name}: {len(texts)} chunks")


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(p.name for p in INDEX_DIR.iterdir() if (p / "chunks.json").exists())
    for n in names:
        refit(n)
