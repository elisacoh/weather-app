""""
app.py: this module hold the Flask app and routes for the weather web app, run it from here
"""
import socket
from flask import Flask, render_template, request, jsonify

from openmeteo_client import OpenMeteoClient
from weather_service import WeatherService

app = Flask(__name__)

from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

client=OpenMeteoClient()
weather_service=WeatherService(client)

@app.get("/whoami")
def whoami():
    """
    simploe function that return the container hostname
    :return: container hostname
    """
    return{"container": socket.gethostname()}

@app.route('/')
def index():
    """
    default route
    :return: a html template with the homepage
    """
    return render_template("home.html")

@app.route('/weather')
def weather():
    """
    retrieve the weather data, request the city name
    :return: a html template with the weather data
    """
    city_name = request.args.get('city', "").strip()

    if not city_name:
        return render_template("home.html", error="Please enter a city name")

    weather_data = weather_service.get_weather(city_name)

    # Check if city was found
    if "error" in weather_data or not weather_data.get("city"):
        return render_template("home.html",
                               error=f"City '{city_name}' not found. Please try again.")

    return render_template("index.html",
                           temperature=weather_data.get("temperature"),
                           city=weather_data.get("city"),
                           country=weather_data.get("country"),
                           daily_forecast=weather_data.get("daily_forecast"),
                           current_icon=weather_data.get("current_icon"),
                           current_desc=weather_data.get("current_desc"),
                           background=weather_data.get("background")
                           )


@app.route('/city')
def city():
    """
    retrieve the city name
    :return: a html template with the city name
    """
    city_name = request.args.get('city', "").strip()
    return render_template("index.html", city=city_name)


@app.get("/api/weather")
def api_weather():
    """
    retrieve the weather data, request the city name
    :return: json of the api data
    """
    q = (request.args.get('q','')).strip()
    if not q:
        return jsonify({"error": "missing q"}), 400
    weather_in = weather_service.get_weather(q)
    return jsonify(weather_in)

@app.get("/debug-geocode")
def debug_geocode():
    """
    helper function to try geocode
    :return: json of the geolocalisation
    """
    city_in = request.args.get("city","Tel Aviv")
    return jsonify(client.geocode(city_in))



if __name__ == '__main__':
    app.run()

@app.get("/health")
def health():
    """
    health check endpoint for Kubernetes readiness probe
    :return: json status ok
    """
    return jsonify({"status": "ok"}), 200
