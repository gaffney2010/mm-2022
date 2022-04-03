'''Make sure that categories work as expected.'''

import pandas as pd
from sklearn.linear_model import LogisticRegression


rows = [
    {"A": "m", "target": "s"},
    {"A": "m", "target": "t"},
    {"A": "n", "target": "u"},
    {"A": "m", "target": "s"},
    {"A": "m", "target": "t"},
    {"A": "m", "target": "u"},
    {"A": "m", "target": "s"},
    {"A": "m", "target": "t"},
    {"A": "n", "target": "u"},
    {"A": "m", "target": "s"},
    {"A": "n", "target": "t"},
    {"A": "n", "target": "u"},
    {"A": "n", "target": "s"},
    {"A": "n", "target": "t"},
    {"A": "n", "target": "u"},
]
df = pd.DataFrame(rows)
X = pd.get_dummies(df["A"])
y = df["target"]

print("HELLO")
clf = LogisticRegression().fit(X, y)
print(clf.classes_)
print(clf.predict_proba([[1, 0]]))
print(clf.predict_proba([[0, 1]]))
print("GOODBYE")
