from flask import Flask, redirect, render_template, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import SignUpForm, LoginForm, PreferenceForm
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
    session['username'] = user.username


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        session['username'] = None


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

    if form.is_submitted() and form.validate():

        new_pref = Preference.create_preference(
            user_id = g.user.id,
            temp_unit=form.temp_unit.data,
            air_temp=form.air_temp.data,
            tide_pref=form.tide_pref.data,
            time_of_day=form.time_of_day.data
        )

        db.session.commit()
        return redirect('/')
    else:
        return render_template('initial_prefs.html', form=form)
    
@app.route('/user/edit', methods=['GET', 'POST'])
def edit_user():

    user = g.user

    form = PreferenceForm(obj=user.preference)

    if form.is_submitted() and form.validate():

        preference = user.preference
        preference.temp_unit = form.temp_unit.data
        preference.air_temp = form.air_temp.data
        preference.tide_pref = form.tide_pref.data
        preference.time_of_day = form.time_of_day.data
       
        db.session.commit()
        return redirect('/')
    else:

        return render_template('edit.html', user=user, form=form)

@app.route('/logout')
def logout():

    do_logout()

    return render_template('home-anon.html')
