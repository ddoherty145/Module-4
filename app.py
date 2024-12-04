import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
# from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city')
    units = request.args.get('units')

    if not city or not units:
        return render_template('error.html', error="Please provide a valid city and unit.")

    params = {
        'q' : city,
        'units' : units,
        'appid' : API_KEY
    }

    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        error_message = response.json().get('message', 'An error occcured while fetching data.')
        return render_template('error.html', error=error_message)
    
    result_json = response.json()

    context = {
        'date': datetime.now(),
        'city': result_json.get('name', 'Unknown'),
        'description': result_json.get('weather', [{}])[0].get('description', 'No description available'),
        'temp': result_json.get('main', {}).get('temp', 'N/A'),
        'humidity': result_json.get('main', {}).get('humidity', 'N/A'),
        'wind_speed': result_json.get('wind', {}).get('speed', 'N/A'),
        'sunrise': datetime.fromtimestamp(result_json.get('sys', {}).get('sunrise', 0)),
        'sunset': datetime.fromtimestamp(result_json.get('sys', {}).get('sunset', 0)),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    def get_weather_data(city, units):
        """Fetch weather data for a city."""
        params = {
            'q': city,
            'units': units,
            'appid': API_KEY
        }
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data for {city}: {response.status_code} - {response.json().get('message')}")
            return None

    city1_data = get_weather_data(city1, units)
    city2_data = get_weather_data(city2, units)

    if not city1_data:
        return render_template('error.html', error=f"Could not fetch data for {city1}.")
    if not city2_data:
        return render_template('error.html', error=f"Could not fetch data for {city2}.")

    city1_info = {
        'temp': city1_data.get('main', {}).get('temp', 'N/A'),
        'humidity': city1_data.get('main', {}).get('humidity', 'N/A'),
        'wind_speed': city1_data.get('wind', {}).get('speed', 'N/A'),
        'sunset': datetime.fromtimestamp(city1_data['sys'].get('sunset', 0)) if city1_data['sys'].get('sunset') else 'N/A',
        'name': city1_data.get('name', 'Unknown')
    }

    city2_info = {
        'temp': city2_data.get('main', {}).get('temp', 'N/A'),
        'humidity': city2_data.get('main', {}).get('humidity', 'N/A'),
        'wind_speed': city2_data.get('wind', {}).get('speed', 'N/A'),
        'sunset': datetime.fromtimestamp(city2_data['sys'].get('sunset', 0)) if city2_data['sys'].get('sunset') else 'N/A',
        'name': city2_data.get('name', 'Unknown')
    }

    temp_diff = abs(city1_info['temp'] - city2_info['temp']) if city1_info['temp'] != 'N/A' and city2_info['temp'] != 'N/A' else 'N/A'

    context = {
        'date': datetime.now().strftime('%A, %B %d, %Y'),
        'units_letter': get_letter_for_units(units),
        'city1_info': city1_info,
        'city2_info': city2_info,
        'temp_diff': temp_diff,
        'abs': abs
    }

    return render_template('comparison_results.html', **context)



if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
