"""
files thzt call the open meteo API - external to retrieve geolocalisation and forecast
"""
import requests

GEOLOCALISATION_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

class OpenMeteoClient:
    """
    une classe
    """
    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def geocode(self, city:str, count: int = 1):
        """

        :param city:
        :param count:
        :return:
        """

        params = {"name":city, "count":count, }
        r = requests.get(GEOLOCALISATION_URL, params=params, timeout=self.timeout_seconds)
        data = r.json()
        results = data.get("results") or []
        return results[0] if results else None

    def forecast(self, latitude:float, longitude:float):
        """Returns raw forecast JSON"""
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "temperature_unit":"celsius",
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
                     "weathercode,relative_humidity_2m_mean",
            "timezone": "auto"
        }
        r= requests.get(FORECAST_URL, params=params, timeout=self.timeout_seconds)
        return r.json()
