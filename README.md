# Divecast
This is a weather and tide focused, SCUBA dive planning application. The user is prompted to input location and tide preferences.
The application querys the weather and tidal conditions for the selected location and then provides an ideal time for the user to 
plan on entering the water if there is such a time that meets the user's preferences. This project is mainly built on Python3. There is the littlest bit of Javascript for the front end functionality  and as I work to improve it I'm sure I will use more Javascript to beautify the front end. I used a PSQL database as my user database and a Redis server as my cache for short term information storing and to speed up certain aspects of the project. This is a project I intend to tinker with for some time so I will certainly be adding more information here.

I will be querying the following APIs for this project:
- Weather conditions:
https://api.weatherbit.io/v2.0/forecast/daily
- Tidal conditions:
https://api.stormglass.io/v2/tide/extremes/point
- Location translation into latitude and longitude:
https://api.opencagedata.com/geocode

## Dependencies
I built this project as Flask app using Python 3.10.6. 
I've made use of the following flask libraries:
- Flask-bcrypt 1.0.1 - For password encryption
- Flask-WTForms 1.1.1 - For form design and implementation
- Flask-SQLAlchemy 3.0.5 - For database interaction and modeling

For a complete list of build dependencies please review the included requirements.txt file. 

## Local Installation and Usage

If you desire to run this application on your own local device feel free to clone this repo.
After setting up your local virtual enviroment you can install all the necessary dependencies using 
the `pip install -r requirements.txt` command or you can install them individually from that same file.
You will need to obtain three api keys to the following urls: 
- [Weatherbit](https://api.weatherbit.io/v2.0/forecast/daily)
- [Stormglass](https://api.stormglass.io/v2/tide/extremes/point)
- [OpenCageData](https://api.opencagedata.com/geocode)

This application does require the creation of an account. It is intended for planning purposes and no weather forecast
is a guarantee of actual weather conditions. 
