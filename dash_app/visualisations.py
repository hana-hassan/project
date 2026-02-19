from urllib.request import urlopen
import json # to connect to api
import pandas as pd # for data 
import dash # for web app + visualisations
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import g


# gathers all laps from spa 2023 gp (one driver)
response = urlopen('https://api.openf1.org/v1/laps?session_key=9141&driver_number=16')
data = json.loads(response.read().decode('utf-8'))
df1 = pd.DataFrame(data)
# print (df)


# all laps from all drivers
response_3 = urlopen('https://api.openf1.org/v1/laps?session_key=9141')
data_3 = json.loads(response_3.read().decode('utf-8'))
df2 = pd.DataFrame(data_3)


#fig = make_subplots(rows=1, cols=1, shared_xaxes=True, shared_yaxes=True)

lap_dur_list = df1["lap_duration"].values.tolist()
#driver_list = df1["driver_number"].values.tolist()
lap_num_list = df1["lap_number"].values.tolist()
#print(lap_dur_list)

#fig1 = px.scatter(df1, x="lap_number", y="lap_duration", color="lap_duration")
#fig1.show()

#fig2 = px.density_heatmap(df1, x="lap_number", y="lap_duration")
#fig2.show()

#fig3 = px.line(df2, x="lap_number", y="lap_duration", color="driver_number", markers=True)
# fig3.show()

base_url = "https://api.openf1.org/v1/sessions"

response = urlopen("https://api.openf1.org/v1/sessions")
data = json.loads(response.read().decode('utf-8'))
df = pd.DataFrame(data)

# year = "2024"
# circuit = "Spa-Francorchamps"

# response_t = urlopen("https://api.openf1.org/v1/sessions?session_name=Race&year=2024&circuit_short_name=Spa-Francorchamps")
# test = json.loads(response_t.read().decode('utf-8'))
# dftest = pd.DataFrame(test)
# print(dftest)



# function semi-copied from https://ploomber.io/blog/dash-in-flask/ , check license


def init_app(url_path):
    #app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app = Dash(server=g.cur_app, url_base_pathname=url_path)

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1('F1 Data Visualisations')
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id="years", options = [{'label':year, 'value':year} for year in df["year"].unique()], 
                             value="2025", 
                             placeholder="Select a year"),

                dcc.Dropdown(id="circuits", options = [{'label': circuit_short_name, 'value': circuit_short_name} for circuit_short_name in df["circuit_short_name"].unique()],
                             value="Spa-Francorchamps",
                             placeholder="Select a circuit")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H3("Lap Times"),
                            dcc.Graph(id="lap_times"),

                        ])
                    ])
                ])
            ])
        ])
    ])

    #init_callbacks(app)
    return app.server
 
@callback(
    Output('lap_times', 'figure'),
    Input('years','value'),
    Input('circuits', 'value'))

# def init_callbacks(app):
#     @app.callback(
#         Output('lap_times', 'figure'),
#         Input('years','value'),
#         Input('circuits', 'value')
#     )

def update_lap_graph(selected_year, selected_circuit):
    if selected_year:
        if selected_circuit:

            #filter dataset so only specific race pops up
            df_year = df[df["year"] == selected_year]
            filtered_df = df_year[df_year["circuit_short_name"] == selected_circuit]

    if df_year.empty:
        print("No Sessions available")

    
    response_race = urlopen(f'https://api.openf1.org/v1/sessions?year={selected_year}&circuit_short_name={selected_circuit}&session_type=Race')
    data_race = json.loads(response_race.read().decode('utf-8'))
    race = pd.DataFrame(data_race)

    s_key = race["session_key"]

    resp_laps = urlopen(f'https://api.openf1.org/v1/laps?session_key={s_key}')
    data_laps = json.loads(resp_laps.read().decode('utf-8'))
    all_laps = pd.DataFrame(data_laps)

    fig =  px.line(all_laps, x="lap_number", y="lap_duration", color="driver_number", markers=True)
    return fig

# def init_callbacks(app):
#     @app.callback(
#         Output('lap_times', 'figure'),
#         Input('years','value'),
#         Input('circuits', 'value')
#     )(update_lap_graph) 