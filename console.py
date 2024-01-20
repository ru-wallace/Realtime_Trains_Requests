import json
import re
import rtt_connect

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


def print_services(service_list):
    
    service_list = sorted(service_list, key=rtt_connect.Service.get_time)
    print(f'|{f"  {service_list[0].location_name}  ".center(100, "#")}|')
    date = ""
    for service in service_list:
        if service.date_str != date:
            print("------------------------------------------------------------------------------------------------------\n")
            print(f" {service.weekday.title()} {service.date_str} ".center(102, "-"))
            print("| Service | Platform | Origin                        | Arr.  | Destination                   | Dep.  |")
            print("|----------------------------------------------------------------------------------------------------|")
            date = service.date_str

        service_str = "placeholder"
        match service.display_as:
            case "ORIGIN":
                service_str = (f"| {service.uid.ljust(8)}| { service.platform.ljust(9)}|                               |       | {service.destination.ljust(30)}| {service.departure_time.ljust(6)}|")
            case "DESTINATION":
                service_str = (f"| {service.uid.ljust(8)}| {service.platform.ljust(9)}| {service.origin.ljust(30)}| {service.arrival_time.ljust(6)}|                               |       |")
            case "CALL":
                service_str = (f"| {service.uid.ljust(8)}| {service.platform.ljust(9)}| {service.origin.ljust(30)}| {service.arrival_time.ljust(6)}| {service.destination.ljust(30)}| {service.departure_time.ljust(6)}|")

        def truncate_stops(stop_list):
            stop_str = stop_list[0]
            for stop in stop_list[1:]:
                if len(", " + stop_str + stop) < 25:
                    stop_str = stop_str + ", " + stop
                else: 
                    stop_str += " (...)"
                    break
            
            stop_str = stop_str.ljust(30)
            return stop_str

        if service.visit_type == "loop":
            time_str = ""
            match service.display_as:
                case "ORIGIN":
                    time_str = service.departure_time
                    service_str = (f"| {service.uid.ljust(8)}| {service.platform.title().ljust(9)}|                               |       | {truncate_stops(service.stops_after)}| {time_str.ljust(6)}|")
                case "DESTINATION":
                    time_str = service.arrival_time
                    service_str = (f"| {service.uid.ljust(8)}| {service.platform.title().ljust(9)}| {truncate_stops(service.stops_before)}| {time_str.ljust(6)}|                               |       | ")
                case "CALL": 
                    time_str = service.departure_time
                    service_str = (f"| {service.uid.ljust(8)}| {service.platform.title().ljust(9)}| {truncate_stops(service.stops_before)}| {service.arrival_time.ljust(6)}| {truncate_stops(service.stops_after)}| {service.departure_time.ljust(6)}| ")
            

        print(service_str)
    print("------------------------------------------------------------------------------------------------------\n")  


#load and print upcoming departures
def get_departures(code, test=False):
    crs_ex = re.compile("^[a-zA-Z][a-zA-Z][a-zA-Z]$") #check code is 3 letters only
    code = code.strip()
    if crs_ex.match(code):
        if code.upper() in stations:
            print(f"{code.upper()}: {stations[code.upper()]["station_name"][:-12]}")
        print("Getting departing services...")
        departures = rtt_connect.Departures(code, num_services=10, test=test)
        if departures.valid:
            print_services(departures.services)
        else:
            if code.upper() in stations:
                print(f"{code.upper()}: {stations[code.upper()]["station_name"][:-12]}")
            print(f"No Services Found")
    else:
        print("Invalid Station CRS Code - use search to find stations")


#load and print upcoming arrivals
def get_arrivals(code, test = False): 
    crs_ex = re.compile("^[a-zA-Z][a-zA-Z][a-zA-Z]$") #check code is 3 letters only
    code = code.strip()
    if crs_ex.match(code):

        if code.upper() in stations:
            print(f"{code.upper()}: {stations[code.upper()]["station_name"][:-12]}")
        print("Getting arriving services...")

        arrivals = rtt_connect.Arrivals(code, num_services=10, test=test)
        if arrivals.valid:
            print_services(arrivals.services)
        else:
            if code.upper() in stations:
                print(f"{code.upper()}: {stations[code.upper()]["station_name"][:-12]}")
                print(f"No Services Found")
    else:
        print("Invalid Station CRS Code - use search to find stations")

def get_all_services(code, test=False):
    crs_ex = re.compile("^[a-zA-Z][a-zA-Z][a-zA-Z]$") #check code is 3 letters only
    code = code.strip()
    if crs_ex.match(code):
        if code.upper() in stations:
            print(f"{code.upper()}: {stations[code.upper()]["station_name"][:-12]}")
        print("Getting all services...")

        arrivals = []
        departures = []

        arrivals = rtt_connect.Arrivals(code, num_services=10, test=test)
         
        departures = rtt_connect.Departures(code, services_before=arrivals.last_date, test=test)
        uid_list = []
        service_list = []
        for service in arrivals.services:
            uid_list.append(service.uid)
            service_list.append(service)

        for service in departures.services:
            if service.display_as == "ORIGIN":
                uid_list.append(service.uid)
                service_list.append(service)
        
        print_services(service_list)
    else:
        print("Invalid Station CRS Code - use search to find stations")


def print_help():
    print(" Help ".center(100, "*"))
    print("[search|s] <search term> ".ljust(50, "."), " Find CRS code of stations matching search term.")
    print("[arrivals|a|arr|arrs] <crs code> ".ljust(50, "."), "Get arriving services for given station.")
    print("[departures|d|dep|deps] <crs code> ".ljust(50, "."),  "Get departing services for given station.")
    print("[all|ad|ads|arrdep|arrsdeps|a+d] <crs code> ".ljust(50, "."), "Get all services for given station") 
    print("[exit|quit|escape|x|q] " .ljust(50, "."),  "Close program.")
    print("[?|help ]".ljust(50, "."), " View help information")
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
    
    input_value = input(">> ").strip()

    if input_value == "":
        if empty_loops < 3:
            empty_loops += 1
        else:
            print_help()
            empty_loops = 0
        continue

    input_list = input_value.split(" ", 1)

    command = input_list[0]
    term = None
    test = False
    
    if len(input_list) > 1:
        body = input_list[1].strip().rsplit(" ", 1)
        term = body[0]
        if "-t" in body:
            test = True



    exit = (command.lower() in ["exit", "q", "x", "quit", "escape"])
    #TODO: Add arguments
    #TODO: change file names
    if not exit:

        if command in ["search", "s"]:
            station_search(term = term)
        elif command in ["d", "departures", "dep", "deps"]:
            get_departures(term, test=test)
        elif command in ["a", "arrivals", "arr"]:
            get_arrivals(term, test=test)
        elif command in ["ad", "da", "all"]:
            get_all_services(term, test=test)
        elif command in ["?", "help"]:
            print_help()            
        else:
            print(f"'{command}' is not a recognised command. use '?' or 'help' for a list of commands")

print("Exiting...")



