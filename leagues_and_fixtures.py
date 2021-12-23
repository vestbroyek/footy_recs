import http.client
import json
import pandas as pd
import datetime
import time
import os.path
from os import path

# initialise: connection and authentication
conn = http.client.HTTPSConnection('v3.football.api-sports.io')
headers = {'x-rapidapi-host': 'v3.football.api-sports.io',
'x-rapidapi-key': 'b44ff87a21fd01aff1a00f803af0664e'}

print('Fetching data and writing to file...')

conn.request('GET', '/leagues', headers = headers)
res = conn.getresponse()

# decode data and turn into json
data = res.read().decode('utf-8')

# write to file
with open('leagues_data.json', 'w') as f:
	f.write(data)
	f.close()

# open fetched file
f = open('leagues_data.json')
data = json.load(f)

print('Processing data...')

# get dict
response = data['response']

# create list of lists with IDs, countries, league names
leagues = []
for league in response:
    leagues.append([league['league']['id'],\
    	league['league']['name'],\
    	league['country']['name'],\
    	league['seasons'][0]['year']])

# turn into df
leagues_df = pd.DataFrame(leagues,\
	columns = ['id', 'league_name', 'country', 'season'])

# league-country combinations to fetch IDs for
leagues_dict = {
    'England': 'Premier League',
    'Germany': 'Bundesliga 1',
    'Spain': 'La Liga',
    'Italy': 'Serie A',
    'France': 'Ligue 1',
    'Portugal': 'Primeira Liga',
    'Netherlands': 'Eredivisie',
    'Scotland': 'Premiership',
    'Russia': 'Premier League'}

# function to get IDs from list of lists
def return_id(country, league_name):
    return leagues_df[(leagues_df['country'] == country) & (leagues_df['league_name'] == league_name)]['id']

# print and store league ids
ids = []
for country, league in leagues_dict.items():
    print(f'Country: {country},\
    	League: {league}')
    ids.append(int(return_id(country, league)))

# now need to get fixtures
# first get current date as a str in YYYY-MM-DD format
current_date = str(datetime.datetime.now())[:10]

# make requests by looping through ids
daily_fixtures = [] # this will be a list of dicts
for id in ids: # NB hardcoded arg season in conn.request
	conn.request('GET',\
		f'/fixtures?league={id}&date={current_date}&season=2021',\
		headers = headers)
	res = conn.getresponse()
	data = json.loads(res.read().decode('utf-8')) # convert to dict
	# append. this yields a list of dicts, each dict containing 
	# an API response for 1 league on that day
	daily_fixtures.append(data)

# now extract fixture IDs and who home/away is
fixture_list = []
fixture_ids = []
# first loop through every league
for daily_list in daily_fixtures:
	# then through every match
    for i in range(len(daily_list['response'])):
        fixture_list.append([daily_list['response'][i]['fixture']['id'],\
                             daily_list['response'][i]['teams']['home']['name'],\
                             daily_list['response'][i]['teams']['away']['name']])
        fixture_ids.append(daily_list['response'][i]['fixture']['id'])

# we now have a list of lists containing ID, home and away and a list of fixture IDs
# write fixture list and IDs to file to fetch by next script
current_date = str(datetime.datetime.now())[:10]
print('Today\'s fixtures:')
for fixture in fixture_list:
    print(fixture[1], 'vs', fixture[2], '\n')
print('Writing fixture IDs and fixture list to file...')
with open(f'fixture_ids_{current_date}.json', 'w') as f:
    f.write(str(fixture_ids))
    f.close()
with open(f'fixture_list_{current_date}.json', 'w') as f:
  json.dump(fixture_list, f)

# check if successful
if path.exists(f'fixture_ids_{current_date}.json'):
    print('Fixture IDs successfully written to file.')
if path.exists(f'fixture_list_{current_date}.json'):
    print('Daily fixture list successfully written to file.')
