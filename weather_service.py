"""
mon module
"""
from datetime import datetime

class WeatherService:
    """
    In this class we retrive and format the weather data for a given city query:
      1) Geocoding a city name into coordinates (lat/lon)
      2) Fetching forecast data from the open meteo client
      3) Translating Open meteo weather codes into description/icons
      4) Return a structured dictionary
    """
    def __init__(self, openmeteo_client, ttl =600):
        self.openmeteo_client = openmeteo_client
        self.ttl = ttl

    def hello_world(self):
        """ a function about hello to the world """
        return "hello world"

    def get_weather(self, q: str) -> dict:
        """

        :param q:
        :return:
        """
        city = q.strip()
        loc = self.openmeteo_client.geocode(city)
        if not loc:
            return {"error": "City not found"}

        raw_data = self.openmeteo_client.forecast(loc["latitude"], loc["longitude"])

        current_code = raw_data.get("current_weather", {}).get("weathercode", 0)
        current_weather = self._get_weather_code(current_code)

        daily_forecast = []
        if "daily" in raw_data:
            for i in range(len(raw_data["daily"]["time"])):
                date_obj = datetime.strptime(raw_data["daily"]["time"][i], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%a %d/%m")

                weather_info = self._get_weather_code(raw_data["daily"]["weathercode"][i])

                daily_forecast.append({
                    "date": raw_data["daily"]["time"][i],
                    "formatted_date": formatted_date,
                    "max": raw_data["daily"]["temperature_2m_max"][i],
                    "min": raw_data["daily"]["temperature_2m_min"][i],
                    "day_avg": raw_data["daily"]["temperature_2m_mean"][i],
                    "night_avg": raw_data["daily"]["temperature_2m_min"][i],
                    "humidity_avg": raw_data["daily"]["relative_humidity_2m_mean"][i],
                    "icon": weather_info["icon"],
                    "description": weather_info["desc"]
                })

        return {
            "city": loc.get("name", city),
            "country": loc.get("country"),
            "latitude": raw_data["latitude"],
            "longitude": raw_data["longitude"],
            "temperature": raw_data.get("current_weather", {}).get("temperature"),
            "units": raw_data.get("current_weather_units", {}),
            "daily_forecast": daily_forecast,
            "current_icon": current_weather["icon"],
            "current_desc": current_weather["desc"],
            "background":current_weather["bg"]
        }

    def _get_weather_code(self, code:int):
        """

        :param code:
        :return:
        """
        weather_map =  {
        0: {"icon": "☀️", "desc": "Clear sky", "bg":"0_clear.jpg"},
        1: {"icon": "🌤️", "desc": "Mainly clear", "bg":"0_clear.jpg"},
        2: {"icon": "⛅", "desc": "Partly cloudy", "bg":"2_partly_cloudy.jpg"},
        3: {"icon": "☁️", "desc": "Overcast", "bg":"3_overcast.jpg"},
        45: {"icon": "🌫️", "desc": "Foggy", "bg":"3_overcast.jpg"},
        48: {"icon": "🌫️", "desc": "Rime fog", "bg":"3_overcast.jpg"},
        51: {"icon": "🌦️", "desc": "Light drizzle", "bg":"51_little_drizzle.jpeg"},
        53: {"icon": "🌦️", "desc": "Moderate drizzle", "bg":"53_moderate_drizzle.jpeg"},
        55: {"icon": "🌧️", "desc": "Dense drizzle", "bg":"53_moderate_drizzle.jpeg"},
        61: {"icon": "🌧️", "desc": "Slight rain", "bg":"53_moderate_drizzle.jpg"},
        63: {"icon": "🌧️", "desc": "Moderate rain", "bg":"53_moderate_drizzle.jpeg"},
        65: {"icon": "🌧️", "desc": "Heavy rain", "bg":"53_moderate_drizzle.jpeg"},
        71: {"icon": "🌨️", "desc": "Slight snow", "bg":"snow.jpeg"},
        73: {"icon": "🌨️", "desc": "Moderate snow", "bg":"snow.jpeg"},
        75: {"icon": "🌨️", "desc": "Heavy snow", "bg":"snow.jpeg"},
        77: {"icon": "🌨️", "desc": "Snow grains", "bg":"snow.jpeg"},
        80: {"icon": "🌦️", "desc": "Slight rain showers","bg":"80_slightly_rain_shower.jpg"},
        81: {"icon": "🌧️", "desc": "Moderate rain showers","bg":"80_slightly_rain_shower.jpg"},
        82: {"icon": "⛈️", "desc": "Violent rain showers","bg":"80_slightly_rain_shower.jpg"},
        85: {"icon": "🌨️", "desc": "Slight snow showers","bg":"snow.jpg"},
        86: {"icon": "🌨️", "desc": "Heavy snow showers","bg":"heavy_snow.jpg"},
        95: {"icon": "⛈️", "desc": "Thunderstorm","bg":"thunder.jpg"},
        96: {"icon": "⛈️", "desc": "Thunderstorm with hail","bg":"thunder.jpg"},
        99: {"icon": "⛈️", "desc": "Thunderstorm with heavy hail","bg":"thunder.jpg"},
    }
        return weather_map.get(code, {"icon": "❓", "desc": "Unknown"})
