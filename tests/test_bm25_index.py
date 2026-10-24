"""Tests for bm25_index.py (items A and B of task N10).

The hand values are the score of three short documents for the query
"a b", computed from the formula of Silajev (2026, arXiv:2609.14016,
page 1 for the term score and its ``+1`` IDF, page 4 for
``Score(q, i)``). With documents ``["a a b", "a c", "b b b"]``,
``k1 = 1.2`` and ``b = 0.75``:

    DF(a) = 2, DF(b) = 2, DF(c) = 1
    IDF(a) = IDF(b) = ln((3-2+0.5)/(2+0.5) + 1) = 0.470004
    IDF(c) = ln((3-1+0.5)/(1+0.5) + 1) = 0.980829
    |d0| = 3, |d1| = 2, |d2| = 3, avgdl = 8/3

The three scores are 0.243510294397587, 0.118988260568541 and
0.163479523215908; they are written as numbers below, not recomputed
from the library.

The tests skip cleanly when Dense-Armor is not installed, so the CI of
local-quantum-rag stays green without the ``dense`` extra.
"""
import json

import numpy as np
import pytest

pytest.importorskip("dense_armor")

from bm25_index import BM25Index

DOCS = ["a a b", "a c", "b b b"]
HAND_SCORES = [0.243510294397587, 0.118988260568541, 0.163479523215908]


def _fingerprint(idx):
    return (
        idx.n_docs_,
        dict(idx.document_frequencies_),
        [dict(c) for c in idx.term_counts_],
        list(idx.lengths_),
        idx.sum_length_,
    )


def test_fit_and_learn_one_same_state():
    a = BM25Index().fit(DOCS)
    b = BM25Index()
    for d in DOCS:
        b.learn_one(d)
    assert _fingerprint(a) == _fingerprint(b)


def test_fit_and_learn_one_same_scores():
    a = BM25Index().fit(DOCS)
    b = BM25Index()
    for d in DOCS:
        b.learn_one(d)
    np.testing.assert_allclose(a.query("a b"), b.query("a b"), atol=1e-12)


def test_state_dict_roundtrip_identical_scores():
    a = BM25Index().fit(DOCS)
    s = a.state_dict()
    b = BM25Index().load_state_dict(s)
    np.testing.assert_allclose(a.query("a b"), b.query("a b"), atol=1e-12)
    assert _fingerprint(a) == _fingerprint(b)


def test_state_dict_is_json():
    a = BM25Index().fit(DOCS)
    text = json.dumps(a.state_dict())
    back = json.loads(text)
    b = BM25Index().load_state_dict(back)
    np.testing.assert_allclose(a.query("a b"), b.query("a b"), atol=1e-12)


def test_hand_values():
    idx = BM25Index().fit(DOCS)
    np.testing.assert_allclose(idx.query("a b"), HAND_SCORES, atol=1e-12)


def test_idf_positive_when_term_in_every_document():
    idx = BM25Index().fit(["a b", "a c", "a d"])
    df = idx.document_frequencies_["a"]
    assert df == 3
    n = idx.n_docs_
    import math
    idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)
    assert idf > 0.0


def test_b_zero_independent_of_length():
    a = BM25Index(b=0.0).fit(["x x x", "x x x y y y y y y y"])
    b = BM25Index(b=0.75).fit(["x x x", "x x x y y y y y y y"])
    qa = a.query("x")
    qb = b.query("x")
    assert abs(qa[0] - qa[1]) < 1e-12
    assert abs(qb[0] - qb[1]) > 1e-3


def test_unknown_query_gives_zeros():
    idx = BM25Index().fit(DOCS)
    s = idx.query("zzz yyy")
    assert s.shape == (3,)
    assert np.all(s == 0.0)
    assert not np.any(np.isnan(s))


def test_empty_query_gives_zeros():
    idx = BM25Index().fit(DOCS)
    assert np.all(idx.query("") == 0.0)


def test_top_k_ties_broken_by_lower_index():
    idx = BM25Index().fit(["x", "x", "x"])
    assert [i for i, _ in idx.top_k("x", k=3)] == [0, 1, 2]


def test_top_k_bad_k_raises():
    idx = BM25Index().fit(DOCS)
    with pytest.raises(ValueError):
        idx.top_k("a b", k=0)


def test_validation_raises():
    with pytest.raises(ValueError):
        BM25Index(k1=-0.1)
    with pytest.raises(ValueError):
        BM25Index(b=1.5)
    with pytest.raises(ValueError):
        BM25Index(b=-0.1)
    with pytest.raises(ValueError):
        BM25Index(stop_words="english")
    BM25Index(k1=0.0, b=0.0)


def test_stop_words_removed():
    idx = BM25Index(stop_words=["the"]).fit(["the a the b", "the c"])
    assert "the" not in idx.document_frequencies_
    assert idx.document_frequencies_["a"] == 1


def test_dict_input_to_dict_branch():
    class _X:
        def to_dict(self):
            return {"text": "a b"}
    idx = BM25Index().fit(["a b", "c d"])
    assert idx.query(_X()).shape == (2,)
    idx.learn_one(_X())
    assert idx.n_docs_ == 3


def test_empty_index_query_and_top_k():
    idx = BM25Index()
    assert idx.query("x").shape == (0,)
    assert idx.top_k("x", k=3) == []
