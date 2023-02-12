# Texas Branch

import pandas as pd
import numpy as np
import json
from geopy.geocoders import Nominatim
import os
geolocator = Nominatim(user_agent="nrpgroup")

# file_name "bexar-addresses-county.geojson"
file_name = input("Geojson Filename (bexar-addresses-county.geojson): ").lower()

# San Antonio
city_name = input("City Name (San Antonio): ").title()

print("Loading and formatting data...\n\n")

if not os.path.exists(f"geojson/{file_name}"):
    print("Error: File not found. Please make sure the file is in the geojson folder and is named correctly.\n")
    raise FileNotFoundError()

out_file_name = f"{''.join(file_name.split('.')[:-1])}-formatted.geojson"

if not os.path.exists(f"geojson/{out_file_name}"):
    with open(f"geojson/{file_name}", 'r') as f:
        file_lines = [''.join([x.strip(), ',', '\n']) for x in f.readlines()]

    with open(f"geojson/{out_file_name}", 'w') as f:
        file_lines[-1] = file_lines[-1][:-2]
        f.write('[\n')
        f.writelines(file_lines)
        f.write('\n]')
else:
    print("Found formatted file. Skipping formatting step.\n\n")

with open(f"geojson/{out_file_name}") as f:
    data = json.load(f)

street_numbers = [int(i['properties']['number']) for i in data]
street_name = [i['properties']['street'] for i in data]
postcode = [i['properties']['postcode'] for i in data]
longitude = [i['geometry']['coordinates'][0] for i in data]
latitude = [i['geometry']['coordinates'][1] for i in data]

addresses = pd.DataFrame({'street_numbers': street_numbers, 'street_name': street_name, 'postcode': postcode, 'longitude': longitude, 'latitude': latitude})
addresses["full_address"] = addresses["street_numbers"].map(str) + " " + addresses["street_name"] + f", {city_name}, TX " + addresses["postcode"]

# address should be in the format of "1234 Main St, San Antonio, TX 78201"
miles_per_degree_lat = 68.93939393939394
miles_per_degree_lon = 54.5985401459854

def get_closest_addresses(address: str, df: pd.DataFrame, max_radius = 5, max_results = 100):
    address = address + f", {city_name}"
    
    try:
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
    except AttributeError:
        print("Error: Address not found.\n")
        return
    
    distance = np.sqrt(((df["latitude"] - lat)*miles_per_degree_lat)**2 + ((df["longitude"] - lon)*miles_per_degree_lon)**2)
    distance.sort_values(inplace=True)
    candidates = distance[distance <= max_radius]
    
    indicies = None
    if len(candidates) > max_results:
        indices = candidates[:max_results].index
    else:
        indices = candidates.index

    df.loc[indices].to_csv(f"results/closest_addresses_to_{address}.csv", index=False)
    print(f"Saved results to results/closest_addresses_to_{address}.csv\n")

max_rad = input("What is the maximum radius you would like to search in miles? (default: 5): ")
max_res = input("What is the maximum results you would like to return? (default: 100): ")

if not max_rad:
    max_rad = 5

if not max_res:
    max_res = 100

while True:
    addr = input("What address would you like to find the closest addresses to?\nFormat: 1234 Main St\nInput (press ctrl+c to exit): ")
    get_closest_addresses(addr, addresses, max_radius = max_rad, max_results = max_res)

