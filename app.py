from flask import Flask, render_template, session, redirect, url_for, request
import requests
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Set the secret key for securely signing session cookies and protecting against tampering
app.secret_key = 'your_secret_key'

# Replace with your actual OpenWeatherMap API key
API_KEY = os.environ["API_KEY"]
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

LANGUAGES = {
    'en': 'English',
    'ar': 'العربية',
    'fr': 'Français',
    'es': 'Español'
}


with open("translations.json", "r", encoding="utf-8") as translations_data:
    translations = json.load(translations_data)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['city'] = request.form.get('city', 'Paris')

    city = session.get('city', 'Paris')
    lang = session.get('lang', 'en')
    weather = get_weather(city, lang)
    labels = translations.get(lang, translations['en'])

    return render_template('index.html',
                           current_lang=lang,
                           languages=LANGUAGES,
                           weather=weather,
                           city=city,
                           labels=labels)


@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in LANGUAGES:
        session['lang'] = lang_code
    return redirect(url_for('index'))


def get_weather(city, lang):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': API_KEY,
        'lang': lang,
        'units': 'metric'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Create a timezone object based on the offset in seconds
        timezone_offset = data.get('timezone', 0)
        tz = timezone(timedelta(seconds=timezone_offset))

        # Convert all relevant timestamps to timezone-aware datetime objects
        local_time = datetime.fromtimestamp(data['dt'], tz)
        sunrise = datetime.fromtimestamp(data['sys']['sunrise'], tz)
        sunset = datetime.fromtimestamp(data['sys']['sunset'], tz)

        return {
            'description': data['weather'][0]['description'].capitalize(),
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'icon': data['weather'][0]['icon'],
            'condition': data['weather'][0]['main'].lower(),
            'city': data['name'],
            'local_time': local_time.strftime('%H:%M'),
            'sunrise': sunrise.strftime('%H:%M'),
            'sunset': sunset.strftime('%H:%M')
        }

    return None


if __name__ == '__main__':
    app.run(debug=True)
