import requests
import os
import json
import re
from dotenv import load_dotenv
import rtt_classes

stations = {}

with open("./stations.json") as station_file:
    stations = json.loads(station_file.read())



def station_search(term):

    term = term.strip()
    print(f"Searching for term '{term}'...")

    term = term.lower()

    matches = []
    for code, station in stations.items():
        station_name = station['station_name'][0:-12]
        if term in station_name.lower() or term in code.lower():
            matches.append([station_name, code])
    if len(matches) > 0:
        for match in matches:
            print(f"{match[0].ljust(30, '.')}{match[1]}")
    else:
        print("No matching stations found.")

#load and print upcoming departures
def get_departures(code):
    code = code.strip()
    if len(code)== 3:
        crs_ex = re.compile("^[a-zA-Z][a-zA-Z][a-zA-Z]$") #check code is 3 letters only
        if crs_ex.match(code):
            departures = rtt_classes.Departure_Data(code)

def print_help():
    print(" Help ".center(100, "*"))
    print("[search|s] <search term> ............. Find CRS code of stations matching search term.")
    print("[departures|d|dep|deps] <crs code> ... Get departures for given time.")
    print("[exit|quit|escape|x|q] ............... Close program.")
    print("".center(100, "*"))

print("".center(100,"*"))
print("        Rail Service Info       ".center(100, "*"))
print("                                ".center(100,"*"))
print(" Powered by Realtime Trains API ".center(100, "*"))
print("".center(100,"*"))

print("Enter '?' or 'help' for commands...")



exit = False
empty_loops = 0

while not exit:
    
    input_value = input(">> ")

    if input_value == "":
        if empty_loops < 3:
            empty_loops += 1
        else:
            print_help()
            empty_loops = 0
        continue

    input_list = input_value.split(" ", 1)

    command = input_list[0]
    body = None
    
    if len(input_list) > 1:
        body = input_list[1].strip()


    exit = (command.lower() in ["exit", "q", "x", "quit", "escape"])

    if not exit:

        if command in ["search", "s"]:
            station_search(term = body)
        elif command in ["d", "departures", "dep", "deps"]:
            get_departures(body)
        elif command in ["?", "help"]:
            print_help()
        else:
            print(f"'{command}' is not a recognised command. use '?' or 'help' for a list of commands")

print("Exiting...")



