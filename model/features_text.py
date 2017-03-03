"""Derive features from charges text."""

from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import make_pipeline

import re
import string


def replace_numbers(text, placeholder="num"):
    repl = " {0} ".format(placeholder)
    return re.sub(r"\d+", repl, text)

def replace_controlled(text):
    """Fix known variations of 'controlled' (e.g. controlled substance)."""
    return re.sub(r"cntl|cntrd|contld|contrld", "controlled", text)

def fix_punct(text):
    s = text.replace("/", " ")
    return re.sub(r"[^\w\s]", "", s)

stemmer = PorterStemmer()

def tokenize(text):
    text = text.lower()
    normalized = replace_controlled(replace_numbers(fix_punct(text)))
    tokens = [
        token for token in wordpunct_tokenize(normalized)
        if token not in string.punctuation
    ]
    return [stemmer.stem(token) for token in tokens]


text_pipeline = make_pipeline(
    CountVectorizer(tokenizer=tokenize, max_features=500),
    TfidfTransformer(norm="l2")
)

