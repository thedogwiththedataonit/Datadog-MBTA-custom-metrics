import requests
import json
from checks import AgentCheck
import logging
import sys
import datetime

logger = logging.getLogger()
fileHandler = logging.FileHandler("/etc/datadog-agent/checks.d/mbta.log")
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)

def alerts_route(route, stop1, stop2):
    url = "https://api-v3.mbta.com/alerts"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[route]": route, "filter[stop]": stop1+","+stop2}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    alerts = []
    #loop through the data and find the alerts
    for i in range(0, len(data["data"])):
        alert = {"header":data["data"][i]["attributes"]["header"],
                "effect":data["data"][i]["attributes"]["effect"],
                "description":data["data"][i]["attributes"]["description"]
        }
        alerts.append(alert)
    return alerts


def schedule(route, stop, bound):
    url = "https://api-v3.mbta.com/schedules"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[route]": route, "filter[stop]": stop, "filter[direction_id]": bound}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    #parse data to get the departure time
    #return the departure time
    list_of_departures = []
    list_of_times_till = []
    list_of_trip_ids = []

    for i in range(0, len(data["data"])):
        if (data["data"][i]["attributes"]["departure_time"] == None):
            continue
        else:
            departure_time = data["data"][i]["attributes"]["departure_time"]
            trip = data["data"][i]["relationships"]["trip"]["data"]["id"]
            new_departure_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")
            #current_time = datetime.datetime.now().strftime("%H:%M") and subtract 5 hours
            current_time = datetime.datetime.now() - datetime.timedelta(hours=5)
            current_time = current_time.strftime("%H:%M")
            time_difference = datetime.datetime.strptime(departure_time[11:16], "%H:%M") - datetime.datetime.strptime(current_time, "%H:%M")
            minute_difference = time_difference.seconds // 60

            list_of_departures.append(new_departure_time.strftime("%I:%M %p"))
            list_of_times_till.append(minute_difference)
            list_of_trip_ids.append(trip)

    #print(new_departure_time.strftime("%I:%M %p"), minute_difference, trip)

    time_till_next_departure = min(list_of_times_till)
    index = list_of_times_till.index(time_till_next_departure)
    next_departure = list_of_departures[index]
    trip_id = list_of_trip_ids[index]
    next_prediction = (predict_stop(stop, bound, trip_id))

    #remove index from list of departures and times till
    list_of_departures.pop(index)
    list_of_times_till.pop(index)

    #second next departure
    next_time_till_next_departure = min(list_of_times_till)
    next_index = list_of_times_till.index(next_time_till_next_departure)
    next_next_departure = list_of_departures[next_index]


    return next_departure, time_till_next_departure, next_prediction, next_next_departure, next_time_till_next_departure

def predict_stop(stop, bound, trip):
    url = "https://api-v3.mbta.com/predictions"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[stop]": stop, "filter[direction_id]": bound, "filter[trip]": trip}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if (data["data"] == []):
        return "No prediction"
    else:
        arrival_time = data["data"][0]["attributes"]["departure_time"]
        new_arrival_time = datetime.datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M:%S%z")
        return new_arrival_time.strftime("%I:%M %p")

def main():
    alerts = (alerts_route("CR-Worcester", "place-WML-0035", "NEC-2287"))
    inbound = (schedule("CR-Worcester", "place-WML-0035", 1))
    outbound = (schedule("CR-Worcester", "NEC-2287", 0))

    time_till_next_inbound = inbound[1]
    time_till_next_outbound = outbound[1]
    time_till_next_next_inbound = inbound[4]
    time_till_next_next_outbound = outbound[4]

    print('Next train from Boston Landing to South Station comes at ' + inbound[0] + ' and it is predicted to arrive at ' + inbound[2])
    print('Next train from South Station to Boston Landing comes at ' + outbound[0] + ' and it is predicted to arrive at ' + outbound[2])
    return 0

class ddogMetric(AgentCheck):
    def check(self, instance):

        alerts = (alerts_route("CR-Worcester", "place-WML-0035", "NEC-2287"))
        inbound = (schedule("CR-Worcester", "place-WML-0035", 1))
        outbound = (schedule("CR-Worcester", "NEC-2287", 0))
        
        for alert in alerts:
            logger.info(alert["effect"] | alert["header"] | alert["description"])
        
        time_till_next_inbound = inbound[1]
        time_till_next_outbound = outbound[1]
        time_till_next_next_inbound = inbound[4]
        time_till_next_next_outbound = outbound[4]

        logger.info('Next train from Boston Landing to South Station comes at ' + inbound[0] + ' and it is predicted to arrive at ' + inbound[2] + ' and the next train comes in ' + str(time_till_next_inbound) + ' minutes')
                
        logger.info('Next train from South Station to Boston Landing comes at ' + outbound[0] + ' and it is predicted to arrive at ' + outbound[2] + ' and the next train comes in ' + str(time_till_next_outbound) + ' minutes')
                               
        self.gauge('minutes_till_arrival_at_boston_landing', time_till_next_inbound, tags=['direction:inbound', "env:mbta"])
        self.gauge('minutes_till_arrival_at_south_station', time_till_next_outbound, tags=['direction:outbound', "env:mbta"])
