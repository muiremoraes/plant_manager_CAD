
import requests
from geopy.geocoders import Nominatim


def get_plant_image(plant_name):
    url = f"https://api.unsplash.com/search/photos?query={plant_name}&client_id=GYdriHj7J2Rjy-GBMq4oKZNtcLDrEXoZWJCLQs7FN0E"
    response = requests.get(url).json()
    if response.get('results'):
        return response['results'][0]['urls']['regular']
    return None


def get_weather(city_name):
    geolocator = Nominatim(user_agent="weather_app")

    location = geolocator.geocode(city_name)
    if not location:
        return {"error": f"'{city_name}' is not a valid city."}

    api_key = "7169d5adfea6dd2e6f52b8e50c399697" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"

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






