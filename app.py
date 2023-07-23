from flask import Flask, redirect, render_template, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import SignUpForm, LoginForm, PreferenceForm
from sqlalchemy.exc import IntegrityError
from models import User, Weather, Tide, Preference, db, connect_db
import requests
import arrow

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///divecast_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

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
    
import requests

def get_tidal_info(api_key, latitude, longitude):
    user = g.user

    latitude = user.preference.latitude
    longitude = user.preference.longitude
    api_key = 'f7e98148-282d-11ee-86b2-0242ac130002-f7e981fc-282d-11ee-86b2-0242ac130002'
    current_time = arrow.now()

    start = current_time
    end = current_time.shift(days=7)

    start_date = start.format('YYYY-MM-DDTHH:mm:ss')
    end_date = end.format('YYYY-MM-DDTHH:mm:ss')


    url = f'https://api.stormglass.io/v2/tide/extremes/point'
    headers = {'Authorization': api_key}
    params = {'lat': latitude, 'lng': longitude, 'start': start_date, 'end': end_date}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        print (data)
        return data
    else:
        print(f'Error occurred during the API request. Status code: {response.status_code}')
        return None

def get_current_coords(location, api_key):
    user = g.user
    location = user.preference.location
    api_key = '5b5d66b9a6ff4b5789d6d3a6ae9f7268'  
    url = f'https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}'

    response = requests.get(url)
    if response.status_code == 200:
         data = response.json()
    if data.get('results'):
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            return latitude, longitude
    
    else:
        return None



@app.route('/')
def home_page():
    """Show homepage: either for a logged in user or for 
    an anon user
    """
    if g.user:
        user = g.user
        tidal_api_key = 'f7e98148-282d-11ee-86b2-0242ac130002-f7e981fc-282d-11ee-86b2-0242ac130002'
        weather_api_key = '426dbf6c3c5c400688f952b786efc418'
        if user.preference.temp_unit == "F":
            units = "I"
        else:
            units = "M"

        weather = get_current_weather(latitude={user.preference.latitude}, longitude={user.preference.longitude}, api_key=weather_api_key, units=units)
        tidal_info=get_tidal_info(latitude={user.preference.latitude}, longitude={user.preference.longitude}, api_key=tidal_api_key)

        return render_template('home.html', user=user, weather=weather, tidal_info=tidal_info)
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
        
            latitude, longitude = get_current_coords(location, api_key)   
            new_pref = Preference.create_preference(
                        user_id=g.user.id,
                        temp_unit=temp_unit,
                        air_temp=air_temp,
                        tide_pref=tide_pref,
                        time_of_day=time_of_day,
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

            db.session.commit()
            return redirect('/')

        flash('Location not found. Please enter a valid location.', 'danger')

    return render_template('edit.html', user=user, form=form)

@app.route('/logout')
def logout():

    do_logout()

    return render_template('home-anon.html')
