import pandas as pd

df = pd.read_csv("all-fantasy-stats.csv")
df.to_pickle("all-fantasy-stats.pkl")