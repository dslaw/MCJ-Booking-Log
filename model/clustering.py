"""Cluster Analysis of inmates."""

from config import pg_kwargs
import features

from collections import Counter
from scipy.spatial import distance
from features_text import load_model
from sklearn.manifold import MDS
from sklearn.preprocessing import scale
from hdbscan import HDBSCAN

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2


def dist(x, metric):
    y = distance.pdist(x, metric)
    return distance.squareform(y)

def scatter(x, y, labels, ax=None, palette="Accent"):
    if ax is None:
        _, ax = plt.subplots()

    cmap = plt.get_cmap(palette)
    for label in np.unique(labels):
        idx = labels == label
        ax.scatter(x[idx], y[idx], c=[cmap(label)], label=label)

    return ax


with open("read.sql", "r") as fh:
    queries = fh.read().split("\n\n")
    queries = [query.strip() for query in queries]
    inmate_query, charge_query = filter(None, queries)

with psycopg2.connect(**pg_kwargs) as conn:
    df = pd.read_sql(inmate_query, con=conn)
    charges = pd.read_sql(charge_query, con=conn)


# Clean empty strings.
# TODO: fix this in the scraper or create a view
charges.level[charges.level == ""] = None

# Create indicators.
df["male"] = df.sex.map(features.is_male)
df["unemployed"] = df.occupation.map(features.is_unemployed)

# Set severity level names.
level_mapping = {
    "f": "felonies",
    "m": "misdemeanors",
    "i": "infractions",
    "x": "level_unknowns",
}
charges["level"] = charges.level.map(lambda s: level_mapping.get(s))

# Get features from charges.
drug_classifier = load_model("drug")
violent_classifier = load_model("violent")

charges["drug"] = drug_classifier.predict(charges.description)
charges["violent"] = violent_classifier.predict(charges.description)

# Roll-up charges and merge with inmates data.
rows = []
for booking_id, group in charges.groupby("booking_id"):
    rows.append({
        **group.level.value_counts().to_dict(),
        "n_charges":  group.shape[0],
        "total_bail": group.bail.sum(),
        "drug":       np.any(group.drug),
        "violent":    np.any(group.violent),
        "booking_id": booking_id,
    })

rollup = pd.DataFrame(rows).set_index("booking_id")
int_cols = list(level_mapping.values())
rollup[int_cols] = rollup[int_cols].fillna(0).astype(int)

# Join onto inmates.
del df["jail_id"]
x = rollup.merge(
    df,
    how="inner",
    left_index=True,
    right_on="booking_id"
)


# Cluster.
variables = [
    "age",
    "drug",
    "felonies",
    "infractions",
    "male",
    "misdemeanors",
    "unemployed",
    "violent",
]
missing = x[variables].isnull().any(axis=1)
X = x.loc[~missing, variables]

pd.scatter_matrix(X)

# Visualize using MDS, as we use a distance based clustering method.
# https://datascience.stackexchange.com/questions/22/k-means-clustering-for-mixed-numeric-and-categorical-data
Z = scale(X.astype(float))
scale_dist = dist(Z, "braycurtis")

mds_scale = MDS(n_components=2, dissimilarity="precomputed", max_iter=1000)
coords_scale = mds_scale.fit_transform(scale_dist)
plt.scatter(*coords_scale.T)

# Run HDSCAN* over precomputed distances.
clusterer = HDBSCAN(min_cluster_size=50, metric="precomputed")
labels = clusterer.fit_predict(scale_dist)

# Cursory diagnostics.
Counter(labels)
clusterer.cluster_persistence_
np.mean(clusterer.probabilities_[labels != -1])

fig, axes = plt.subplots(1, 2)
ax1, ax2 = axes

scatter(*coords_scale.T, labels=labels + 1, ax=ax1)
ax1.legend()
ax1.set_title("Clusters")

ax2.hist(clusterer.probabilities_[labels != -1], bins=60, normed=True)
ax2.set_title("Probability of belonging to assigned cluster")


# Summary statistics by cluster.
clustered = x[~missing].copy()
clustered["labels"] = labels
clustered["dummy"] = 1

agg = {
    "age": {
        "average": "median",
        "min": "min",
        "max": "max",
    },
    "infractions": {
        "average": "mean",
        "min": "min",
        "max": "max",
    },
    "misdemeanors": {
        "average": "mean",
        "min": "min",
        "max": "max",
    },
    "felonies": {
        "average": "mean",
        "min": "min",
        "max": "max",
    },
    "n_charges": {
        "total": "sum",
        "average": "mean",
    },
    "violent": {
        "total": "sum",
        "average": "mean",
    },
    "drug": {
        "total": "sum",
        "average": "mean",
    },
    "male": {
        "total": "sum",
        "proportion": lambda x: x.astype(int).mean(),
    },
    "unemployed": {
        "total": "sum",
        "proportion": lambda x: x.astype(int).mean(),
    }
}

summary_overall = clustered.groupby("dummy").aggregate(agg)
summary_cluster = clustered.groupby("labels").aggregate(agg)

print(summary_overall)
print(summary_cluster)

