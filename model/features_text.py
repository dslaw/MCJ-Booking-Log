"""Models for crime classification based on charge descriptions."""

from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import (
    ENGLISH_STOP_WORDS,
    CountVectorizer,
    TfidfTransformer
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

import re
import string


DRUG_MODEL_FILENAME = "drug_crime_classifier.skmodel"
VIOLENT_MODEL_FILENAME = "violent_crime_classifier.skmodel"
NUMBER_TOKEN = " num "

def preprocess(text):
    lowered = text.lower()

    # Fix punctuation.
    without_slashes = lowered.replace("/", " ")
    without_punct = re.sub(r"[^\w\s]", "", without_slashes)

    # Replace numbers with a special token.
    without_numbers = re.sub(r"\d+", NUMBER_TOKEN, without_punct)

    # Fix known variations of "controlled", as in "controlled substance".
    fixed = re.sub(r"cntl|cntrd|contld|contrld", "controlled", without_numbers)
    return fixed

stemmer = PorterStemmer()

def tokenize(text):
    tokens = [
        token for token in wordpunct_tokenize(text)
        if token not in string.punctuation
    ]
    return [stemmer.stem(token) for token in tokens]

def prepare_stop_words(stop_words):
    prepared_stop_words = set()
    for w in ENGLISH_STOP_WORDS:
        p = preprocess(w)
        stop_tokens = tokenize(p)
        for t in stop_tokens:
            prepared_stop_words.add(t)
    return prepared_stop_words

def make_pipeline():
    stop_words = prepare_stop_words(ENGLISH_STOP_WORDS)
    vectorizer = CountVectorizer(
        analyzer="word",
        preprocessor=preprocess,
        tokenizer=tokenize,
        stop_words=stop_words,
        max_features=500
    )
    weighter = TfidfTransformer(norm=None)
    classifier = LogisticRegression(solver="liblinear", random_state=13)
    return Pipeline([
        ("vectorize", vectorizer),
        ("weight", weighter),
        ("classify", classifier)
    ])

def train_and_save_models():
    """Train crime classification models and persist in the
    current working directory under `*_crime_classifier.skmodel`.
    """
    # Hidden imports - only used to get training data.
    from config import pg_kwargs
    from features import is_drugcrime, is_violentcrime
    import pandas as pd
    import psycopg2

    with psycopg2.connect(**pg_kwargs) as conn:
        charges = pd.read_sql("select * from charges_t", con=conn)

    drug = map(is_drugcrime, charges.charge, charges.description)
    violent = map(is_violentcrime, charges.charge, charges.description)
    charges["drug"] = list(drug)
    charges["violent"] = list(violent)

    drug_pipeline = make_pipeline()
    violent_pipeline = make_pipeline()

    drug_pipeline.fit(charges.description, y=charges.drug)
    violent_pipeline.fit(charges.description, y=charges.violent)

    joblib.dump(drug_pipeline, DRUG_MODEL_FILENAME)
    joblib.dump(violent_pipeline, VIOLENT_MODEL_FILENAME)
    return

def load_model(model_name):
    """Load a trained crime text classifier from disk.

    Parameters
    ----------
    model_name : str
        The model name, one of ("drug", "violent").

    Returns
    -------
    model : sklearn.pipeline.Pipeline
        A fitted pipeline instance.
    """

    model_filename = {
        "drug": DRUG_MODEL_FILENAME,
        "violent": VIOLENT_MODEL_FILENAME,
    }[model_name]
    return joblib.load(model_filename)

