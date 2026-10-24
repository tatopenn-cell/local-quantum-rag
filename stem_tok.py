import re
from functools import lru_cache

from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_TOK = re.compile(r"(?u)\b\w\w+\b")
_stem = lru_cache(maxsize=None)(SnowballStemmer("english").stem)


def analyze(text):
    toks = [_stem(w) for w in _TOK.findall(text.lower()) if w not in ENGLISH_STOP_WORDS]
    return toks + [a + " " + b for a, b in zip(toks, toks[1:])]
