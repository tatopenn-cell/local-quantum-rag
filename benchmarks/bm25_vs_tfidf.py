"""Benchmark: BM25 vs Dense-Armor TF-IDF vs sklearn TF-IDF.

Three systems on the same 12 questions, each with a known source paper:

- ``bm25``: the BM25Index of ``bm25_index.py`` (Silajev 2026, page 1 term
  score + page 4 score), built on the Dense-Armor Tokenizer with unigrams.
- ``dense_tfidf``: the Dense-Armor TextVectorizer + SparseCosineIndex,
  same Tokenizer (unigrams), same stop words.
- ``sklearn_tfidf``: the scikit-learn TfidfVectorizer with
  ``stem_tok.analyze`` (Snowball stemmer + ENGLISH_STOP_WORDS + bigrams),
  which is what local-quantum-rag uses today.

Output: ``benchmarks/bm25_vs_tfidf.json`` with the per-question ranks,
the reciprocal ranks, the build and query times, and the pairwise paired
Wilcoxon p-value and A12 effect size on the reciprocal ranks.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dense_armor.utility.preprocessing.vectorizer import TextVectorizer
from dense_armor.utility.stats.similarity import SparseCosineIndex

from bm25_index import BM25Index
from stem_tok import analyze

STOP = sorted(ENGLISH_STOP_WORDS)
TOP = 5


def _order(scores):
    s = np.asarray(scores, dtype=float)
    return np.lexsort((np.arange(len(s)), -s))


def _rank_of(order, expected, sources, top=TOP):
    exp = expected.lower()
    for r, i in enumerate(order[:top], 1):
        if exp in sources[i].lower():
            return r
    return 0


def _reciprocal_rank(order, expected, sources):
    exp = expected.lower()
    for r, i in enumerate(order, 1):
        if exp in sources[i].lower():
            return 1.0 / r
    return 0.0


def _a12(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    d = x[:, None] - y[None, :]
    return float((d > 0).mean() + 0.5 * (d == 0).mean())


def _bootstrap_a12(x, y, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    k = len(x)
    vals = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, k, size=k)
        vals[i] = _a12(np.asarray(x)[idx], np.asarray(y)[idx])
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def _wilcoxon_p(x, y):
    try:
        return float(wilcoxon(x, y).pvalue)
    except ValueError:
        return 1.0


def build_bm25(texts):
    t0 = time.perf_counter()
    idx = BM25Index(stop_words=STOP).fit(texts)
    return idx, time.perf_counter() - t0


def query_bm25(idx, q):
    t0 = time.perf_counter()
    s = idx.query(q)
    return s, time.perf_counter() - t0


def build_dense_tfidf(texts):
    t0 = time.perf_counter()
    v = TextVectorizer(ngram_range=(1, 1), stop_words=STOP, norm="l2").fit(texts)
    X = [v.transform_one({"text": d})["scores"] for d in texts]
    idx = SparseCosineIndex(X)
    return (v, idx), time.perf_counter() - t0


def query_dense_tfidf(pair, q):
    v, idx = pair
    t0 = time.perf_counter()
    qv = v.transform_one({"text": q})["scores"]
    s = idx.query(qv)
    return s, time.perf_counter() - t0


def build_sklearn(texts):
    t0 = time.perf_counter()
    vec = TfidfVectorizer(analyzer=analyze, max_features=20000)
    M = vec.fit_transform(texts)
    return (vec, M), time.perf_counter() - t0


def query_sklearn(pair, q):
    vec, M = pair
    t0 = time.perf_counter()
    qv = vec.transform([q])
    s = cosine_similarity(qv, M).ravel()
    return s, time.perf_counter() - t0


BUILDERS = {"bm25": build_bm25,
            "dense_tfidf": build_dense_tfidf,
            "sklearn_tfidf": build_sklearn}
QUERIERS = {"bm25": query_bm25,
            "dense_tfidf": query_dense_tfidf,
            "sklearn_tfidf": query_sklearn}
SYSTEMS = ["bm25", "dense_tfidf", "sklearn_tfidf"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chunks", required=True)
    p.add_argument("--qa", required=True)
    p.add_argument("--out", default=str(_ROOT / "benchmarks" / "bm25_vs_tfidf.json"))
    args = p.parse_args()

    t_start = time.perf_counter()

    chunks = json.loads(Path(args.chunks).read_text(encoding="utf-8"))
    qa = json.loads(Path(args.qa).read_text(encoding="utf-8"))
    sources = [c["source"] for c in chunks]
    texts = [c["text"] for c in chunks]

    print("=== read-once check ===")
    print(f"chunks: {len(chunks)}")
    print(f"questions: {len(qa)}")
    print(f"all sources non-empty: {all(bool(s) for s in sources)}")
    print(f"all questions have 'query' and 'expected': "
          f"{all('query' in x and 'expected' in x for x in qa)}")
    if len(qa) != 12:
        raise SystemExit(f"expected 12 questions, got {len(qa)}")

    print("\n=== expected vs sources ===")
    for item in qa:
        exp = item["expected"].lower()
        n = sum(1 for s in sources if exp in s.lower())
        print(f"  {item['expected']:<32} {n:>3} source(s)")
        if n == 0:
            raise SystemExit(f"expected {item['expected']!r} not a substring of any source")

    per_system = {}
    raw_scores = {}
    for name in SYSTEMS:
        print(f"\n=== building {name} ===")
        bundle, build_s = BUILDERS[name](texts)
        print(f"  build time: {build_s:.2f} s")
        ranks, rrs, qms, all_scores = [], [], [], []
        for item in qa:
            s, dt = QUERIERS[name](bundle, item["query"])
            order = _order(s)
            ranks.append(_rank_of(order, item["expected"], sources))
            rrs.append(_reciprocal_rank(order, item["expected"], sources))
            qms.append(dt * 1000.0)
            all_scores.append(np.asarray(s, dtype=float))
        all_arr = np.concatenate(all_scores) if all_scores else np.zeros(0)
        raw_scores[name] = {
            "min": float(all_arr.min()) if all_arr.size else 0.0,
            "max": float(all_arr.max()) if all_arr.size else 0.0,
            "mean": float(all_arr.mean()) if all_arr.size else 0.0,
        }
        per_system[name] = {
            "ranks": ranks,
            "rrs": rrs,
            "build_s": build_s,
            "query_ms_median": float(np.median(qms)),
            "query_ms_max": float(np.max(qms)),
            "rank1": int(sum(1 for r in ranks if r == 1)),
            "rank3": int(sum(1 for r in ranks if 1 <= r <= 3)),
            "rank5": int(sum(1 for r in ranks if 1 <= r <= 5)),
            "rr_median": float(np.median(rrs)),
            "rr_q1": float(np.quantile(rrs, 0.25)),
            "rr_q3": float(np.quantile(rrs, 0.75)),
        }
        d = per_system[name]
        print(f"  rank1={d['rank1']}/12  rank3={d['rank3']}/12  "
              f"rank5={d['rank5']}/12  RR_med={d['rr_median']:.3f}")

    print("\n=== systems table ===")
    hdr = (f"{'system':<15} {'build_s':>8} {'q_ms':>7} "
           f"{'r1':>4} {'r3':>4} {'r5':>4} {'RR_med':>7} {'RR_IQR':>18}")
    print(hdr); print("-" * len(hdr))
    for name in SYSTEMS:
        d = per_system[name]
        iqr = f"[{d['rr_q1']:.3f}, {d['rr_q3']:.3f}]"
        print(f"{name:<15} {d['build_s']:>8.2f} {d['query_ms_median']:>7.3f} "
              f"{d['rank1']:>4} {d['rank3']:>4} {d['rank5']:>4} "
              f"{d['rr_median']:>7.3f} {iqr:>18}")

    print("\n=== raw score ranges (before ranking) ===")
    print(f"{'system':<15} {'min':>13} {'max':>13} {'mean':>13}")
    for name in SYSTEMS:
        r = raw_scores[name]
        print(f"{name:<15} {r['min']:>13.4e} {r['max']:>13.4e} {r['mean']:>13.4e}")

    print("\n=== pairwise: paired Wilcoxon + A12 on RR ===")
    pairs = [(SYSTEMS[i], SYSTEMS[j])
             for i in range(len(SYSTEMS)) for j in range(i + 1, len(SYSTEMS))]
    pairwise = {}
    print(f"{'pair':<35} {'p':>8} {'A12':>6} {'A12_CI95':>18} "
          f"{'wins_a':>6} {'wins_b':>6} {'tie':>4}")
    for a, b in pairs:
        ra, rb = per_system[a]["rrs"], per_system[b]["rrs"]
        pv = _wilcoxon_p(ra, rb)
        a12v = _a12(ra, rb)
        lo, hi = _bootstrap_a12(ra, rb, n=2000, seed=0)
        wa = sum(1 for x, y in zip(ra, rb) if x > y)
        wb = sum(1 for x, y in zip(ra, rb) if x < y)
        tie = 12 - wa - wb
        key = f"{a}_vs_{b}"
        pairwise[key] = {"p": pv, "a12": a12v, "a12_ci95": [lo, hi],
                         "wins_a": wa, "wins_b": wb, "ties": tie}
        print(f"{key:<35} {pv:>8.4f} {a12v:>6.3f} "
              f"[{lo:.3f}, {hi:.3f}]".ljust(18) +
              f" {wa:>6} {wb:>6} {tie:>4}")

    print("\n=== per-question ranks (0 = not in top 5) ===")
    print(f"{'q':>2}  {'expected':<32} {'bm25':>4} {'dense':>5} {'sklearn':>7}  diff")
    for i, item in enumerate(qa, 1):
        r1 = per_system["bm25"]["ranks"][i - 1]
        r2 = per_system["dense_tfidf"]["ranks"][i - 1]
        r3 = per_system["sklearn_tfidf"]["ranks"][i - 1]
        diff = "" if (r1 == r2 == r3) else "  ←"
        print(f"{i:>2}  {item['expected']:<32} {r1:>4} {r2:>5} {r3:>7}{diff}")

    total_s = time.perf_counter() - t_start
    print(f"\ntotal: {total_s:.2f} s")
    if total_s > 60:
        print("WARNING: over 60 s")

    out = {
        "n_chunks": len(chunks),
        "n_questions": len(qa),
        "systems": per_system,
        "raw_score_ranges": raw_scores,
        "pairwise": pairwise,
        "total_seconds": total_s,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
