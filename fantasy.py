from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

pfr = 'https://www.pro-football-reference.com'
gameLogs = []
playerIDs = {}
uniquePlayers = 0
logCount = 0

with open("./team-codes.json", 'r') as fp:
    teamCodes = json.load(fp)

for year in range (2020, 2011, -1):
    # Get top fantasy players of each year
    soup = BeautifulSoup(requests.get(pfr + '/years/' + str(year) + '/fantasy.htm').content, 'html.parser')
    parsed_table = soup.find_all('table')[0]
    print("Year", year)
    # iterate through all rows starting from index 2 (first player)
    for i, row in enumerate(parsed_table.find_all('tr')[2:]):
        if i > 250:
            # Stop after first 250 rows
            print('Complete')
            break
        try:
            # Get players' base info from list of all fantasy players
            # Name, position, player ID, fantasy ppg
            dat = row.find('td', attrs={'data-stat': 'player'})
            name = " ".join(dat.a.get_text().split())
            pos = row.find('td', attrs={'data-stat': 'fantasy_pos'}).get_text()
            posRank = int(row.find('td', attrs={'data-stat': 'fantasy_rank_pos'}).get_text())
            stub = dat.a.get('href')[:-4]
            playerID = stub[stub.rindex('/') + 1:]
            avg = round(float(row.find('td', attrs={'data-stat': 'fantasy_points'}).get_text()) / float(row.find('td', attrs={'data-stat': 'g'}).get_text()), 2)

            # Store player id in dict and export to json at end
            if name not in playerIDs:
                playerIDs[name] = playerID
                uniquePlayers += 1

            # Set tier and skip non QB, WR, RB, TE (will get K and DST in another scrape)
            tier = 0
            if pos != 'QB' and pos != 'RB' and pos != 'WR' and pos != 'TE':
                pass
            else:
                if posRank <= 12:
                    # Tier 1 players (top 12 in pos rank)
                    tier = 1
                elif posRank <= 24:
                    tier = 2
                else:
                    tier = 3
            print(name, pos, stub, avg)

            # Use pandas to extract fantasy data and organize table
            tdf = pd.read_html(pfr + stub + '/fantasy/' + str(year))[0]
            tdf.columns = tdf.columns.get_level_values(-1)                      # Only keep bottom row in table head
            tdf = tdf.rename(columns={'Unnamed: 4_level_2':'Away'})             # Rename 'away' column
            tdf['Away'] = [1 if r == '@' else 0 for r in tdf['Away']]           # Change @ to 1 and NaN to 0
            tdf = tdf.iloc[:,[1, 2, 3, 4, 5, -8, -3]]                           # Only keep useful stats
            tdf = tdf.query('Date != "Total"')                                  # Keep everything except Total row
            tdf['G#'] = tdf['G#'].astype(int)                                   # Change G# to int
            
            # Add additional data points
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
            pass                                                                # skip PFR lines with headers every 30 lines

gameLogs = pd.concat(gameLogs)
print(gameLogs.head())
gameLogs.to_csv('fantasy-stats.csv')
gameLogs.to_pickle('fantasy-stats.pkl')

with open("./player-ids.json", 'w') as fp:
    json.dump(playerIDs, fp)

print("Logs", logCount)
print("Individual players", uniquePlayers)