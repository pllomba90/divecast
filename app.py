from flask import Flask, redirect, render_template, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import SignUpForm, LoginForm, PreferenceForm
from sqlalchemy.exc import IntegrityError
from models import User, Preference, db, connect_db
import requests, arrow, redis, json, pytz
from datetime import datetime



CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///divecast_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

with app.app_context():
    connect_db(app)
    db.create_all()

app.config['SECRET_KEY'] = "alwaysbetter"

debug = DebugToolbarExtension(app)

@app.before_request
def add_user_to_g():
    """Adding user to Flask Global. This logic will also check to see if user
    is already logged in. """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        if g.user:
            print(f"User {g.user.username} added to 'g'")

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id
    session['username'] = user.username


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        session['username'] = None


def get_current_weather(latitude, longitude, api_key, units):
    api_key = '426dbf6c3c5c400688f952b786efc418'

    user_id = g.user.id

    user = User.query.get(user_id)

    latitude = user.preference.latitude
    longitude = user.preference.longitude
    if user.preference.temp_unit == "F":
        units = "I"
    else:
        units = "M"
    
    
    
    url = f'http://api.weatherbit.io/v2.0/current?lat={latitude}&lon={longitude}&key={api_key}&units={units}'
    

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    else:
        print(f'Error occurred during the API request. Status code: {response.status_code}')
        return None


def get_weather_forecast(latitude, longitude, api_key, units, forecast_length):

    cache_key = f'weather_forecast:{latitude}:{longitude}:{api_key}:{units}:{forecast_length}'

    forecast = redis_client.get(cache_key)
    if forecast is not None:
        return json.loads(forecast)
    


    api_key = '426dbf6c3c5c400688f952b786efc418'

    user_id = g.user.id

    user = User.query.get(user_id)

    latitude = user.preference.latitude
    longitude = user.preference.longitude
    forecast_length = user.preference.forecast_length
    if user.preference.temp_unit == "F":
        units = "I"
    else:
        units = "M"
    
    url = f"https://api.weatherbit.io/v2.0/forecast/daily?lat={latitude}&lon={longitude}&key={api_key}&units={units}&days={forecast_length}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        serialized_data = json.dumps(data['data'])  
        redis_client.set(cache_key, serialized_data, ex=86400)
        return data['data']  
    else:
        print(f'Error occurred during the API request. Status code: {response.status_code}')
        return None
    
def get_correct_temp(user, weather_data):
    api_key = '426dbf6c3c5c400688f952b786efc418'

    latitude = user.preference.latitude
    longitude = user.preference.longitude

    if user.preference.temp_unit == "F":
        units = "I"
    else:
        units = "M"
    weather_data = get_current_weather(latitude, longitude, api_key, units)

    if user.preference.air_temp <= weather_data['data'][0]['temp']:
        return True
    else:
        return False


def fetch_and_cache_tidal_info(api_key, latitude, longitude, forecast_length):
    user = g.user
    forecast_length = int(user.preference.forecast_length)
    cache_key = f'tidal_info:{latitude}:{longitude}:{api_key}:{forecast_length}'
    
    start = arrow.now().floor('day')
    end = arrow.now().shift(days=forecast_length).floor('day')

    start_date = start.to('UTC').timestamp()
    end_date = end.to('UTC').timestamp()

    url = f'https://api.stormglass.io/v2/tide/extremes/point'
    headers = {'Authorization': api_key}
    params = {'lat': latitude, 'lng': longitude, 'start': start_date, 'end': end_date}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        serialized_data = json.dumps(data)
        redis_client.set(cache_key, serialized_data, ex=86400)
        return data
    else:
        print(f'Error occurred during the API request. Status code: {response.status_code}')
        return None


def get_tidal_info(api_key, latitude, longitude, forecast_length):
    cache_key = f'tidal_info:{latitude}:{longitude}:{api_key}:{forecast_length}'
    tidal_info = redis_client.get(cache_key)

    if tidal_info is not None:
        data = json.loads(tidal_info)
        return data

    data = fetch_and_cache_tidal_info(api_key, latitude, longitude, forecast_length)
    if data:
        return data


def calculate_ideal_dive_time(tidal_info, preference):
    user = g.user
    latitude = user.preference.latitude
    longitude = user.preference.longitude
    forecast_length = int(user.preference.forecast_length)
    api_key = 'f7e98148-282d-11ee-86b2-0242ac130002-f7e981fc-282d-11ee-86b2-0242ac130002'

    tidal_info = get_tidal_info(api_key, latitude, longitude, forecast_length)

    low_tide_events = [event for event in tidal_info['data'] if event['type'] == 'low']
    high_tide_events = [event for event in tidal_info['data'] if event['type'] == 'high']

    first_low_tide = low_tide_events[0]
    first_high_tide = high_tide_events[0]

    if user.preference.tide_preference == 'incoming':
        ideal_dive_time = arrow.get(first_low_tide['time']).shift(hours=1.5)
    else:
        ideal_dive_time = arrow.get(first_high_tide['time']).shift(hours=1.5)

    morning_time = arrow.get('06:00', 'HH:mm')
    afternoon_time = arrow.get('11:00', 'HH:mm')
    evening_time = arrow.get('16:00', 'HH:mm')

    if user.preference.time_of_day == 'Morning' and morning_time <= ideal_dive_time < afternoon_time:
        matched_tide_time = 'Morning'
    elif user.preference.time_of_day == 'Afternoon' and afternoon_time <= ideal_dive_time < evening_time:
        matched_tide_time = 'Afternoon'
    elif user.preference.time_of_day == 'Evening' and evening_time <= ideal_dive_time:
        matched_tide_time = 'Evening'
    else:
        matched_tide_time = None

    return ideal_dive_time.format('HH:mm:ss'), matched_tide_time



def get_current_coords(location, api_key):
    
    api_key = '5b5d66b9a6ff4b5789d6d3a6ae9f7268'  
    url = f'https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
         data = response.json()
    if data.get('results'):
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            print(latitude, longitude)
            return latitude, longitude
    
    else:
        return None



@app.route('/')
def home_page():
    """Show homepage: either for a logged-in user or for an anon user"""
    if g.user:
        user = g.user
        tidal_api_key = 'f7e98148-282d-11ee-86b2-0242ac130002-f7e981fc-282d-11ee-86b2-0242ac130002'
        weather_api_key = '426dbf6c3c5c400688f952b786efc418'
        if user.preference.temp_unit == "F":
            units = "I"
        else:
            units = "M"

        weather = get_current_weather(latitude=user.preference.latitude, 
                                      longitude=user.preference.longitude, 
                                      api_key=weather_api_key, 
                                      units=units)
        
        tidal_info = get_tidal_info(latitude=user.preference.latitude,
                                    longitude=user.preference.longitude, 
                                    api_key=tidal_api_key,
                                    forecast_length=user.preference.forecast_length)
        
        extended_forecast = get_weather_forecast(latitude=user.preference.latitude,
                                                longitude=user.preference.longitude,
                                                api_key=weather_api_key, 
                                                units=units,
                                                forecast_length=user.preference.forecast_length)
        
        user_timezone = user.preference.get_user_timezone(user.preference.latitude, user.preference.longitude)

        correct_temp = get_correct_temp(user, weather_data=weather)

        ideal_dive_time, matched_tide_time = calculate_ideal_dive_time(tidal_info=tidal_info,
                                                    preference=user.preference.tide_preference)

        for event in tidal_info['data']:
            utc_time = arrow.get(event['time'])  
            local_time = utc_time.to(user_timezone)  
            event['time'] = local_time.format('YYYY-MM-DD HH:mm:ss')

        return render_template('home.html', user=user, 
                               weather=weather, 
                               tidal_info=tidal_info, 
                               extended_forecast=extended_forecast, 
                               ideal_dive_time=ideal_dive_time,
                               matched_tide_time=matched_tide_time,
                               correct_temp=correct_temp)
    else:
        return render_template('home-anon.html')



@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()

    if form.is_submitted() and form.validate():
         user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
         db.session.commit()
         do_login(user)
         add_user_to_g()
         return redirect("/initial_pref")

    else:

        return render_template('sign-up.html', form=form)

       
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.is_submitted() and form.validate():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            add_user_to_g()
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)



@app.route('/initial_pref', methods=['GET', 'POST'])
def set_up_prefs():


    form = PreferenceForm()

    api_key = "5b5d66b9a6ff4b5789d6d3a6ae9f7268"
    

    if form.is_submitted() and form.validate():
            location = form.location.data
            temp_unit=form.temp_unit.data
            air_temp=form.air_temp.data
            tide_pref=form.tide_pref.data
            time_of_day=form.time_of_day.data
            forecast_length = form.forecast_length.data
        
            latitude, longitude = get_current_coords(location, api_key)   
            new_pref = Preference.create_preference(
                        user_id=g.user.id,
                        temp_unit=temp_unit,
                        air_temp=air_temp,
                        tide_pref=tide_pref,
                        time_of_day=time_of_day,
                        forecast_length=forecast_length,
                        location=location,  
                        latitude=latitude, 
                        longitude=longitude  
                    )

                    
            db.session.commit()
            return redirect('/')

    else:
                # flash('Location not found. Please enter a valid location.', 'danger')
                # flash('Error occurred during geocoding. Please try again later.', 'danger')
                return render_template('initial_prefs.html', form=form)
            
    
@app.route('/user/edit', methods=['GET', 'POST'])
def edit_user():

    user_id = g.user.id
    user = User.query.get(user_id)
    api_key = "5b5d66b9a6ff4b5789d6d3a6ae9f7268"

    form = PreferenceForm(obj=user.preference)

    

    if form.is_submitted() and form.validate():

        location = form.location.data
        temp_unit = form.temp_unit.data
        air_temp = form.air_temp.data
        tide_pref = form.tide_pref.data
        time_of_day = form.time_of_day.data
        forecast_length = form.forecast_length.data

        latitude, longitude = get_current_coords(location, api_key)

        if latitude is not None and longitude is not None:
            preference = user.preference
            preference.temp_unit = temp_unit
            preference.air_temp = air_temp
            preference.tide_pref = tide_pref
            preference.time_of_day = time_of_day
            preference.location = location
            preference.latitude = latitude
            preference.longitude = longitude
            preference.forecast_length = forecast_length

            db.session.commit()
            return redirect('/')

        flash('Location not found. Please enter a valid location.', 'danger')

    return render_template('edit.html', user=user, form=form)

@app.route('/forecast/<date>')
def individual_forecast(date):
    user = g.user
    tidal_api_key = 'f7e98148-282d-11ee-86b2-0242ac130002-f7e981fc-282d-11ee-86b2-0242ac130002'
    weather_api_key = '426dbf6c3c5c400688f952b786efc418'
    if user.preference.temp_unit == "F":
        units = "I"
    else:
        units = "M"

    tidal_info = get_tidal_info(latitude=user.preference.latitude,
                                    longitude=user.preference.longitude, 
                                    api_key=tidal_api_key,
                                    forecast_length=user.preference.forecast_length)
    
    ideal_dive_time, matched_tide_time = calculate_ideal_dive_time(tidal_info=tidal_info,
                                                    preference=user.preference.tide_preference)

    forecast = get_weather_forecast(latitude=user.preference.latitude,
                                    longitude=user.preference.longitude,
                                    api_key=weather_api_key,
                                    units=units,
                                    forecast_length=user.preference.forecast_length)

    selected_forecast = [f for f in forecast if f['valid_date'] == date]

    return render_template('single_forecast.html', 
                           forecast=selected_forecast[0],
                             user=user, 
                             ideal_dive_time=ideal_dive_time,
                             matched_tide_time=matched_tide_time,
                             tidal_info=tidal_info)

@app.route('/logout')
def logout():

    do_logout()

    return render_template('home-anon.html')