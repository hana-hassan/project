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

pd.options.display.max_rows = 20

# filtered f1 winners dataset for predictions section for webpages for 2026 races
winners = pd.read_csv('f1_dataset_filtered.csv')


# response = requests.get(sessions_url, params = params)
# data = json.loads(response.json())
# df = pd.DataFrame(data)

def get_race(year, circuit):

    params = {
        'year': year, 
        'circuit_short_name' : circuit, 
        'session_type' : 'Race',
        'session_name' : 'Race'
    }

    race_url = requests.Request('GET', sessions_base, params=params).prepare().url
    response_race = requests.get(race_url)
    race = pd.DataFrame(response_race.json())

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
            'abu_dhabi' : 'Yas Marina Circuit'}

def get_circuit_name (page_name):
    
    return circuits[page_name[:-4]]


def get_page_name(year, circuit):

    season = str(year)

    for key in circuits.keys():
        if circuits.get(key) == circuit:
            return key+season


def get_possible_winners(circuit):
    filtered_wins = winners[winners["circuit"] == circuit]

    win_counts = filtered_wins["winner_name"].value_counts()

    winners_dict = win_counts.head(3).to_dict()

    unique_ws = len(win_counts)

    for x,y in winners_dict.items():
        winners_dict[x] = round((y / unique_ws) * 100, 1)

    return (winners_dict)


# for some reason comes with an error when 'Shanghai' is passed through? please fix

def is_wet_race(circuit):

    race_25 = get_race("2025", circuit)
    race_24 = get_race("2024", circuit)
    race_23 = get_race("2023", circuit)

    wet_races = []
    race_num = 0
    

    if race_25.empty == False:

        params = {
            "session_key" : race_25['session_key']
        }

        url = requests.Request('GET', weather_base, params=params).prepare().url
        response = requests.get(url)
        results_25 = pd.DataFrame(response.json())

        for x in list(results_25["rainfall"].to_dict().values()):
            if x == 1:
                wet_races.append(True)
                break

        race_num += 1


    if race_24.empty == False:

        params_2 = {
            "session_key" : race_24['session_key']
        }

        url_2 = requests.Request('GET', weather_base, params=params_2).prepare().url
        response_2 = requests.get(url_2)
        results_24 = pd.DataFrame(response_2.json())

        for x in list(results_24["rainfall"].to_dict().values()):
            if x == 1:
                wet_races.append(True)
                break
                
        race_num += 1

    
    if race_23.empty == False:

        params_3 = {
            "session_key" : race_23['session_key']
        }

        url_3 = requests.Request('GET', weather_base, params=params_3).prepare().url
        response_3 = requests.get(url_3)
        results_23 = pd.DataFrame(response_3.json())

        for x in list(results_23["rainfall"].to_dict().values()):
            if x == 1:
                wet_races.append(True)
                break
        
        race_num += 1

    
    return len(wet_races), race_num



# print(is_wet_race("Interlagos"))

# print(get_website_info("2025", "Sakhir"))

# print(get_page_name(2025, "Melbourne"))

s_key = get_race("2026", "Melbourne")["session_key"]

# params = {"session_key" : s_key}

# url = requests.Request('GET', result_base, params=params).prepare().url
# response = requests.get(url)
# results = pd.DataFrame(response.json())

# print(results)

# response = urlopen('https://api.openf1.org/v1/meetings?year=2026')
# data = json.loads(response.read().decode('utf-8'))
# results = pd.DataFrame(data)

# print(results["circuit_short_name"])








