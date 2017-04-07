"""Models for crime classification based on charge descriptions."""

from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import re
import string


DRUG_MODEL_FILENAME = "drug_crime_classifier.skmodel"
VIOLENT_MODEL_FILENAME = "violent_crime_classifier.skmodel"

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

    vectorizer = CountVectorizer(
        analyzer="word",
        tokenizer=tokenize,
        stop_words="english",
        max_features=500
    )
    weighter = TfidfTransformer(norm=None)
    classifier = LogisticRegression(solver="liblinear", random_state=13)

    drug_pipeline = Pipeline([
        ("vectorize", vectorizer),
        ("weight", weighter),
        ("classify", classifier)
    ])

    violent_pipeline = Pipeline([
        ("vectorize", vectorizer),
        ("weight", weighter),
        ("classify", classifier)
    ])

    # Transformers are refit - it's cheap.
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

