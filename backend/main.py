import pandas as pd
import json

df = pd.read_csv("data/tmdb_5000_movies.csv")
print(f"Nombre de films : {len(df)}")
print(df.columns.tolist())
print(df.head(2))