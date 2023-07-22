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
    
    email = db.Column(db.String,
                    nullable=False)
    
    preference = db.relationship('Preference', 
                                 backref='users', 
                                 uselist=False)
    
    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`. Basic login method.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    

    

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

    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id'), 
                        primary_key=True)
    
    user = db.relationship('User', 
                           backref='preferences', 
                           uselist=False)
    
    temp_unit = db.Column(db.String,
                          default='f',
                          nullable=False)
    
    air_temp = db.Column(db.Integer,
                         nullable=False)
    
    tide_preference = db.Column(db.String,
                                default='Outgoing',
                                nullable=False)
    
    time_of_day = db.Column(db.String,
                            default='Afternoon',
                            nullable=False)
    
    location = db.Column(db.String,
                         nullable=False)
    latitude = db.Column(db.Float, 
                         nullable=True)

    longitude = db.Column(db.Float, 
                          nullable=True)
    
    @classmethod
    def create_preference(cls, user_id, temp_unit, air_temp, tide_pref, time_of_day, location, latitude, longitude):
        """Method to create a users new preferences"""

        new_pref = Preference(
        user_id=user_id,
        temp_unit=temp_unit,
        air_temp=air_temp,
        tide_preference=tide_pref,
        time_of_day=time_of_day,
        location=location,
        latitude=latitude, 
        longitude=longitude
    )

        db.session.add(new_pref)

        return new_pref