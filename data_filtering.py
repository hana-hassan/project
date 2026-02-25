from urllib.request import urlopen
import json
import pandas as pd
import requests
import plotly.express as px
import datetime as dt

sessions_base = 'https://api.openf1.org/v1/sessions'
laps_base = 'https://api.openf1.org/v1/laps'
drivers_base = 'https://api.openf1.org/v1/drivers'
positions_base = 'https://api.openf1.org/v1/position'
stints_base = 'https://api.openf1.org/v1/stints'
grid_base = 'https://api.openf1.org/v1/starting_grid'
result_base = 'https://api.openf1.org/v1/session_result'

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

    all_laps.sort_values(by=["lap_number"])
    all_laps.drop_duplicates(subset=["driver_number", "lap_number"], inplace = True)

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

    all_positions = all_positions.sort_values(by=["date"])

    all_positions["date"] = pd.to_datetime(all_positions["date"], errors='coerce').dt.strftime("%H:%M")

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

def get_quali(year, circuit):

    params = {
        'year' : year,
        'circuit_short_name' : circuit,
        'session_type' : 'Qualifying',
        'session_name' : 'Qualifying'
    }

    url = requests.Request('GET', sessions_base, params=params).prepare().url
    response = requests.get(url)
    quali = pd.DataFrame(response.json())

    return quali[['session_key', 'year', 'circuit_short_name']]



def get_starting_grid(session_key):
    
    params = {
        'session_key' : session_key,
    }

    url = requests.Request('GET', grid_base, params=params).prepare().url
    response = requests.get(url)
    grid = pd.DataFrame(response.json())

    #return grid[["driver_number", "position"]]
    return grid


def get_results(session_key, quali_key):

    params = {
        'session_key' : session_key
    }

    url = requests.Request('GET', result_base, params=params).prepare().url
    response = requests.get(url)
    results = pd.DataFrame(response.json())

    grid_df = get_starting_grid(quali_key)

    results.rename(columns={"position" : "final_position"}, inplace=True)

    results_df = pd.merge(results, grid_df, on="driver_number")

    # results_df.drop(results_df[results_df["dnf"] == True], inplace=True)
    # results_df.drop(results_df[results_df["dns"] == True], inplace=True)
    # results_df.drop(results_df[results_df["dsq"] == True], inplace=True)

    results_df.dropna(subset=["final_position"], inplace=True)

    results_df["pos_difference"] = results_df["position"] - results_df["final_position"]

    return results_df[["driver_number", "position", "final_position", "pos_difference"]]
    #return results

    

df_race = get_race('2024', 'Silverstone')

key = (df_race["session_key"])

df_drivers = get_drivers(key)

driver_num = df_drivers.loc[df_drivers["full_name"] == "Lewis HAMILTON", "driver_number"]

# df_quali = get_quali('2024', 'Silverstone')

# q_key = df_quali["session_key"]

# print(q_key)

# grid = get_starting_grid(q_key)

# print(grid)



# response = urlopen("https://api.openf1.org/v1/starting_grid?session_key=9558")
# data = json.loads(response.read().decode('utf-8'))
# print(pd.DataFrame(data))

# df_results = get_results(key, q_key)

# print(df_results)

# df_grid = get_starting_grid(other_key)
# print(df_grid)
#all_pos = get_all_positions(key)
#print(all_pos)
#all_laps = get_laps(key)
#print(all_laps["duration_sector_1"].min())
#all_laps.sort_values(by=["lap_number"])
#print(all_laps["lap_number"])

# df_position["date"] = pd.to_datetime(df_position["date"], errors='coerce')

# df_position["date"] = df_position["date"].dt.strftime("%H:%M")

# all_pos = all_pos.sort_values(by=["date"])
# print(all_pos["date"])

# position_graph = px.scatter(df_positions, x="date", y="position", color="position")

# position_graph.show()

#print(df_positions)


#print (get_position('lewis HAMILTON', key))


