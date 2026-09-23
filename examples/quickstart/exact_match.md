# Why exact-match search exists alongside semantic search

Semantic search ranks passages by topical similarity, not by literal wording. That is usually
what you want, but it has one specific failure mode: a short, load-bearing phrase (an exact
clause, a fixed parameter value, a named condition) can sit inside a chunk that is not the most
topically central one, so semantic ranking buries it below chunks that only discuss the topic in
general terms.

Exact-match search sidesteps this entirely: it does a plain substring or regex search over the
raw chunk text, with no embeddings and no model involved. The magic phrase for this example is
"the answer is 42 kelvin" -- a specific value that a purely semantic query would likely never
surface first, because nothing about the surrounding sentence is topically distinctive.
