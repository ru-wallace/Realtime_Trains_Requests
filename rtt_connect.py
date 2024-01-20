import json
from datetime import datetime
from datetime import timedelta
import time
import os
import requests
from dotenv import load_dotenv

class RTT_Requests:
    def __init__(self) -> None:

        load_dotenv()

        username = os.environ.get("USER")
        password = os.environ.get("PASSWORD")

        self.session = requests.Session()
        self.session.auth = (username,password)
    
    def get_services(self, code, arrivals = False, date=None, print_response = False):
        req_string = code
        if date is not None:
            date_str = datetime.strftime(date, "%Y/%m/%d")
            req_string += f"/{date_str}" 
                    
        
        if arrivals:
            req_string += "/arrivals"



        response = self.session.get(f"https://api.rtt.io/api/v1/json/search/{req_string}")
        
        if print_response:
            print("req string: ", req_string)
            print("response: ", response.content)
        response_dict = json.loads(response.content)
        if "error" in response_dict :
            response_dict = None

        
        return response_dict
    
    def get_service_details(self, service):
        req_string = f"{service.uid}/{service.date_str} "
        response = self.session.get(f"https://api.rtt.io/api/v1/json/service/{req_string}")
        details = json.loads(response.content)
        if "error" in details:
            details = None

        return details






  

class Service: 

    def get_time(service):

        time = datetime.now()
        match service.display_as:
            case "ORIGIN":
                time = datetime.strptime(f"{service.date_str}/{service.departure_time}", "%Y/%m/%d/%H%M")
            case "DESTINATION":
                time = datetime.strptime(f"{service.date_str}/{service.arrival_time}", "%Y/%m/%d/%H%M")
            case "CALL":
                time = datetime.strptime(f"{service.date_str}/{service.departure_time}", "%Y/%m/%d/%H%M")
        
        return time


    def __get_stops(self) :

        time = Service.get_time(self)


        req_string = f"{self.uid}/{self.date_str}" 

        session = RTT_Requests()
        
        service_details = session.get_service_details(self)
        #TODO: add error handling
        self.stops_before = []
        self.stops_after= []

        for stop in service_details["locations"]:
            stop_time = 0
            if "gbttBookedDeparture" in stop:
                stop_time = stop["gbttBookedDeparture"]

            if "gbttBookedArrival" in stop:
                stop_time = stop["gbttBookedArrival"]

            stop_time = datetime.strptime(f"{self.date_str}/{stop_time}", "%Y/%m/%d/%H%M")


            if stop_time > time:
                self.stops_after.append(stop["description"])

            if stop_time < time:
                self.stops_before.append(stop["description"])

        self.stops_before = self.stops_before[1:]
   
    def __init__(self, service_json, name, mode) -> None:
        self.mode = mode
        self.location_name = name
        location = service_json["locationDetail"]
        self.uid = service_json["serviceUid"]
        self.display_as = location["displayAs"]
        self.date_str = service_json["runDate"].replace("-","/")
        self.date = datetime.strptime(self.date_str, "%Y/%m/%d")
        self.weekday = datetime.strftime(self.date,  "%A")
        self.origin = location["origin"][0]["description"]
        self.destination = location["destination"][0]["description"]
        self.type = service_json["serviceType"]
        self.operator = service_json["atocName"]
        self.visit_type = "through"
        if self.destination.strip().lower() == self.location_name.strip().lower():
            self.visit_type = "terminating"
        elif self.origin.strip().lower() == self.location_name.strip().lower():
            self.visit_type = "originating"
        
        if self.origin.strip().lower() == self.destination.strip().lower() and self.origin.strip().lower() == self.location_name.strip().lower():
            self.visit_type = "loop"

        if "realtimeDeparture" in location:
            self.departure_time=location["realtimeDeparture"]
        elif "gbttBookedDeparture" in location:
            self.departure_time = location["gbttBookedDeparture"]

        if "realtimeArrival" in location:
            self.arrival_time=location["realtimeArrival"]
        elif "gbttBookedArrival" in location:
            self.arrival_time = location["gbttBookedArrival"]


        self.platform= "TBA"

        if "platform" in location:
            self.platform = location["platform"]


        if self.type != "train" or self.visit_type == "loop":
                self.__get_stops()
        
        if self.type != "train":
            self.platform = self.type.title()

        


           
           

    def print(self):
        match self.display_as:
            case "ORIGIN":
                if self.type == "train":
                    print(f"{self.departure_time} to {self.destination.ljust(30, '.')} | Platform {self.platform.ljust(2)} | {self.operator}")
                else:
                    print(f"{self.departure_time} to {self.destination.ljust(30, '.')} | {self.type.title()} {self.stops_before}, {self.stops_after}")
            case "DESTINATION":
                    if self.type == "train":
                        print(f"{self.arrival_time} from {self.origin.ljust(30, '.')} | Platform {self.platform.ljust(2)} | {self.operator}")
                    else:
                        print(f"{self.arrival_time} from {self.origin.ljust(30, '.')}")
            case "CALL":
                    print(f"{self.departure_time} from {self.origin} to {self.destination} | Platform {self.platform.ljust(2)} | {self.operator}")


class Departures:


    def __init__(self, station_code, num_services=300, services_before=None, test = False) :

        session = RTT_Requests()

        station_code = station_code.strip()

        stations = {}
        with open("./stations.json") as station_file:
            stations = json.loads(station_file.read())


        self.station_name = ""

        if station_code.upper() in stations:
            self.station_name = stations[station_code.upper()]["station_name"][:-12]
        
        self.valid = True        


        self.services = []
        service_uids = []
        date = datetime.now()
        date_string = date.strftime("%Y/%m/%d")

        self.last_date = date

        if services_before is None:
            services_before = date + timedelta(days=50)
        elif services_before < (date + timedelta(days=1)):
            services_before = date + timedelta(days=1)

        
        loop_count = 0
        done = False

        while len(self.services)<= num_services and date <= services_before and not done:
            loop_count += 1
            now = datetime.now()
            date_string = date.strftime("%Y/%m/%d")
            departures = session.get_services(code = station_code, date= date, print_response=test)
            if departures is None:
                print("Invalid Station CRS Code")
                self.valid = False
                return
                
            if departures["services"] is not None:
                for service in departures["services"]:
                    service_obj = Service(service, self.station_name, "departure")
                    if service_obj.display_as in ["ORIGIN", "CALL"]:
                        departure_datetime = datetime.strptime(f"{service_obj.date_str}/{service_obj.departure_time}", "%Y/%m/%d/%H%M")
                        self.last_date = departure_datetime
                        is_in_future = departure_datetime >= now
                        matches_day = service_obj.date_str == date_string

                        if f"{service_obj.uid}_{service_obj.date_str}" not in service_uids and is_in_future and matches_day:
                            self.services.append(service_obj)
                            service_uids.append(f"{service_obj.uid}_{date_string}")
                    else:
                        print(f"API Error: {service_obj.uid} on {service_obj.date_str} is not a Departing service.")

            date = date + timedelta(days=1)  
            time.sleep(1) #wait so as not to overload the api
            if loop_count > 5 :
                print(f"No services found in next {loop_count} days")
                keep_searching = input("Keep searching? ([y]/n)").strip().lower()
                if keep_searching in ["n", "no"]:
                    print("Finished Search")
                    done = True
                loop_count = 0
                    

                
        
        print("\r", end="") #erase loading message


class Arrivals:


    def __init__(self, station_code, num_services=300, services_before = None, test = False) :

        session = RTT_Requests()
        
        station_code = station_code.strip()

        stations = {}
        with open("./stations.json") as station_file:
            stations = json.loads(station_file.read())


        self.station_name = ""

        if station_code.upper() in stations:
            self.station_name = stations[station_code.upper()]["station_name"][:-12]
        
        self.valid = True

        self.services = []
        service_uids = []
        date = datetime.now()
        date_string = date.strftime("%Y/%m/%d")

        self.last_date = date

        if services_before is None:
            services_before = date + timedelta(days=50)
        elif services_before < (date + timedelta(days=1)):
            services_before = date + timedelta(days=1)

        loop_count = 0
        done = False

        while len(self.services)<= num_services and date <= services_before and done == False:
            loop_count += 1
            now = datetime.now()
            date_string = date.strftime("%Y/%m/%d")
            arrivals = session.get_services(code = station_code, date = date, arrivals = True, print_response=test)
            if arrivals is None:
                print("Invalid Station CRS Code")
                self.valid = False
                return
            if arrivals["services"] is not None:
                for service in arrivals["services"]:
                    service_obj = Service(service, self.station_name, "arrival")
                    if service_obj.display_as in ["DESTINATION", "CALL"]:
                        
                        arrival_datetime = datetime.strptime(f"{service_obj.date_str}/{service_obj.arrival_time}", "%Y/%m/%d/%H%M")
                        self.last_date = arrival_datetime
                        is_in_future = arrival_datetime >= now
                        if service_obj.uid not in service_uids and is_in_future:
                            self.services.append(service_obj)
                            service_uids.append(f"{service_obj.uid}_{date_string}")
                    else:
                        print(f"API Error: {service_obj.uid} on {service_obj.date_str} is not an Arriving service.")

            date = date + timedelta(days=1)
            print("Number of Services: ", len(self.services))

            if loop_count > 5 and len(self.services) == 0:
                print(f"No services found in next {loop_count} days")
                keep_searching = input("Keep searching? ([y]/n)").strip().lower()
                if keep_searching in ["n", "no"]:
                    print("Finished Search")
                    done = True
                loop_count = 0

            time.sleep(1) #wait so as not to overload the api
        
        print("\r", end="") #erase loading message



