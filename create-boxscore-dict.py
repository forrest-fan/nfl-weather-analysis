import pandas as pd
import json

df = pd.read_pickle("all-fantasy-stats.pkl")

boxDict = {}

for i, row in df.iterrows():
    gameID = row["Game ID"]

    if gameID in boxDict:
        boxDict[gameID].append(row.to_dict())
    else:
        boxDict[gameID] = [row.to_dict()]

with open('boxscore-dict.json', 'w+') as f:
    json.dump(boxDict, f)

print("done")