from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

pfr = 'https://www.pro-football-reference.com'
year = 2020

r = requests.get(pfr + '/years/' + str(year) + '/fantasy.htm')       # get html from list of all fantasy rankings
soup = BeautifulSoup(r.content, 'html.parser')                      # create soup object from html code to organize tags
parsed_table = soup.find_all('table')[0]                            # extract the first table (table of all players)

# Empty array to store all dataframes
df = []

# iterate through all rows starting from index 2 (first player)
for i, row in enumerate(parsed_table.find_all('tr')[2:]):
    if i > 200:
        print('Complete')
        break
    try:
        dat = row.find('td', attrs={'data-stat': 'player'})                 # find data item with attribute data-stat: player
        name = dat.a.get_text()                                             # get player name
        pos = row.find('td', attrs={'data-stat': 'fantasy_pos'}).get_text   # get player's position
        stub = dat.a.get('href')                                            # get href to player stats
        stub = stub[:-4] + '/fantasy/' + str(year)                          # get href to players fantasy stats
        
        # Use pandas to extract fantasy data
        tdf = pd.read_html(pfr + stub)[0]
        tdf.columns = tdf.columns.get_level_values(-1)                      # Only keep bottom row in table head
        tdf = tdf.rename(columns={'Unnamed: 4_level_2':'Away'})             # Rename 'away' column
        tdf['Away'] = [1 if r == '@' else 0 for r in tdf['Away']]           # Change @ to 1 and NaN to 0
        tdf = tdf.iloc[:,[1, 2, 3, 4, 5, -3]]                               # Only keep useful stats
        tdf = tdf.query('Date != "Total"')                                  # Keep everything except Total row
        tdf['Name'] = name
        tdf['Position'] = pos
        tdf['Season'] = year
        df.append(tdf)
    except Exception as e:
        print(e)
        pass                                                                # skip lines without a tag

df = pd.concat(df)
df.head()
# df.to_csv('fantasy2020.csv')