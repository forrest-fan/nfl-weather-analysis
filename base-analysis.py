import pandas as pd
import numpy as np
import json

gameLogs = pd.read_pickle('./fantasy-stats.pkl')
weather = pd.read_pickle('./weather-only.pkl')
# Temps at 5th and 95th percentile
tempLo = 31
tempHi = 85

# Wind speed 95th percentile
windHi = 13

# Bad weather is considered anything with extreme temps, high winds, rain, or snow
coldGames = weather['Temperature (F)'].astype(int) < tempLo
hotGames = weather['Temperature (F)'].astype(int) > tempHi
windyGames = weather['Wind Speed (mph)'].astype(int) > windHi
rainGames = 'Rain' in weather['Forecast'].astype(str)
snowGames = 'Snow' in weather['Forecast'].astype(str)
badWeather = weather[coldGames | hotGames | windyGames | rainGames | snowGames]

playersBadWeather = []
diffToAvg = []
homeWin = 0
awayWin = 0
tie = 0
homeCov = 0
awayCov = 0
covPush = 0
over = 0
under = 0
ouPush = 0

for game in badWeather.iterrows():
    players = gameLogs[gameLogs['Game ID'] == game[0]]
    playersBadWeather.append(players)
    diffToAvg = diffToAvg + players['Diff to Avg'].tolist()
    if game[1]['Winner'] == 'Home':
        homeWin += 1
    elif game[1]['Winner'] == 'Away':
        awayWin += 1
    else:
        tie += 1
    
    if game[1]['Covered'] == 'Home':
        homeCov += 1
    elif game[1]['Covered'] == 'Away':
        awayCov += 1
    else:
        covPush += 1
    
    if game[1]['O/U Result'] == 'Over':
        over += 1
    elif game[1]['O/U Result'] == 'Under':
        under += 1
    else:
        ouPush += 1
print(diffToAvg)
diffToAvg = [float(i) for i in diffToAvg]
print(diffToAvg)
print("Average diff", np.average(diffToAvg))
print("Winner", homeWin, "-", awayWin, "-", tie)
print("Cover", homeCov, "-", awayCov, "-", covPush)
print("ou", over, "-", under, "-", ouPush)
playersBadWeather = pd.concat(playersBadWeather)
playersBadWeather.to_csv('players-bad.csv')