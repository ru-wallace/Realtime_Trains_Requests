import requests
import os
import json

from dotenv import load_dotenv
import rtt_classes

stations = {}

with open("./stations.json") as station_file:
    stations = json.loads(station_file.read())



def station_search(term = None):
    if term == None:
        term = input("Search for Station Name or Code: ")

    term = term.strip()
    print(f"Searching for term \"{term}\"")

    term = term.lower()
    for code, station in stations.items():
        if term in station["station_name"].lower() or term in code.lower():
            print(f"{station['station_name'][0:-12].ljust(30, '.')}{code}")

station_search()

exit = False

while not exit:
    station_code = input("Station CRS Code: ")
    exit = (station_code.lower() in ["/exit", "/q", "/x"])
    if not exit:

        if station_code[0:2] == "/s":
 
            station_search(term = station_code[3:])
        else:
            departures = rtt_classes.Departure_Data(station_code.upper())

print("Exiting...")

#response_json = json.loads(response.content)


