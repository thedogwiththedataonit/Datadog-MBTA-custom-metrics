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
    departure_time = results["data"][0]["attributes"]["departure_time"]

    stripped_departure_time = departure_time[11:16]
    current_time = datetime.datetime.now().strftime("%H:%M")
    time_difference = datetime.datetime.strptime(stripped_departure_time, "%H:%M") - datetime.datetime.strptime(current_time, "%H:%M")

    minute_difference = time_difference.seconds // 60
    new_departure_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")

    return new_departure_time.strftime("%I:%M %p"), minute_difference


print(south_station_to_boston_landing())
print(boston_landing_to_south_station())

#the pm and AM doesnt work for metrics, maybe make it a log then into a metric or something


