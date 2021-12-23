import http.client
import json
import pandas as pd
import datetime
import time
import os.path
from os import path
from pushsafer import Client

# initialise date
current_date = str(datetime.datetime.now())[:10]

# initialise API connection
conn = http.client.HTTPSConnection('v3.football.api-sports.io')
headers = {'x-rapidapi-host': 'v3.football.api-sports.io',
'x-rapidapi-key': 'b44ff87a21fd01aff1a00f803af0664e'}

# open files
# fixture IDs
print('Opening fixture ID file...')
with open(f'fixture_ids_{current_date}.json') as f:
    fixture_ids = json.load(f)
# fixture list
with open(f'fixture_list_{current_date}.json') as f:
    fixture_list = json.load(f)

### API calls
# for the first 10 fixtures (max API calls per minute), get statistical probability and William Hill's odds
fixture_probs = []
fixture_odds = []
print('Retrieving probabilities and William Hill\'s odds for each game...')
for fixture_id in fixture_ids[:5]: # try 2
    # first get prob
    conn.request('GET', f'/predictions?fixture={fixture_id}', headers = headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    fixture_probs.append([fixture_id,\
                              data['response'][0]['predictions']['percent']['home'],\
                              data['response'][0]['predictions']['percent']['draw'],\
                              data['response'][0]['predictions']['percent']['away']])
    # now William Hill's odds (bookmaker ID 7) & match winner (bet ID 1)
    conn.request('GET',\
        f'/odds?season=2021&bet=1&bookmaker=7&fixture={fixture_id}', headers = headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    # update dict with odds
    fixture_odds.append([fixture_id,\
                         data['response'][0]['bookmakers'][0]['bets'][0]['values']])

### Cleaning
# turn into dfs
list_df = pd.DataFrame(fixture_list, columns = ['id', 'home', 'away'])
probs_df = pd.DataFrame(fixture_probs, columns = ['id', 'prob_home', 'prob_draw', 'prob_away'])
odds_df = pd.DataFrame(fixture_odds, columns = ['id', 'odds'])

# col names
for i, col_name in zip(range(3), ['home', 'draw', 'away']):
    odds_df[f'odds_{col_name}'] = odds_df['odds'].apply(lambda x: x[i]['odd'])
odds_df.drop('odds', axis = 1, inplace = True)

# merge 
final_df = pd.concat([list_df, probs_df, odds_df], axis = 1, join = 'inner')
final_df = final_df.loc[:, ~final_df.columns.duplicated()]

# clean up % and convert dtype for prob cols
pct_cols = ['prob_home', 'prob_draw', 'prob_away']
for col in pct_cols:
    final_df[col] = final_df[col].str.replace('%', '')
# set all as float (bit lazy but OK)
final_df.iloc[:, 3:] = final_df.iloc[:, 3:].astype(float)

# calc implied prob from odds. If the 'real' probability is higher than the implied probability, it's a good bet
# also calc the size of this difference and sort by it
calc_dict = {
    'prob_home': 'odds_home',
    'prob_draw': 'odds_draw',
    'prob_away': 'odds_away'}

new_cols = ['diff_home', 'diff_draw', 'diff_away']
for k, v, new_col in zip(calc_dict.keys(), calc_dict.values(), ['diff_home', 'diff_draw', 'diff_away']):
    final_df[new_col] = final_df[k] - round(100 / final_df[v], 2)

# saving df
final_df.to_csv('daily_df.csv')

### Recommendations
# write recommendation
for index, row in final_df.iterrows():
    for col in ['diff_home', 'diff_draw', 'diff_away']:
        if row[col] > 0: 
            print(f'Recommendation found. Bet on {col[-4:]} \
            in the game between {row[1]} and {row[2]}.\
            The difference is  {int(row[col])}%.')

# notifications
client = Client('CWatZaW6emrT1jHCSORu')

# write notification
recs = []
if final_df.iloc[:, -3:].to_numpy().any():
    recs.append('Recommendation(s) found!')
    for index, row in final_df.iterrows():
        for col in ['diff_home', 'diff_draw', 'diff_away']:
            if row[col] > 0: 
                message = f'Bet on {col[-4:]} \
                in the game between {row[1]} and {row[2]}.\
                The difference is  {int(row[col])}%.'
                recs.append(message)
else:
    recs.append('No recommendations found.')

print('Sending notification(s)...')
for rec in recs:      
    resp = client.send_message(
        rec,
        'Daily football notification',
        48183,
        170
        )

# print status message
if resp['status']:
    print('Great succces!')
else:
    print('Something went wrong... The API says \'{}\''.format(resp['error']))