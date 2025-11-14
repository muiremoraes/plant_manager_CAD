from geopy.geocoders import Nominatim

def city_exists(city_name):
    geolocator = Nominatim(user_agent="city_checker", timeout=10)  # 10 seconds timeout
    try:
        location = geolocator.geocode(city_name)
        if location and "Ireland" in location.address:
            return True
        else:
            return False
    except Exception as e:
        print(f"Geocoder error: {e}")
        return False
