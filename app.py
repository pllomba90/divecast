from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import SignUpForm, LoginForm
from models import User, Weather, Tide, Preference, db, connect_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///divecast_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

with app.app_context():
    connect_db(app)
    db.create_all()

app.config['SECRET_KEY'] = "alwaysbetter"

debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return render_template('home-anon.html')

@app.route('/sign_up')
def sign_up():
    form = SignUpForm()
    return render_template('sign-up.html', form=form)

@app.route('/login')
def login():
    form = LoginForm()

    return render_template('login.html', form=form)