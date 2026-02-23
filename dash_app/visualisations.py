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
import requests
from data_filtering import get_laps, get_position, get_race, get_drivers, get_all_positions, get_stints

base_url_sessions = "https://api.openf1.org/v1/sessions"
base_url_drivers = "https://api.openf1.org/v1/drivers"

response = urlopen(base_url_sessions)
data = json.loads(response.read().decode('utf-8'))
df = pd.DataFrame(data)

response2 = urlopen(base_url_drivers)
data2 = json.loads(response2.read().decode('utf-8'))
df2 = pd.DataFrame(data2)

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
                html.H2('Select a year: '),
                dcc.Dropdown(id="years", options = [{'label':year, 'value':year} for year in df["year"].unique()], 
                             value="2025", 
                             placeholder="Select a year")
            ]),
            dbc.Col([
                html.H2('Select a circuit: '),
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
                            dcc.Graph(id="lap_times_hist"),
                            dcc.Graph(id="lap_times"),
                        ])
                    ])
                ])
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("Race Positions"),
                            dcc.Graph(id="positions_graph"),
                        ])
                    ])
                ])
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Dropdown(id="drivers", options = [{'label': full_name, 'value': full_name} for full_name in df2["full_name"].unique()], 
                            value="Lewis HAMILTON", 
                            placeholder="Select a driver"),
                        html.Div([
                            html.H2("Stints, Lap Times, and Tyre Degredation"),
                            dcc.Graph(id="stints_tyres"),
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
    Output('lap_times_hist', 'figure'),
    Output('positions_graph', 'figure'),
    Output('stints_tyres', 'figure'),
    Input('years','value'), 
    Input('circuits', 'value'),
    Input('drivers', 'value'),
    )

# def init_callbacks(app):
#     @app.callback(
#         Output('lap_times', 'figure'),
#         Input('years','value'),
#         Input('circuits', 'value')
#     )

def update_graphs(selected_year, selected_circuit, selected_driver):
    if selected_year:
        if selected_circuit:

            #filter dataset so only specific race pops up
            df_year = df[df["year"] == selected_year]
            filtered_df = df_year[df_year["circuit_short_name"] == selected_circuit]

            if df_year.empty:
                print("No Sessions available")
    
    params = {
        'year' : selected_year,
        'circuit_short_name' : selected_circuit,
        'session_type' : 'Race'
    }

    
    url_race = requests.Request('GET', base_url_sessions, params=params).prepare().url
    response_race = requests.get(url_race)
    race = pd.DataFrame(response_race.json())


    s_key = race["session_key"]

    driver_df = get_drivers(s_key)

    driver_num = driver_df.loc[driver_df["full_name"] == selected_driver, "driver_number"]
    
    if selected_driver:

        positions_df = get_position(driver_num, s_key)

        if positions_df.empty:
            print("No positions data available for this driver")

    # params1 = {
    #     'session_key' : s_key
    # }

    # url_laps = requests.Request('GET','https://api.openf1.org/v1/laps', params=params1).prepare().url
    # response_laps = requests.get(url_laps)
    # all_laps = pd.DataFrame(response_laps.json())


    all_laps = get_laps(s_key)
    all_positions = get_all_positions(s_key)
    dr_stints = get_stints(driver_num, s_key)

    fig_hist = px.histogram(all_laps, x="lap_duration")

    fig =  px.line(all_laps, x="lap_number", y="lap_duration", color="driver_number", markers=True)
    #fig = make_subplots(rows=2, cols=1, row_heights = [0.3, 0.7])

    # fig.add_trace(
    #     go.Histogram(
    #         x=all_laps["lap_duration"]
    #     ), row=1, col=1
    # )

    # fig.add_trace(
    #     go.Scatter(
    #         x=all_laps["lap_number"],
    #         y=all_laps["lap_duration"],
    #         marker=dict(
    #             color=all_laps["driver_number"]
    #         )
    #     ), row=2, col=1
    # )


    #fig1 = px.scatter(positions_df, x="date", y="position", color="position")
    #fig1 = go.Figure(data=go.Heatmap(z=all_positions["position"], x=all_positions["date"], y=all_positions["driver_number"]))
    fig1 = px.bar(all_positions, x="date", y="driver_number", color="position", orientation="h")
    fig1.update_yaxes(type='category')
    fig1.update_xaxes(type='date')

    #structure for the dumbbell plot copied from https://plotly.com/python/dumbbell-plots/#what-about-dash

    stints = dr_stints["stint_number"].unique()

    st_data = {"line_x" : [], "line_y" : [], "stint_start" : [], "stint_end" : [],
               "colors" : [], "stints" : [], "stint_num" : [], "tyre_age_start" : [], "tyre_age_end" : []}
    
    for st in stints:
        st_data["stint_start"].extend([dr_stints.loc[(dr_stints["stint_number"] == st)]["lap_start"].values[0]])
        st_data["stint_end"].extend([dr_stints.loc[(dr_stints["stint_number"] == st)]["lap_end"].values[0]])
        st_data["tyre_age_start"].extend([dr_stints.loc[(dr_stints["stint_number"] == st)]["tyre_age_at_start"].values[0]])
        st_data["tyre_age_end"].extend([dr_stints.loc[(dr_stints["stint_number"] == st)]["tyre_age_at_end"].values[0]])


        st_data["line_x"].extend(
            [
            dr_stints.loc[(dr_stints.stint_number == st)]["lap_start"].values[0],
            dr_stints.loc[(dr_stints.stint_number == st)]["lap_end"].values[0],
            None,
            ]
        )

        st_data["line_y"].extend([st, st, None])


    fig2 = go.Figure(
        data=[
            go.Scatter(
                x=st_data["line_x"],
                y=st_data["line_y"],
                mode="lines",
                showlegend=False,
                marker=dict(
                    color="black"
                )
            ),

            go.Scatter(
                x=st_data["stint_start"],
                y=stints,
                mode="markers",
                marker=dict(
                    color="green",
                    size=st_data["tyre_age_start"]
                )
            ),

            go.Scatter(
                x=st_data["stint_end"],
                y=stints,
                mode="markers",
                marker=dict(
                    color="red",
                    size=st_data["tyre_age_end"]
                )
            ),

        ]
    )




    return fig_hist, fig, fig1, fig2

# @callback(
#     Output('positions_graph', 'figure'),
#     Input('drivers', 'value'),
#     Input('year', 'value'),
#     Input('circuit', 'value')
# )

# def update_positions_graph(selected_driver, selected_year, selected_circuit):
#     if selected_year:
#         if selected_circuit:

#             race = get_race(selected_year, selected_circuit)

#             if race.empty:
#                 print("race not available")

#             s_key = race["session_key"]

#             driver_df = get_drivers(s_key)

#             driver_num = driver_df.loc[driver_df["full_name"] == selected_driver, "driver_number"]
    
#             if selected_driver:

#                 positions_df = get_position(driver_num, s_key)

#                 if positions_df.empty:
#                     print("No positions data available for this driver")
            
#                 fig1 = px.scatter(positions_df, x="date", y="position", color="position")

#                 return fig1

# def init_callbacks(app):
#     @app.callback(
#         Output('lap_times', 'figure'),
#         Input('years','value'),
#         Input('circuits', 'value')
#     )(update_lap_graph) 