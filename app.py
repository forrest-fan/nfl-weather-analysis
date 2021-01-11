from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
from flask import Flask, redirect, url_for, render_template, request

gameStats = pd.read_pickle('game-stats.pkl')
weatherOnly = pd.read_pickle('weather-only.pkl')

allTemps = weatherOnly['Temperature (F)'].astype(int).tolist()
allWinds = weatherOnly['Wind Speed (mph)'].astype(int).tolist()

tempPercentiles = []
windPercentiles = []
labels = []
for i in range(0, 101, 5):
    tempPercentiles.append(np.percentile(allTemps, i))
    windPercentiles.append(np.percentile(allWinds, i))
    labels.append(i)

print(labels)


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
        count = 0
        for winner, covered, ouResult in zip(filteredWeather['Winner'], filteredWeather['Covered'], filteredWeather['O/U Result']):
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

        weatherDict = {
            'table': table,
            'count': count,
            'winners': winners,
            'covers': covers,
            'ou': ou
        }

        return weatherDict
    return render_template("index.html", tempPercentiles=tempPercentiles, windPercentiles=windPercentiles)

if __name__ == "__main__":
    app.run(debug=True)