"""Explore feature engineering on charges."""

from bookinglog import config
from features_text import tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.neural_network import BernoulliRBM

import features
import pandas as pd
import psycopg2


with psycopg2.connect(**config.pg_kwargs) as conn:
    charges = pd.read_sql("select * from charges_t", con=conn)


drug = map(features.is_drugcrime, charges.charge, charges.description)
violent = map(features.is_violentcrime, charges.charge, charges.description)
charges["drug"] = list(drug)
charges["violent"] = list(violent)


vectorizer = CountVectorizer(
    analyzer="word",
    tokenizer=tokenize,
    stop_words="english",
    max_features=500)
weighter = TfidfTransformer(norm="l2")
rbm = BernoulliRBM(
    n_components=256,
    learning_rate=0.05,
    n_iter=300,
    random_state=13)

tf = vectorizer.fit_transform(charges.description)
tfidf = weighter.fit_transform(tf)
X = rbm.fit_transform(tfidf)


# See if engineered features identify the presence of violent or
# drug crimes well.
def run(X, y):
    sss = StratifiedShuffleSplit(
        n_splits=2,
        test_size=.3,
        random_state=13)

    train_idx, test_idx = next(sss.split(X, y))
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    model = LogisticRegression(solver="liblinear", random_state=13)\
        .fit(X_train, y=y_train)
    y_pred = model.predict(X_test)
    return {
        "score": model.score(X_test, y_test),
        "confusion": confusion_matrix(y_test, y_pred, labels=[True, False])
    }


run(X, charges.violent)
run(tfidf, charges.violent)

run(X, charges.drug)
run(tfidf, charges.drug)

# tf-idf inputs score better. RBM features on violent crimes
# always predicts False. tf-idf doesn't do a good job of identifying
# violent crimes (recall ~55%).
