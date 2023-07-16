from flask import Flask, redirect, render_template, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import SignUpForm, LoginForm
from sqlalchemy.exc import IntegrityError
from models import User, Weather, Tide, Preference, db, connect_db

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


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def home_page():
    """Show homepage: either for a logged in user or for 
    an anon user
    """
    if g.user:
        user = g.user

        return render_template('home.html', user=user)
    else:
        return render_template('home-anon.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.is_submitted() and form.validate():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                location=form.location.data
            )
            
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('sign-up.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('sign-up.html', form=form)


@app.route('/login')
def login():
    form = LoginForm()

    return render_template('login.html', form=form)