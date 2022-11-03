import requests
import datetime

def get_lines():
    #make a get request curl -X GET "https://api-v3.mbta.com/lines?api_key=20" -H "accept: application/vnd.api+json" -H "x-api-key: 3738225e25f743cdbd12e3b1d7708490"
    #parse the response
    #return the status

    url = "https://api-v3.mbta.com/lines"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

#print(get_lines())

def get_stop(stop_id):
    #make a get request curl -X GET "https://api-v3.mbta.com/stops?filter[route]=Red&filter[direction_id]=0&include=route&api_key=3738225e25f743cdbd12e3b1d7708490" -H "accept: application/vnd.api+json" -H "x-api-key: 3738225e25f743cdbd12e3b1d7708490"
    #parse the response
    #return the status

    url = "https://api-v3.mbta.com/stops"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[id]": stop_id, "include": "route"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data

#print(get_stop("WML-0035"))

def get_schedule():
    #make a get request curl -X GET "https://api-v3.mbta.com/schedules?filter[stop]=place-north&filter[route]=Red&filter[direction_id]=0&include=stop,route&sort=departure_time&api_key=3738225e25f743cdbd12e3b1d7708490" -H "accept: application/vnd.api+json" -H "x-api-key: 3738225e25f743cdbd12e3b1d7708490"
    #parse the response
    #return the status

    url = "https://api-v3.mbta.com/schedules"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[stop]": "place-north", "filter[direction_id]": "0", "include": "stop,route", "sort": "departure_time"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data


def get_routes(long_name):
    #make a get request curl -X GET "https://api-v3.mbta.com/routes?filter[type]=0,1&filter[long_name]=Red&api_key=3738225e25f743cdbd12e3b1d7708490" -H "accept: application/vnd.api+json" -H "x-api-key: 3738225e25f743cdbd12e3b1d7708490"
    #parse the response
    #return the status

    url = "https://api-v3.mbta.com/routes"
    headers = {"accept": "application/vnd.api+json", "x-api-key": "3738225e25f743cdbd12e3b1d7708490"}
    params = {"filter[type]": "2", "filter[long_name]": long_name}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data

#print(get_routes("Framingham/Worcester Line"))



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
        if (data["data"][i]["attributes"]["departure_time"] != None):
            departure_time = data["data"][i]["attributes"]["departure_time"]
            trip = data["data"][i]["relationships"]["trip"]["data"]["id"]
            new_departure_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")
            current_time = datetime.datetime.now().strftime("%H:%M")
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
        arrival_time = data["data"][0]["attributes"]["arrival_time"]
        new_arrival_time = datetime.datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M:%S%z")
        return new_arrival_time.strftime("%I:%M %p")



print(alerts_route("CR-Worcester", "place-WML-0035", "NEC-2287"))
print(schedule("CR-Worcester", "place-WML-0035", 1))
print(schedule("CR-Worcester", "NEC-2287", 0))

#the pm and AM doesnt work for metrics, maybe make it a log then into a metric or something


