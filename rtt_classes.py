import json
from datetime import datetime
from datetime import timedelta
import time
import os
import requests
from dotenv import load_dotenv

class Service:
    def __init__(self, uid, date):

        print("ID ", uid)
        print("Date: ", date)
        load_dotenv("./environment/.env")
        self.uid = uid
        username = os.environ.get("USER")
        password = os.environ.get("PASSWORD")

        session = requests.Session()

        session.auth = (username,password)
        self.stops = {}
        response = session.get(f"https://api.rtt.io/api/v1/json/service/{uid}/{date}")
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
    def __get_stops(self, uid, date = False) :

        req_string = uid
        if date != False:
            req_string = f"{uid}/{date}" 

        load_dotenv("./environment/.env")

        username = os.environ.get("USER")
        password = os.environ.get("PASSWORD")

        session = requests.Session()
        
        session.auth = (username,password)
        response = session.get(f"https://api.rtt.io/api/v1/json/service/{req_string}")

        stops_json = json.loads(response.content)
        stops = []
        for stop in stops_json["locations"]:
            stops.append(stop["description"])

        if len(stops) > 2:
            stops_str = ", ".join(stops[1:len(stops)-1])
            stops_str = f"via {stops_str}" #TODO: Only show stops after current stop
        else:
            stops_str = "(direct)"

        return stops_str
   
    def __init__(self, service_json) -> None:
        now = datetime.now()
        current_time = now.strftime("%H%M")
        current_date = now.strftime("%Y/%m/%d")
        location = service_json["locationDetail"]
        self.uid = service_json["serviceUid"]
        self.date = service_json["runDate"].replace("-","/")
        self.origin = location["origin"][0]["description"]
        self.destination = location["destination"][0]["description"]
        self.type = service_json["serviceType"]
        self.operator = service_json["atocName"]
        if "realtimeDeparture" in location:
            self.departure_time=location["realtimeDeparture"]
        else:
            self.departure_time = location["gbttBookedDeparture"]
        self.platform= "TBA"

        if "platform" in location:
            self.platform = location["platform"]

        minute_diff = int(self.departure_time[-2:]) - int(current_time[-2:])
        hour_diff = 60*(int(self.departure_time[0:2]) - int(current_time[0:2]))
        diff = minute_diff+hour_diff

        if self.type != "train":
            self.stops = self.__get_stops(self.uid, self.date)

        


           
           

    def print(self):
        if self.type == "train":
            print(f"{self.date} | {self.departure_time} to {self.destination.ljust(30, '.')} | Platform {self.platform} | {self.operator}")
        else:
            print(f"{self.date} | {self.departure_time} to {self.destination.ljust(30, '.')} | {self.type.title()} {self.stops}")


class Departure_Data:

    def __get_departures(self, code, date = False) :

        req_string = code
        if date != False:
            req_string = f"{code}/{date}" 

        load_dotenv("./environment/.env")

        username = os.environ.get("USER")
        password = os.environ.get("PASSWORD")

        session = requests.Session()
        
        session.auth = (username,password)
        response = session.get(f"https://api.rtt.io/api/v1/json/search/{req_string}")
        return response
    

    def __init__(self, station_code) :
        self.services = []
        service_uids = []
        date = datetime.now()
        date_string = date.strftime("%Y/%m/%d")
        current_time = date.strftime("%H%M")
        departures = self.__get_departures(station_code)
        response_json = json.loads(departures.content)
        station_name = response_json["location"]["name"]
        print(f"{station_code}: {station_name}")

        
        while len(self.services)<= 10:
            print("Loading...")
            time.sleep(2)
            
            date_string = date.strftime("%Y/%m/%d")
            departures = self.__get_departures(station_code, date_string)
            response_json = json.loads(departures.content)
            if response_json["services"] is not None:
                for service in response_json["services"]:
                    service_obj = Station_Service(service)
                    if service_obj.uid not in service_uids and int(service_obj.departure_time) >= int(current_time):
                        self.services.append(service_obj)
                        service_uids.append(f"{service_obj.uid}_{date_string}")
            date = date + timedelta(days=1)  

             

        
        for service in self.services:
            service.print()


