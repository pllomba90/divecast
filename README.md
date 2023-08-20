#Divecast
This is a weather and tide focused SCUBA dive planning application. The user is prompted to input location and tide preferences.
The application querys the weather and tidal conditions for the selected location and then provides an ideal time for the user to 
plan on entering the water if there is such a time that meets the user's preferences. 
I will be querying the following APIs for this project:
Weather conditions:
https://api.weatherbit.io/v2.0/forecast/daily
Tidal conditions:
https://api.stormglass.io/v2/tide/extremes/point
Location translation into latitude and longitude:
https://api.opencagedata.com/geocode

This project is mainly built on Python3. There is the littlest bit of Javascript for the front end functionality 
and as I work to improve it I'm sure I will use more Javascript to beautify the front end. I used a PSQL database as my user 
database and a Redis server as my cache for short term information storing and to speed up certain aspects of the project. This 
is a project I intend to tinker with for some time so I will certainly be adding more information here. I will have to use Docker to
launch it on Render.com as they don't support this iteration of Python. 