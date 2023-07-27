from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class SignUpForm(FlaskForm):
    """Form for inital user registration"""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class PreferenceForm(FlaskForm):
    """Form for establishing a user's preferences. I will 
    also probably use this form to edit preferences as well. """

    temp_unit = SelectField('Temperature Units', choices=[('F', 'Fahrenheit'), ('C', 'Celcius')])

    air_temp = IntegerField('Air Temp', validators=[DataRequired()])

    tide_pref = SelectField('Tidal Preference', choices=[('Incoming', 'Incoming'), ('Outgoing', 'outgoing')])

    time_of_day = SelectField('Time of Day', choices=[('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Evening')])

    forecast_length = SelectField('Length of Forecast', choices=[(3, 3), (7,7), (10,10), (14,14)])

    location = StringField('Location')