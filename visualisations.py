from urllib.request import urlopen
import json # to connect to api
import pandas as pd # for data 
import dash # for web app + visualisations
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# gathers all laps from spa 2023 gp (one driver)
response = urlopen('https://api.openf1.org/v1/laps?session_key=9141&driver_number=16')
data = json.loads(response.read().decode('utf-8'))
df1 = pd.DataFrame(data)
# print (df)

#response_2 = urlopen('https://api.openf1.org/v1/sessions?session_type=Race&session_name=Race')
#data_2 = json.loads(response_2.read().decode('utf-8'))
#df = pd.DataFrame(data_2)
#print(df)

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

fig3 = px.line(df2, x="lap_number", y="lap_duration", color="driver_number", markers=True)
fig3.show()

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# app.layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             html.H1('F1 Data Visualisations')
#         ])
#     ]),

#     dbc.Row([
#         dbc.Col([
#             dbc.Card([
#                 dbc.CardBody([
#                     html.Div([
#                         html.H3("Lap Times"),
#                         dcc.Graph(figure=fig3),

#                     ])
#                 ])
#             ])
#         ])
#     ])
# ])




#if __name__ == "__main__":
#    app.run_server(debug=True)