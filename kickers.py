from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

pfr = 'https://www.pro-football-reference.com'
gameLogs = [pd.read_pickle('./fantasy-stats.pkl')]
playerIDs = {}
uniquePlayers = 0
logCount = 0

with open("./team-codes.json", 'r') as fp:
    teamCodes = json.load(fp)

existingLogs = pd.read_pickle('./fantasy-stats.pkl')

for year in range(2020, 2011, -1):
    # Get top kickers each year
    soup = BeautifulSoup(requests.get(pfr + '/years/' + str(year) + '/kicking.htm').content, 'html.parser')
    parsed_table = soup.find_all('table')[0]
    print("Year", year)

    # Iterate through table of kickers and extract player ID
    for i, row in enumerate(parsed_table.find_all('tr')[2:]):
        if i > 50:
            print('Complete')
            break

        try:
            # Get base player info from list of all kickers
            dat = row.find('td', attrs={'data-stat': 'player'})
            name = " ".join(dat.a.get_text().split())
            pos = 'K'
            posRank = i + 1
            stub = dat.a.get('href')[:-4]
            playerID = stub[stub.rindex('/') + 1:]
            fgm = row.find('td', attrs={'data-stat': 'fgm'}).get_text()
            xpm = row.find('td', attrs={'data-stat': 'xpm'}).get_text()

            if fgm != '' or xpm != '':
                # Store player id in dict and export to json at end
                if name not in playerIDs:
                    playerIDs[name] = [playerID]
                    uniquePlayers += 1
                elif playerID not in playerIDs[name]:
                    playerIDs[name].append(playerID)
                    uniquePlayers += 1

                # Calculate player tier
                tier = 0
                if posRank <= 12:
                    # Tier 1 players (top 12 in pos rank)
                    tier = 1
                elif posRank <= 24:
                    tier = 2
                else:
                    tier = 3

                print(name, pos, stub)

                # Go to player's individual fantasy page to get game logs
                tdf = pd.read_html(pfr + stub + '/fantasy/' + str(year))[0]
                tdf.columns = tdf.columns.get_level_values(-1)                      # Only keep bottom row in table head
                tdf = tdf.rename(columns={'Unnamed: 4_level_2':'Away'})             # Rename 'away' column
                tdf['Away'] = [1 if r == '@' else 0 for r in tdf['Away']]           # Change @ to 1 and NaN to 0
                tdf = tdf.iloc[:,[1, 2, 3, 4, 5, -4, -3]]                           # Only keep useful stats
                # tdf['G#'] = tdf['G#'].astype(int)                                   # Change G# to int

                # Get avg fantasy pts
                avg = round((tdf.query('Date == "Total"')['FantPt'].iloc[0].astype(float)) / (tdf['FantPt'].size - 1), 2)
                print(avg)

                # Remove total from dataframe
                tdf = tdf.query('Date != "Total"')

                # Add additional data
                tdf['Name'] = name
                tdf['Position'] = pos
                tdf['Season'] = year
                tdf['Game ID'] = ["".join(date.split("-")) + '0' + (teamCodes[tm] if away == 0 else teamCodes[opp]) for date, tm, away, opp in zip(tdf['Date'], tdf['Tm'], tdf['Away'], tdf['Opp'])]
                tdf['Player ID'] = playerID
                tdf['Tier'] = tier
                tdf['Diff to Avg'] = [round(float(points) - avg, 2) for points in tdf['FantPt']]
                tdf['Boxscore'] = ['<a href="https://www.pro-football-reference.com/boxscores/' + gameId + '.htm">Boxscore</a>' for gameId in tdf['Game ID']]
                tdf = tdf.set_axis(tdf['Game ID'].tolist(), axis='index')

                # Add to gameLogs array
                gameLogs.append(tdf)
                logCount += 1
        except Exception as e:
            print(e)
            pass

gameLogs = pd.concat(gameLogs)
gameLogs.to_pickle('./all-fantasy-stats.pkl')
gameLogs.to_csv('./all-fantasy-stats.csv')
with open("./player-ids-k.json", 'w') as fp:
    json.dump(playerIDs, fp)

