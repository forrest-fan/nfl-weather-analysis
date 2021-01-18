from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import math

gameLogs = pd.read_pickle('./fantasy-stats.pkl')

gameLogs['Diff to Avg'] = [0 if math.isnan(r) else r for r in gameLogs['Diff to Avg']]

gameLogs.to_csv('fantasy-stats.csv')
gameLogs.to_pickle('fantas-stats.pkl')

# Position players
# 35042 Logs
# 825 players
    