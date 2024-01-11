import json
from datetime import datetime
from datetime import timedelta
import time
import os
import requests
from dotenv import load_dotenv

class RTT_Session:
    def __init__(self) -> None:

        load_dotenv()

        username = os.environ.get("USER")
        password = os.environ.get("PASSWORD")

        self.session = requests.Session()

        self.session.auth = (username,password)




class Service:
    def __init__(self, uid, date):

        print("ID ", uid)
        print("Date: ", date)
        
        self.uid = uid

        self.stops = {}

        session = RTT_Session().session
        response = session(f"https://api.rtt.io/api/v1/json/service/{uid}/{date}")
        data = json.loads(response.content)

        #print(json.dumps(data, indent=2))
        for stop in data["locations"]:
            print(stop)
            if "platform" in stop and "realtimeDeparture" in stop : 
                print("Has platform and departure")
                self.stops.update({stop["crs"]:
                                        {"departure": stop["realtimeDeparture"],
                                        "platform": stop["platform"]}})
                
    def print(self):
       print(f"UID: {self.uid}")
       print(json.dumps(self.stops, indent=2))
  

class Station_Service: 

    def get_time(service):

        time = datetime.now()
        match service.display_as:
            case "ORIGIN":
                time = datetime.strptime(f"{service.date}/{service.departure_time}", "%Y/%m/%d/%H%M")
            case "DESTINATION":
                time = datetime.strptime(f"{service.date}/{service.arrival_time}", "%Y/%m/%d/%H%M")
            case "CALL":
                time = datetime.strptime(f"{service.date}/{service.departure_time}", "%Y/%m/%d/%H%M")
        
        return time


    def __get_stops(self) :

        time = Station_Service.get_time(self)


        req_string = f"{self.uid}/{self.date}" 

        session = RTT_Session().session
        
        response = session.get(f"https://api.rtt.io/api/v1/json/service/{req_string}")

        stops_json = json.loads(response.content)
        self.stops_before = []
        self.stops_after= []
        for stop in stops_json["locations"]:
            stop_time = 0
            if "gbttBookedDeparture" in stop:
                stop_time = stop["gbttBookedDeparture"]

            if "gbttBookedArrival" in stop:
                stop_time = stop["gbttBookedArrival"]

            stop_time = datetime.strptime(f"{self.date}/{stop_time}", "%Y/%m/%d/%H%M")


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
        self.date = service_json["runDate"].replace("-","/")
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
        if self.mode == "departure":
            if self.type == "train":
                print(f"{self.departure_time} to {self.destination.ljust(30, '.')} | Platform {self.platform.ljust(2)} | {self.operator}")
            else:
                print(f"{self.departure_time} to {self.destination.ljust(30, '.')} | {self.type.title()} {self.stops}")
        elif self.mode == "arrival":
            if self.type == "train":
                print(f"{self.arrival_time} from {self.origin.ljust(30, '.')} | Platform {self.platform.ljust(2)} | {self.operator}")
            else:
                print(f"{self.arrival_time} from {self.origin.ljust(30, '.')}")


class Departures:

    def __get_departures(self, code, date = False) :

        


        req_string = code
        if date != False:
            req_string = f"{code}/{date}" 

        session = RTT_Session().session
        response = session.get(f"https://api.rtt.io/api/v1/json/search/{req_string}")
        response_dict = json.loads(response.content)
        if "error" in response_dict :
            response_dict = None
        return response_dict

    

    def __init__(self, station_code) :
        
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


        
        while len(self.services)<= 10:

            now = datetime.now()
            date_string = date.strftime("%Y/%m/%d")
            departures = self.__get_departures(station_code, date_string)
            if departures is None:
                print("Invalid Station CRS Code")
                self.valid = False
                return
                
            if departures["services"] is not None:
                for service in departures["services"]:
                    service_obj = Station_Service(service, self.station_name, "departure")
                    departure_datetime = datetime.strptime(f"{service_obj.date}/{service_obj.departure_time}", "%Y/%m/%d/%H%M")
                    is_in_future = departure_datetime >= now
                    if service_obj.uid not in service_uids and is_in_future:
                        self.services.append(service_obj)
                        service_uids.append(f"{service_obj.uid}_{date_string}")

            date = date + timedelta(days=1)  
            time.sleep(1) #wait so as not to overload the api
        
        print("\r", end="") #erase loading message


class Arrivals:

    def __get_arrivals(self, code, date = False) :


        req_string = code
        if date != False:
            req_string = f"{code}/{date}" 

        session = RTT_Session().session
        response = session.get(f"https://api.rtt.io/api/v1/json/search/{req_string}/arrivals")

        response_dict = json.loads(response.content)
        if "error" in response_dict :
            response_dict = None
        return response_dict
    

    def __init__(self, station_code) :
        
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
        current_time = date.strftime("%H%M")
        today = datetime.now()


        
        while len(self.services)<= 10:

            now = datetime.now()
            date_string = date.strftime("%Y/%m/%d")
            arrivals = self.__get_arrivals(station_code, date_string)
            if arrivals is None:
                print("Invalid Station CRS Code")
                self.valid = False
                return
            if arrivals["services"] is not None:
                for service in arrivals["services"]:
                    service_obj = Station_Service(service, self.station_name, "arrival")
                    arrival_datetime = datetime.strptime(f"{service_obj.date}/{service_obj.arrival_time}", "%Y/%m/%d/%H%M")
                    is_in_future = arrival_datetime >= now
                    if service_obj.uid not in service_uids and is_in_future:
                        self.services.append(service_obj)
                        service_uids.append(f"{service_obj.uid}_{date_string}")

            date = date + timedelta(days=1)  
            time.sleep(1) #wait so as not to overload the api
        
        print("\r", end="") #erase loading message



