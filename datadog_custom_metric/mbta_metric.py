import requests
import json
from checks import AgentCheck
import logging
import sys
import datetime

logger = logging.getLogger()
fileHandler = logging.FileHandler("/etc/dataog-agent/checks.d/logfile.log")
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)

def get_predictions(stop, bound):
    #make a get request curl -X GET "https://api-v3.mbta.com/predictions?filter[stop]=place-north&filter[route]=Red&filter[direction_id]=0&include=stop,route&api_key=3738225e25f743cdbd12e3b1d7708490" -H "accept: application/vnd.api+json" -H "x-api-key: 3738225e25f743cdbd12e3b1d7708490"
    #parse the response
    #return the status
    url = "https://api-v3.mbta.com/predictions"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[stop]": stop, "include": "stop,route", "filter[direction_id]": bound, "filter[route]":"CR-Worcester"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data


    #south station ID: NEC-2287
    #Boston Landing ID: place-WML-0035

def south_station_to_boston_landing():
    id = "NEC-2287"
    bound = 0
    results = get_predictions(id, bound)
    if (results["data"] == []):
        return "No trains", 0
    departure_time = results["data"][0]["attributes"]["departure_time"]
    new_departure_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")
    #find the difference between the current time and the departure time
    stripped_departure_time = departure_time[11:16]
    current_time = datetime.datetime.now().strftime("%H:%M")
    time_difference = datetime.datetime.strptime(stripped_departure_time, "%H:%M") - datetime.datetime.strptime(current_time, "%H:%M")

    minute_difference = time_difference.seconds // 60
    new_departure_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")

    return new_departure_time.strftime("%I:%M %p"), minute_difference
        
def boston_landing_to_south_station():
    id = "place-WML-0035"
    bound = 1
    results = get_predictions(id, bound)
    if (results["data"] == []):
        return "No trains", 0

    departure_time = results["data"][0]["attributes"]["departure_time"]

    stripped_departure_time = departure_time[11:16]
    current_time = datetime.datetime.now().strftime("%H:%M")
    time_difference = datetime.datetime.strptime(stripped_departure_time, "%H:%M") - datetime.datetime.strptime(current_time, "%H:%M")

    minute_difference = time_difference.seconds // 60
    new_departure_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")

    return new_departure_time.strftime("%I:%M %p"), minute_difference


class ddogMetric(AgentCheck):
    def check(self, instance):
        ssToBL = (south_station_to_boston_landing())
        blToSS = (boston_landing_to_south_station())

        if ssToBL[0] == "No trains":
            logger.info("No trains")

        elif blToSS[0] == "No trains":
            logger.info("No trains")
        else:                
            self.gauge('timeTillArrival_SouthStation', ssToBL[1])
            self.gauge('timeTillArrival_BostonLanding', blToSS[1])

            logger.info('The train is leaving South Station at ' + str(ssToBL[0]) + " and is headed to Boston Landing")
            logger.info('The train is leaving Boston Landing at ' + str(blToSS[0]) + " and is headed to South Station")

