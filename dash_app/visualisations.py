from urllib.request import urlopen
import json # to connect to api
import pandas as pd # for data 
#import dash # for web app + visualisations
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import g
import requests
import plotly.io as pio
from data_filtering import get_laps, get_position, get_race, get_drivers, get_all_positions, get_stints, get_quali, get_starting_grid, get_results
base_url_sessions = "https://api.openf1.org/v1/sessions"
base_url_drivers = "https://api.openf1.org/v1/drivers"

response = urlopen(base_url_sessions)
data = json.loads(response.read().decode('utf-8'))
df = pd.DataFrame(data)

response2 = urlopen(base_url_drivers)
data2 = json.loads(response2.read().decode('utf-8'))
df2 = pd.DataFrame(data2)


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

        # row for dropdowns - here the user selects a year and circuit so that all other visualisation can display the appropriate data
        dbc.Row([
            dbc.Col([
                html.H2('Select a year: '),
                dcc.Dropdown(className = 'dropdowns', id="years", options = [{'label': year, 'value': year} for year in df["year"].unique()], 
                             value = 2023, 
                             placeholder="Select a year"),
            ]),
            dbc.Col([
                html.H2('Select a circuit: '),
                dcc.Dropdown(className = 'dropdowns', id="circuits", options = [{'label': circuit_short_name, 'value': circuit_short_name} for circuit_short_name in df["circuit_short_name"].unique()],
                             value="Spa-Francorchamps",
                             placeholder="Select a circuit")
            ])
        ]),

        #section for lap time data vis

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("Lap Times"),
                            dcc.Graph(id="lap_times_hist"),
                            dcc.Graph(className="graphs", id="lap_times"),
                        ],  className="vis_div" )
                    ])
                ])
            ])
        ]),

        # section/div for the stints data vis

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Dropdown(className = 'dropdowns', id="drivers", options = [{'label': full_name, 'value': full_name} for full_name in df2["full_name"].unique()], 
                            value="Lewis HAMILTON", 
                            placeholder="Select a driver"),
                        html.Div([
                            html.H2("Race Stints"),
                            dcc.Graph(id="stints_tyres"),
                        ], className="vis_div")
                    ])
                ])
            ])
        ]),

        # section for the sector times data vis

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("Sector Times"),
                            dcc.Graph(id="sector_times"),
                        ], className="vis_div")
                    ])
                ])
            ])
        ]),

        # section for the positions data vis
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("Qualifications and Race Results"),
                            dcc.Graph(id="positions_graph"),
                        ], className="vis_div")
                    ])
                ])
            ])
        ])
    ])

    #init_callbacks(app)
    return app.server
 
@callback(
    Output('lap_times_hist', 'figure'),
    Output('lap_times', 'figure'),
    Output('positions_graph', 'figure'),
    Output('sector_times', 'figure'),
    Output('stints_tyres', 'figure'),
    Input('years','value'), 
    Input('circuits', 'value'),
    Input('drivers', 'value'),
    #Input('drivers_sector', 'value'),
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

    pio.templates.default = "plotly_dark"

    # histogram for lap times
    fig_hist = px.histogram(all_laps, x="lap_duration", labels = {"lap_duration" : "Lap Duration (seconds)"},title="Distribution of Lap Times")

    fig_hist.update_layout(
        font_family="monospace",
        font_size=15,
        title_font_size=20,
        height=450
    )

    fig =  px.line(all_laps, x="lap_number", y="lap_duration", color="driver_number", markers=True, 
    labels = {"lap_number" : "Lap Number", 
              "lap_duration" : "Lap Duration (seconds)",
              "driver_number" : "Driver Number"},
    title="Driver Lap Times"
    )

    fig.update_xaxes(rangeslider_visible = True)
    fig.update_layout(
        font_family="monospace",
        font_size=15,
        title_font_size=20,
        height=1000
    )

    quali = get_quali(selected_year, selected_circuit)

    q_key = quali["session_key"]

    results = get_results(s_key, q_key)

    # vis for positions lost/gained
    
    fig_results = px.bar(results, x="driver_number", y="pos_difference", color="pos_difference", color_continuous_scale="RdBu", labels={"driver_number" : "Driver", "pos_difference" : "Positions Lost/Gained"}, 
                         title="Positions Lost/Gained", text_auto=".2s")
    fig_results.update_xaxes(type='category')
    fig_results.update_layout(
        font_family="monospace",
        font_size=15,
        title_font_size=20,
        height=700
    )

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
                    color="white"
                ),
            ),

            go.Scatter(
                x=st_data["stint_start"],
                y=stints,
                mode="markers",
                marker=dict(
                    color="green",
                    size=10
                ),
                name="Start of stint"
            ),

            go.Scatter(
                x=st_data["stint_end"],
                y=stints,
                mode="markers",
                marker=dict(
                    color="red",
                    size=10,
                ),
                name="End of stint"
            ),

        ]
    )

    fig2.update_layout(
        title=dict(
            text="Stint Lengths"
        ),

        xaxis=dict(
            title=dict(
                text="Lap Number"
            )
        ),

        yaxis=dict(
            title=dict(
                text="Stints"
            )
        ),
        
        font_family="monospace",
        font_size=15,
        title_font_size=20,
        height=500
    )

    # density histogram/heatmap for sector times

    fig_sectors = make_subplots(rows=3, cols=1, shared_xaxes=True, horizontal_spacing=0.1 , specs = [[{}], [{}], [{}]], subplot_titles = ("Sector 1", "Sector 2", "Sector 3"), y_title="Sector Time (seconds)", x_title="Lap Number")
    
    fig_sectors.add_trace(go.Histogram2dContour(x=all_laps["lap_number"], y = all_laps["duration_sector_1"], autobinx=False, xbins= dict(start=all_laps["lap_number"].min(), end=all_laps["lap_number"].max(), size=1), autobiny=False, ybins= dict(start=(all_laps["duration_sector_1"].min() - 15), end=all_laps["duration_sector_1"].max(), size=5),
                                                 coloraxis="coloraxis", name="Sector 1", hovertemplate="Lap: %{x} <br>Sector Duration: %{y} <br>Count: %{z}"), 
                                                 row=1, col=1
    )

    fig_sectors.add_trace(go.Histogram2dContour(x=all_laps["lap_number"], y = all_laps["duration_sector_2"], autobinx=False, xbins= dict(start=all_laps["lap_number"].min(), end=all_laps["lap_number"].max(), size=1), autobiny=False, ybins= dict(start=(all_laps["duration_sector_2"].min() - 15), end=all_laps["duration_sector_2"].max(), size=5), 
                                                coloraxis="coloraxis", name="Sector 2", hovertemplate="Lap: %{x} <br>Sector Duration: %{y} <br>Count: %{z}"), 
                                                row=2, col=1
    )

    fig_sectors.add_trace(go.Histogram2dContour(x=all_laps["lap_number"], y = all_laps["duration_sector_3"], autobinx=False, xbins= dict(start=all_laps["lap_number"].min(), end=all_laps["lap_number"].max(), size=1), autobiny=False, ybins= dict(start=(all_laps["duration_sector_3"].min() - 15), end=all_laps["duration_sector_3"].max(), size=5), 
                                                coloraxis="coloraxis", name="Sector 3", hovertemplate="Lap: %{x} <br>Sector Duration: %{y} <br>Count: %{z}"), 
                                                row=3, col=1
    )

    fig_sectors.update_layout(
        height = 1500, 
        coloraxis = dict(colorscale = 'Viridis'), 
        title = "Race Sector Times",
        hoversubplots = "axis",
        hovermode = "x",
        font_family="monospace",
        font_size=15,
        title_font_size=20
        )


    return fig_hist, fig, fig_results, fig2, fig_sectors

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