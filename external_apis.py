
import requests
from geopy.geocoders import Nominatim

import os

print(os.getenv("api_key", default=None))

image_api_key = os.getenv("image_api_key", default=None)

def get_plant_image(plant_name):
    url = f"https://api.unsplash.com/search/photos?query={plant_name}&client_id={image_api_key}"
    response = requests.get(url).json()
    if response.get('results'):
        return response['results'][0]['urls']['regular']
    return None


def get_weather(city_name):
    geolocator = Nominatim(user_agent="weather_app")

    location = geolocator.geocode(city_name)
    if not location:
        return {"error": f"'{city_name}' is not a valid city."}

    weather_api_key = os.getenv("weather_api_key", default=None)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get("main"):
            weather = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
            }
            return weather
        else:
            return {"error": "Weather data not available for this city."}

    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {"error": "Something went wrong, please try again."}






