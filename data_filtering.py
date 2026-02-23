from urllib.request import urlopen
import json
import pandas as pd
import requests
import plotly.express as px

sessions_base = 'https://api.openf1.org/v1/sessions'
laps_base = 'https://api.openf1.org/v1/laps'
drivers_base = 'https://api.openf1.org/v1/drivers'
positions_base = 'https://api.openf1.org/v1/position'
stints_base = 'https://api.openf1.org/v1/stints'

# response = requests.get(sessions_url, params = params)
# data = json.loads(response.json())
# df = pd.DataFrame(data)

def get_race(year, circuit):

    params = {
        'year': year, 
        'circuit_short_name' : circuit, 
        'session_type' : 'Race'
    }

    race_url = requests.Request('GET', sessions_base, params=params).prepare().url
    response_race = requests.get(race_url)
    race = pd.DataFrame(response_race.json())

    # session key is a global variable to make filtering the other DataFrames easier
    # global selected_session_key 
    # selected_session_key = race["session_key"].values[0]

    return race[['session_key', 'year', 'circuit_short_name']]

def get_laps(session_key):

    params = {
        'session_key' : session_key
    }

    laps_url = requests.Request('GET', laps_base, params=params).prepare().url
    response_laps = requests.get(laps_url)
    all_laps = pd.DataFrame(response_laps.json())

    return all_laps

def get_drivers(session_key):

    params = {
        'session_key' : session_key
    }

    drivers_url = requests.Request('GET', drivers_base, params=params).prepare().url
    response_drivers = requests.get(drivers_url)
    all_drivers = pd.DataFrame(response_drivers.json())

    return all_drivers

def get_position(driver_num, session_key):

    params = {
        'driver_number' : driver_num,
        'session_key' : session_key
    }

    url = requests.Request('GET', positions_base, params=params).prepare().url
    response = requests.get(url)
    all_positions = pd.DataFrame(response.json())

    return all_positions

def get_all_positions(session_key):

    params = {
        'session_key' : session_key
    }

    url = requests.Request('GET', positions_base, params=params).prepare().url
    response = requests.get(url)
    all_positions = pd.DataFrame(response.json())

    return all_positions[['date', 'driver_number', 'position']]

def get_stints(driver_num, session_key):

    params = {
        'driver_number' : driver_num,
        'session_key' : session_key
    }

    url = requests.Request('GET', stints_base, params=params).prepare().url
    response = requests.get(url)
    dr_stints = pd.DataFrame(response.json())

    dr_stints["tyre_age_at_end"] = dr_stints["tyre_age_at_start"] + (dr_stints["lap_end"] - dr_stints["lap_start"])

    return dr_stints

df_race = get_race('2024', 'Silverstone')

key = (df_race["session_key"])

df_drivers = get_drivers(key)

driver_num = df_drivers.loc[df_drivers["full_name"] == "Lewis HAMILTON", "driver_number"]

df_stints = get_stints(driver_num, key)

print(df_stints)


# position_graph = px.scatter(df_positions, x="date", y="position", color="position")

# position_graph.show()

#print(df_positions)


#print (get_position('lewis HAMILTON', key))


