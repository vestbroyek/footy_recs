import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash_table import DataTable
from dash_table.Format import Format, Scheme
import pandas as pd
import datetime
# grab data
df = pd.read_csv('daily_df.csv')


# data table
columns = [
{'name': ['', 'Match ID'],
'id': 'id'},
{'name': ['Team', 'Home'],
'id': 'home'},
{'name': ['Team', 'Away'],
'id': 'away'},
{'name': ['Probability', 'Home win (%)'],
'id': 'prob_home'},
{'name': ['Probability', 'Draw (%)'],
'id': 'prob_draw'},
{'name': ['Probability', 'Away win (%)'],
'id': 'prob_away'},
{'name': ['Odds: William Hill', 'Home win'],
'id': 'odds_home'},
{'name': ['Odds: William Hill', 'Draw'],
'id': 'odds_draw'},
{'name': ['Odds: William Hill', 'Away win'],
'id': 'odds_away'},
{'name': ['Probability - odds difference (%)', 'Home win'],
'id': 'diff_home',
'type': 'numeric',
'format': Format(precision = 2, scheme = Scheme.decimal)},
{'name': ['Probability - odds difference (%)', 'Draw'],
'id': 'diff_draw',
'type': 'numeric',
'format': Format(precision = 2, scheme = Scheme.decimal)},
{'name': ['Probability - odds difference (%)', 'Away win'],
'id': 'diff_away',
'type': 'numeric',
'format': Format(precision = 2, scheme = Scheme.decimal)},
]

table = DataTable(columns = columns,
	data = df.to_dict(orient = 'records'),
	cell_selectable = False,
	sort_action = 'native',
	filter_action = 'native',
	style_cell = ({'textAlign': 'center', 'fontSize': 14, 'font-family': 'sans-serif',
		'background-color': '#f4faff'}),
	style_header = ({'background-color':'grey', 'color': 'white', 'fontSize': 18}),
	style_as_list_view = True,
	merge_duplicate_headers = True,
	style_data_conditional = [
	{
		'if': {
		'filter_query': '{diff_home} > 10',
		'column_id': 'diff_home'
		},
		'background-color': 'green',
		'color': 'white'
	},
	{
		'if': {
		'filter_query': '{diff_draw} > 10',
		'column_id': 'diff_draw'
		},
		'background-color': 'green',
		'color': 'white'
	},
	{
		'if': {
		'filter_query': '{diff_away} > 10',
		'column_id': 'diff_away'
		},
		'background-color': 'green',
		'color': 'white'
	}
	])

# date
current_date = str(datetime.datetime.now())[:10]

# initialise app
app = dash.Dash()
# layout
app.layout = html.Div(children = [
	html.H1('Welcome to Maurits\'s football recommendations web app!', 
		style = {'font-family': 'sans-serif',
		'textAlign': 'center',
		'color': 'darkblue'}),
	html.H2(f'These recommendations are for {current_date}. Last updated: {str(datetime.datetime.now())[11:20]}', 
		style = {'font-family': 'sans-serif',
		'textAlign': 'center',
		'color': 'darkblue'}),
	table],
	style = {'height': '100%', 'width': '100%', 'background-color': 'white'})

# run
if __name__ == '__main__':
	app.run_server(debug = True)
