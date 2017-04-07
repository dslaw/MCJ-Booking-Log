## Modeling MCJ Booking Log

### EDA
Exploratory analysis of inmate data includes looking at the number of newly
booked inmates over time (`arrivals.py`), summary statistics (`eda.sql`) and
clustering analysis (`clustering.py`). Note that cluster analysis depends on
models which have been trained and saved to disk via:

```python
from features_text import train_and_save_models
train_and_save_models()
```

### Crime Classification
Two additional features are derived from the charges: whether an inmate has been
charged with a _violent_ crime, or with a _drug related_ crime. These are
determined by training separate models, which use NLP to detect the categories
individually. The process of these classification models can be seen in
`text_eda.py` and `features_text.py`.

### Dependencies
The following packages are necessary, and are all available from the
`conda-forge` conda channel:

```
hdbscan
matplotlib
nltk
numpy
pandas
psycopg2
scipy
sklearn
```

Access to the database is also necessary. A `config.py` file is used to store
the database parameters as map under the variable `pg_kwargs`, but may be
substituted (the python file is not checked into git).
