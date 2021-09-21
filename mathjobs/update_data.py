from mathjob_ovtime import find_trends
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pathlib import Path

project_dir = Path(__file__).resolve().parents[1]

date_range = list(range(2010, 2021))

subjects = [("number theory", "math.NT") ] #, ("differential geometry", "math.DG"), ("machine learning" , "cs.LG"), ("mathematical physics", "math.MP")]

df = pd.read_csv(project_dir / "data/processed/jobs.csv" )

rows = []

for subject in subjects:
    key_word = f"(?i){subject[0]}"
    key_words = [[key_word, 0]]

    key_word_counts = find_trends(date_range, key_words)

    y = key_word_counts[key_word]

    for i, j in zip(date_range, y):
        rows.append([subject[0], i, subject[1], j])
        #if df[(df["name"] == subject[0]) & (df["year"] == i) ].shape[0] == 0:

df2 = pd.DataFrame(rows, columns=["name","year","arxivId","jobCount"])

df = pd.concat([df, df2])

df.to_csv(project_dir / "data/processed/jobs.csv", index=False)