from urllib.request import urlopen
import json
import pandas as pd
import requests

sessions_base = 'https://api.openf1.org/v1/sessions'
laps_base = 'https://api.openf1.org/v1/laps'
drivers_base = 'https://api.openf1.org/v1/drivers'

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

#df_race = get_race('2024', 'Spa-Francorchamps')

#print(get_laps(df_race["session_key"]))


