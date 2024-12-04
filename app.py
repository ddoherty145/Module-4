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
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = ''
    city2 = ''
    units = ''

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!


    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    context = {

    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
