"""Explore feature engineering on charges."""

from bookinglog import config
from features_text import tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit

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
weighter = TfidfTransformer(norm=None)

tf = vectorizer.fit_transform(charges.description)
tfidf = weighter.fit_transform(tf)


# See if engineered features identify the presence of violent or
# drug crimes well.
y = charges.violent
X = tfidf
sss = StratifiedShuffleSplit(
    n_splits=2,
    test_size=.3,
    random_state=13)
train_idx, test_idx = next(sss.split(X, y))  # 70 / 30

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X[test_idx], y[test_idx]

model = LogisticRegression(solver="liblinear", random_state=13)\
    .fit(X_train, y=y_train)
y_pred = model.predict(X_test)

model.score(X_test, y_test)
confusion_matrix(y_test, y_pred, labels=[True, False])

# Check what's going on...
false_negative = y_test & ~y_pred
false_positive = ~y_test & y_pred

charges.iloc[test_idx][false_negative]
charges.iloc[test_idx][false_positive]
# ...it would appear that the two false positives are mislabeled.

# Drug crimes, on the same input data.
y = charges.drug
y_train, y_test = y[train_idx], y[test_idx]

drug_model = LogisticRegression(solver="liblinear", random_state=13)\
    .fit(X_train, y=y_train)
y_pred = drug_model.predict(X_test)

drug_model.score(X_test, y_test)
confusion_matrix(y_test, y_pred, labels=[True, False])

false_positive = ~y_test & y_pred
charges.iloc[test_idx][false_positive]
# Possess/sell a switchblade... yeah that makes sense.


# See if the models still perform when multiple charges are collapsed to a
# single inmate. One charge in the positive category is sufficient.
by_inmate = charges.groupby("booking_id").aggregate({
    "description": lambda xs: " ".join(xs),
    "drug": "any",
    "violent": "any",
})

features = weighter.transform(
    vectorizer.transform(by_inmate.description)
)
violent_pred = model.predict(features)
drug_pred = drug_model.predict(features)

confusion_matrix(violent_pred, by_inmate.violent, labels=[True, False])
confusion_matrix(drug_pred, by_inmate.drug, labels=[True, False])
# Good recall and poor precision on both. Although the drug model fairs better.

# Instead of merging charges and predicting on those, predict on individual
# charges and take `any` over them.
v_pred = model.predict(tfidf)
d_pred = drug_model.predict(tfidf)

pred_agg = pd.DataFrame({
    "booking_id": charges.booking_id,
    "violent_pred": v_pred,
    "drug_pred": d_pred
}).groupby("booking_id").aggregate({
    "violent_pred": "any",
    "drug_pred": "any"
}).reset_index()

confusion_matrix(pred_agg.violent_pred, by_inmate.violent, labels=[True, False])
confusion_matrix(pred_agg.drug_pred, by_inmate.drug, labels=[True, False])
# Much better. Less noise when charges are looked at individually.

