from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
import time

pfr = 'https://www.pro-football-reference.com'
weather = 'http://www.nflweather.com/en'


with open("./team-codes.json", 'r') as fp:
    teamCodes = json.load(fp)

with open("./direction-degree.json", 'r') as fp:
    dirDeg = json.load(fp)

gameCounter = 0
homeWin = 0
awayWin = 0
tie = 0
homeCover = 0
awayCover = 0
pushCover = 0
over = 0
under = 0
ouPush = 0

seasonGames = []
windSpeeds = []
temps = []

for year in range(2011, 2008, -1):
    for i in range (1, 18):
        try:
            # Get weather data from NFLWeather.com
            gameWeather = pd.read_html(weather + '/week/' + str(year) + '/week-' + str(i))[0]

            # Set game id based on PFR team codes
            gameWeather['Game ID'] = [teamCodes[r] for r in gameWeather['Home']]

            # Separate forecast into temp and weather
            gameWeather['Temp'] = ['dome' if r == 'DOME' else r[:r.index('f')] for r in gameWeather['Forecast']]
            gameWeather['Forecast'] = ['dome' if r == 'DOME' else r[r.index(' ') + 1:] for r in gameWeather['Forecast']]
            print('got temp')
            # Separate wind into speed and direction (change to degrees)
            gameWeather['Wind Speed'] = ['dome' if s == 'dome' else r[:r.index('m')] for r, s in zip(gameWeather['Wind'], gameWeather['Forecast'])]
            gameWeather['Wind Direction'] = ['dome' if s == 'dome' else dirDeg[r[r.index(' ') + 1:]] for r, s in zip(gameWeather['Wind'], gameWeather['Forecast'])]
            gameWeather = gameWeather[['Game ID', 'Temp', 'Forecast', 'Wind Speed', 'Wind Direction']]
            print('got wind')
            # Go to PFR page with all boxscores from week i
            games = BeautifulSoup(requests.get(pfr + '/years/' + str(year) + '/week_' + str(i) + '.htm').content, 'html.parser').find_all('table', class_='teams')
            for game in games:
                try:
                    # Get href to individual game and extract HTML
                    gameLink = game.find('td', attrs={'class': 'gamelink'})
                    href = gameLink.a.get('href')
                    gameID = href[href.index('/', 1) + 1:-4]
                    gameHTML = BeautifulSoup(requests.get(pfr+href).content, 'html.parser')
                    print('got href')
                    # Find row with matching weather data
                    for k in range(gameWeather['Game ID'].size):
                        if gameWeather['Game ID'].iloc[k] == gameID[-3:]:
                            break

                    # Game info data
                    # Find comment with game info and extract HTML code and convert to DataFrame
                    gameInfoComment = str(gameHTML.find(id='all_game_info'))
                    gameInfoComment = gameInfoComment[gameInfoComment.index('<!--') + 5:gameInfoComment.index('-->')]

                    # Rotate df and move 1st row to header
                    gameInfo = pd.read_html(gameInfoComment)[0].transpose()
                    gameInfo.columns = gameInfo.iloc[0]
                    gameInfo = gameInfo[1:]

                    # Add weather data to DataFrame
                    gameInfo['Temp'] = gameWeather['Temp'].iloc[k]
                    gameInfo['Forecast'] = gameWeather['Forecast'].iloc[k]
                    gameInfo['Wind Speed'] = gameWeather['Wind Speed'].iloc[k]
                    gameInfo['Wind Direction'] = gameWeather['Wind Direction'].iloc[k]
                    if gameInfo['Temp'].iloc[0] is not 'dome':
                        windSpeeds.append(float(gameInfo['Wind Speed'].iloc[0]))
                        temps.append(float(gameInfo['Temp'].iloc[0]))

                    # Get teams and score and add to DataFrame
                    lineScore = pd.read_html(str(gameHTML), attrs={'class': 'linescore'})[0]
                    gameInfo['Away Team'] = lineScore['Unnamed: 1'].iloc[0]
                    gameInfo['Away Score'] = int(lineScore['Final'].iloc[0])
                    gameInfo['Home Team'] = lineScore['Unnamed: 1'].iloc[1]
                    gameInfo['Home Score'] = int(lineScore['Final'].iloc[1])

                    # Calculate winner
                    if int(gameInfo['Away Score'].iloc[0]) > int(gameInfo['Home Score'].iloc[0]):
                        gameInfo['Winner'] = 'Away'
                        awayWin += 1
                    elif int(gameInfo['Away Score'].iloc[0]) < int(gameInfo['Home Score'].iloc[0]):
                        gameInfo['Winner'] = 'Home'
                        homeWin += 1
                    else:
                        gameInfo['Winner'] = 'Tie'
                        tie += 1

                    # Update vegas line to home team spread
                    spread = 0
                    if gameInfo['Vegas Line'].iloc[0] == 'Pick':
                        spread = float(0)
                    else:
                        fav = gameInfo['Vegas Line'].iloc[0][:gameInfo['Vegas Line'].iloc[0].rfind(' ')]
                        spread = float(gameInfo['Vegas Line'].iloc[0][gameInfo['Vegas Line'].iloc[0].rfind(' '):])
                        if fav == gameInfo['Away Team'].iloc[0]:
                            spread = spread * -1

                    gameInfo['Home Spread'] = spread

                    # Who covered the spread
                    diff = int(gameInfo['Away Score'].iloc[0]) - int(gameInfo['Home Score'].iloc[0])
                    if diff > spread:
                        gameInfo['Covered'] = 'Away'
                        awayCover += 1
                    elif spread > diff:
                        gameInfo['Covered'] = 'Home'
                        homeCover += 1
                    else:
                        gameInfo['Covered'] = 'Push'
                        pushCover += 1

                    # Split O/U into O/U and result
                    ou = float(gameInfo['Over/Under'].iloc[0][:gameInfo['Over/Under'].iloc[0].index(' ')])
                    total = gameInfo['Away Score'].iloc[0] + gameInfo['Home Score'].iloc[0]
                    gameInfo['O/U'] = ou
                    if total > ou:
                        gameInfo['O/U Result'] = 'Over'
                        over += 1
                    elif ou > total:
                        gameInfo['O/U Result'] = 'Under'
                        under += 1
                    else:
                        gameInfo['O/U Result'] = 'Push'
                        ouPush += 1

                    # Remove unneccesary columns
                    gameInfo = gameInfo.drop(['Game Info', 'Attendance', 'Roof', 'Over/Under', 'Weather', 'Won Toss', 'Duration', 'Vegas Line'], axis=1, errors='ignore')

                    # Insert game ID
                    gameInfo['Game ID'] = gameID

                    # Append to games
                    seasonGames.append(gameInfo)
                    gameCounter += 1
                    print(gameID)
                    time.sleep(0.5)
                except Exception as error:
                    print("Error: ", error)
        except Exception as e:
            print(e)
            pass

seasonGames = pd.concat(seasonGames)
seasonGames.to_csv('game-stats.csv')

print("Number of games: ", gameCounter)
print("Winner H/A/T: ", homeWin, "-", awayWin, "-", tie)
print("Cover H/A/P: ", homeCover, "-", awayCover, "-", pushCover)
print("O/U O/U/P: ", over, "-", under, "-", ouPush)
print("5th pecentile temp: ", np.percentile(temps, 5))
print("25th pecentile temp: ", np.percentile(temps, 25))
print("50th pecentile temp: ", np.percentile(temps, 50))
print("75th pecentile temp: ", np.percentile(temps, 75))
print("95th pecentile temp: ", np.percentile(temps, 95))
print("5th pecentile wind: ", np.percentile(windSpeeds, 5))
print("25th pecentile wind: ", np.percentile(windSpeeds, 25))
print("50th pecentile wind: ", np.percentile(windSpeeds, 50))
print("75th pecentile wind: ", np.percentile(windSpeeds, 75))
print("95th pecentile wind: ", np.percentile(windSpeeds, 95))

# First batch results
# Number of games:  2233
# Winner H/A/T:  1242 - 982 - 9
# Cover H/A/P:  1052 - 1126 - 55
# O/U O/U/P:  1082 - 1122 - 29
# 5th pecentile temp:  31.0
# 75th pecentile temp:  72.0
# 95th pecentile temp:  85.0
# 5th pecentile wind:  0.0
# 25th pecentile wind:  3.0
# 50th pecentile wind:  5.0
# 75th pecentile wind:  8.0
# 95th pecentile wind:  13.0