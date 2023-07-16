from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """Basic user model"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    first_name = db.Column(db.String,
                           nullable=False)
    
    last_name = db.Column(db.String,
                          nullable=False)
    username = db.Column(db.String,
                         nullable=False,
                         unique=True)
    
    password = db.Column(db.String,
                         nullable=False)
    
    location = db.Column(db.String,
                         nullable=False)
    

class Tide(db.Model):
    """Tidal model """

    __tablename__ = 'tides'

    id = db.Column(db.Integer,
                   primary_key=True)
    
    location = db.Column(db.String,
                         nullable=False)
    
    time_span = db.Column(db.DateTime,
                          nullable=False,
        default=datetime.utcnow())


class Weather(db.Model):
    """Weather model"""

    __tablename__ = "weather"

    id =  db.Column(db.Integer,
                    primary_key=True)
    
    location = db.Column(db.String,
                         nullable=False)
    
    time_span = db.Column(db.DateTime,
                          nullable=False,
        default=datetime.utcnow())

class Preference(db.Model):
    """This is meant to bring together a users 
    tidal and weather from location"""

    __tablename__ = "preferences"

    weather_id = db.Column(db.Integer,
                           db.ForeignKey('weather.id', ondelete='cascade'),
                           primary_key=True)
    
    tide_id = db.Column(db.Integer,
                        db.ForeignKey('tides.id', ondelete='cascade'),
                        primary_key=True)