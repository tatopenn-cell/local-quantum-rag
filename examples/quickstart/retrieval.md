# How hybrid retrieval works

A pure keyword search misses anything phrased differently than the source text, even when the
meaning is identical. A pure semantic search, on the other hand, can rank a topically-similar but
factually-wrong passage above the one short sentence that actually answers the question, because
embeddings capture topic more than precision.

Hybrid retrieval pools candidates from both a sparse method (TF-IDF cosine similarity, which
rewards exact term overlap) and a dense method (a bi-encoder that embeds query and passage
into the same vector space, which catches paraphrases and synonyms). The union of both pools is
then reranked by a cross-encoder, a slower but far more accurate model that looks at the query
and each candidate passage together, rather than independently.

The result is a two-stage system: cheap, broad recall first, then an expensive, accurate pass over
a small candidate set.
