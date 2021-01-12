from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

gameLogs = pd.read_pickle('./fantasy-stats.pkl')
with open("./player-ids.json", 'r') as fp:
    playerIDs = json.load(fp)

uniquePlayers = 0

for name in playerIDs:
    if (len(playerIDs[name]) > 1):
        print(playerIDs[name])
    uniquePlayers += len(playerIDs[name])

print("unique", uniquePlayers)

# Position players
# 35042 Logs
# 825 players
    