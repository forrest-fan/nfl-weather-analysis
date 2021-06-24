from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
from flask import Flask, redirect, url_for, render_template, request

gameStats = pd.read_pickle('./static/game-stats.pkl')
weatherOnly = pd.read_pickle('./static/weather-only.pkl')
playerStats = pd.read_pickle('./static/all-fantasy-stats.pkl')

with open('./static/percentiles.json', 'r') as fp:
    percentiles = json.load(fp)

with open("./static/boxscore-dict.json", 'r') as f:
    boxscoreDict = json.load(f)

tempPercentiles = percentiles['temp']
windPercentiles = percentiles['wind']

app = Flask(__name__)

@app.route('/',  methods=['POST', 'GET'])
def home():
    global tempPercentiles, windPercentiles
    if request.method == 'POST':
        maxTemp = int(request.form['maxTemp'])
        minTemp = int(request.form['minTemp'])
        maxWind = int(request.form['maxWind'])
        minWind = int(request.form['minWind'])
        filteredWeather = weatherOnly[(weatherOnly['Temperature (F)'].astype(int) <= maxTemp) & (weatherOnly['Temperature (F)'].astype(int) >= minTemp) & (weatherOnly['Wind Speed (mph)'].astype(int) <= maxWind) & (weatherOnly['Wind Speed (mph)'].astype(int) >= minWind)]
        table = filteredWeather.to_html(escape=False, index=False)
        winners = [0, 0, 0]
        covers = [0, 0, 0]
        ou = [0, 0, 0]
        # Tier 1, 2, 3
        tierSum = [0, 0, 0]
        tierCount = [0, 0, 0]
        tierAvg = [0, 0, 0]
        # QB, RB, WR, TE, K
        positionSum = [0, 0, 0, 0, 0]
        positionCount = [0, 0, 0, 0, 0]
        positionAvg = [0, 0, 0, 0, 0]
        count = 0
        for gameID, winner, covered, ouResult in zip(filteredWeather.index, filteredWeather['Winner'], filteredWeather['Covered'], filteredWeather['O/U Result']):
            count += 1
            if winner == 'Home':
                winners[0] += 1
            elif winner == 'Away':
                winners[1] += 1
            else:
                winners[2] += 1
            
            if covered == 'Home':
                covers[0] += 1
            elif covered == 'Away':
                covers[1] += 1
            else:
                covers[2] += 1
            
            if ouResult == 'Over':
                ou[0] += 1
            elif ouResult =='Under':
                ou[1] += 1
            else:
                ou[2] += 1
            
            for player in boxscoreDict[gameID]:
                if player["Tier"] == 1:
                    tierSum[0] += player["Diff to Avg"]
                    tierCount[0] += 1
                elif player["Tier"] == 2:
                    tierSum[1] += player["Diff to Avg"]
                    tierCount[1] += 1
                else:
                    tierSum[2] += player["Diff to Avg"]
                    tierCount[2] += 1

                if player["Position"] == "QB":
                    positionSum[0] += player["Diff to Avg"]
                    positionCount[0] += 1
                elif player["Position"] == "RB":
                    positionSum[1] += player["Diff to Avg"]
                    positionCount[1] += 1
                elif player["Position"] == "WR":
                    positionSum[2] += player["Diff to Avg"]
                    positionCount[2] += 1
                elif player["Position"] == "TE":
                    positionSum[3] += player["Diff to Avg"]
                    positionCount[3] += 1
                else:
                    positionSum[4] += player["Diff to Avg"]
                    positionCount[4] += 1
            
            for i in range(3):
                tierAvg[i] = round(tierSum[i] / tierCount[i], 2)
            
            for i in range(5):
                positionAvg[i] = round(positionSum[i] / positionCount[i], 2)

        weatherDict = {
            'table': table,
            'count': count,
            'winners': winners,
            'covers': covers,
            'ou': ou,
            'tierAvg': tierAvg,
            'positionAvg': positionAvg
        }

        return weatherDict
    return render_template("index.html", tempPercentiles=tempPercentiles, windPercentiles=windPercentiles)

if __name__ == "__main__":
    app.run(debug=True)