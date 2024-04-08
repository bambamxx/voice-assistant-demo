import json
import requests
from geopy.geocoders import Nominatim
import os


def rag_weather(msg):
    """
    Retrieves weather data for a given location using OpenWeatherMap API and constructs the RAG section of the prompt.

    Args:
        msg (str): The input message containing the location information.

    Yields:
        str: The JSON string containing the RAG prompt with weather data and the soruce.
    """

    # load the input data
    data = json.loads(msg.body)
    weather_location = data["cat_json"]["location"]

    # calling the Nominatim tool and create Nominatim class
    loc = Nominatim(user_agent="Geopy Library")

    # entering the location name
    getLoc = loc.geocode(weather_location)

    # printing latitude and longitude
    print("Latitude = ", getLoc.latitude, "\n")
    print("Longitude = ", getLoc.longitude)

    # send api request to get weather data
    data["RAG"] = json.loads(
        requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={getLoc.latitude}&lon={getLoc.longitude}&appid={os.getenv('WEATHER_API_KEY')}&units=imperial"
        ).text
    )

    # set the source of the RAG
    data["source"] = "Open weather API"

    yield json.dumps(data)
