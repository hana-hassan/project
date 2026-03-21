from urllib.request import urlopen
import json
import pandas as pd
import requests
import plotly.express as px
import datetime as dt

sessions_base = 'https://api.openf1.org/v1/sessions'
meetings_base = 'https://api.openf1.org/v1/meetings'
laps_base = 'https://api.openf1.org/v1/laps'
drivers_base = 'https://api.openf1.org/v1/drivers'
positions_base = 'https://api.openf1.org/v1/position'
stints_base = 'https://api.openf1.org/v1/stints'
grid_base = 'https://api.openf1.org/v1/starting_grid'
result_base = 'https://api.openf1.org/v1/session_result'
weather_base = 'https://api.openf1.org/v1/weather'
control_base = 'https://api.openf1.org/v1/race_control'

# pd.options.display.max_rows = 20

# used one main dataset to create two filtered ones for the predictions section for webpages for 2026 races
# filtered f1 wins dataset no. 1 (used to retrieve the wins of drivers since 2003 in the current 2026 grid)
winners = pd.read_csv('f1_dataset_filtered.csv')

# filtered f1 wins dataset no. 1 (used to retrieve the constructor wins from 2006-2025 at all tracks in the 2026 calendar)
constructor_wins = pd.read_csv('constructor_winners.csv')

# attempt to make a csv file to hold "stats" for races since retrieving info from the API at all times is not reliable
races = pd.read_csv('races_stats.csv')


def get_race(year, circuit):

    params = {
        'year': year, 
        'circuit_short_name' : circuit, 
        'session_type' : 'Race',
        'session_name' : 'Race'
    }

    race_url = requests.Request('GET', sessions_base, params=params).prepare().url
    response_race = requests.get(race_url)
    race_dict = response_race.json()
    if (race_dict == {'detail': 'No results found.'}):
        return pd.DataFrame({})

    race = pd.DataFrame(race_dict)
    # race = pd.DataFrame(response_race.json())

    # session key is a global variable to make filtering the other DataFrames easier
    # global selected_session_key 
    # selected_session_key = race["session_key"].values[0]

    race['date_start'] = pd.to_datetime(race["date_start"], errors='coerce').dt.strftime("%d-%m-%Y %H:%M:%S")

    race['date_end'] = pd.to_datetime(race["date_end"], errors='coerce').dt.strftime("%d-%m-%Y %H:%M:%S")

    return race[['session_key', 'year', 'circuit_short_name', 'date_start', 'date_end']]

def get_meeting(short_name, year):

    params = {
        'circuit_short_name' : short_name,
        'year' : year
    }

    url = requests.Request('GET', meetings_base, params=params).prepare().url
    response = requests.get(url)
    meeting = pd.DataFrame(response.json())

    return meeting[['circuit_short_name','circuit_image', 'circuit_type', 'country_flag', 'location', 'meeting_official_name']]


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


def get_website_info (year, circuit):

    race = get_race(year, circuit)
    name = race["circuit_short_name"]
    #race_dict = race.to_dict("records")

    meeting = get_meeting(name, year)
    #meeting_dict = meeting.to_dict("records")

    merged = pd.merge(race, meeting, on="circuit_short_name")

    info = merged.to_dict("records")

    if (circuit == "Sakhir"):
        return info[1]
    else:
        return info[0]


circuits = {'aus' : 'Melbourne', 'china' : 'Shanghai', 'japan' : 'Suzuka', 'bahrain' : 'Sakhir',
            'saudi' : 'Jeddah', 'miami' : 'Miami', 'imola' : 'Imola', 'monaco' : 'Monte Carlo',
            'spain' : 'Catalunya', 'canada' : 'Montreal', 'austria' : 'Spielberg', 'britain' : 'Silverstone',
            'belgium' : 'Spa-Francorchamps', 'hungary' : 'Hungaroring', 'dutch' : 'Zandvoort', 
            'monza' : 'Monza', 'baku' : 'Baku', 'singapore' : 'Singapore', 'cota' : 'Austin',
            'mexico' : 'Mexico City', 'brazil' : 'Interlagos', 'vegas' : 'Las Vegas', 'qatar' : 'Lusail',
            'abu_dhabi' : 'Yas Marina Circuit', 'madrid' : 'Madring'}

def get_circuit_name (page_name):
    
    return circuits[page_name[:-4]]


def get_page_name(year, circuit):

    season = str(year)

    for key in circuits.keys():
        if circuits.get(key) == circuit:
            return key+season


# FOLLOWING FUNCTIONS ARE USED FOR 2026 RACE PREDICTIONS

# returns the 3 most successful drivers at the track based on past wins
def get_possible_winners(circuit):
    filtered_wins = winners[winners["circuit"] == circuit]

    win_counts = filtered_wins["winner_name"].value_counts()

    winners_dict = win_counts.head(3).to_dict()

    unique_ws = len(win_counts)

    # for x,y in winners_dict.items():
    #     winners_dict[x] = round((y / unique_ws) * 100, 1)

    return (winners_dict)


#create function that returns most successful teams/constructors
def get_team_wins(circuit):
    filtered_wins = constructor_wins[constructor_wins["circuit"] == circuit]

    team_win_counts = filtered_wins["team"].value_counts()

    winners_dict = team_win_counts.head(3).to_dict()

    unique_ws = len(team_win_counts)

    # for x,y in winners_dict.items():
    #     winners_dict[x] = round((y / unique_ws) * 100, 1)

    return (winners_dict)


def get_session_keys(circuit):
    years = ["2023", "2024", "2025"]
    keys = []
    seasons_dict = {}


    for year in years:

        if get_race(year, circuit).empty:
            continue
        else:
            key = get_race(year,circuit)["session_key"].to_list()
            keys.append(key[0])
            seasons_dict[key[0]] = int(year)
            

    # return keys,seasons_dict
    return 0


# returns the probability of the race being a wet race based on the last three races
def is_wet_race(circuit):

    filtered_races = races[races["circuit"] == circuit]

    total_races = len(filtered_races)

    wet_races = filtered_races[filtered_races["wet_race"] == True]

    return len(wet_races), total_races

    # keys = get_session_keys(circuit)[0]
    # seasons_dict = get_session_keys(circuit)[1]
    # wet_races = []
    # # race_num = len(keys)

    # for key in keys:

    #     params = {
    #         "session_key" : key
    #     }

    #     url = requests.Request('GET', stints_base, params=params).prepare().url
    #     response = requests.get(url)
    #     results = pd.DataFrame(response.json())

    #     for x in list(results["compound"]):
    #         if x == "WET" or x == "INTERMEDIATE":
    #             races.loc[(races["circuit"] == circuit) & (races['year'] == seasons_dict.get(key)), "wet_race"] = True
    #             wet_races.append(True)
    #             break

        
    # # return [len(wet_races), race_num]
    # return 0



# print(is_wet_race("Interlagos"))

# returns the probability of a safety car being deployed based on the last three races
def is_safety_car(circuit):

    filtered_races = races[races["circuit"] == circuit]

    total_races = len(filtered_races)

    sc_count = len(filtered_races[filtered_races["safety_car"] == True])

    return sc_count, total_races

    # keys = get_session_keys(circuit)[0]
    # seasons_dict = get_session_keys(circuit)[1]
    # sc_count = 0
    # race_num = len(keys)

    # for key in keys:
    #     params = {
    #         "session_key" : key
    #     }

    #     url = requests.Request('GET', control_base, params=params).prepare().url
    #     response = requests.get(url)
    #     results = pd.DataFrame(response.json())

    #     if results[results["category"] == "SafetyCar"].empty == False:
    #         races.loc[(races["circuit"] == circuit) & (races['year'] == seasons_dict.get(key)), "safety_car"] = True
    #         sc_count += 1

    
    # return [sc_count, race_num]

# print(safety_car_prob("Madring"))
    

# returns the probability of a red flag based on the last three races

def is_red_flag(circuit):

    filtered_races = races[races["circuit"] == circuit]

    total_races = len(filtered_races)

    flag_count = len(filtered_races[filtered_races["red_flag"] == True])

    return flag_count, total_races

    # keys = get_session_keys(circuit)[0]
    # seasons_dict = get_session_keys(circuit)[1]
    # flag_count = 0
    # race_num = len(keys)

    # for key in keys:
        
    #     params = {
    #         "session_key" : key
    #     }

    #     url = requests.Request('GET', control_base, params=params).prepare().url
    #     response = requests.get(url)
    #     results_25 = pd.DataFrame(response.json())

    #     if results_25[results_25["flag"] == "RED"].empty == False:
    #         races.loc[(races["circuit"] == circuit) & (races['year'] == seasons_dict.get(key)), "red_flag"] = True
    #         flag_count += 1


    # # chance = round((flag_count / race_num * 100), 1)

    # return [flag_count, race_num]

# print(is_wet_race("Interlagos"))
# print(is_safety_car("Interlagos"))
# print(is_red_flag("Interlagos"))

# response = urlopen('https://api.openf1.org/v1/sessions?circuit_short_name=Shanghai&session_name=Race&session_name=Race&year=2023')
# data = json.loads(response.read().decode('utf-8'))
# print(pd.DataFrame(data))

# print(get_race("2023", "Shanghai"))

# print(get_page_name(2025, "Melbourne"))

# s_key = get_race("2026", "Melbourne")["session_key"]

# params = {"session_key" : s_key}

# url = requests.Request('GET', result_base, params=params).prepare().url
# response = requests.get(url)
# results = pd.DataFrame(response.json())

# print(results)

# response = urlopen('https://api.openf1.org/v1/meetings?year=2026')
# data = json.loads(response.read().decode('utf-8'))
# results = pd.DataFrame(data)

# print(results["circuit_short_name"])










