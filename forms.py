from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length, URL, Optional


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email(message='Please enter valid email address')])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    image_url = StringField('Profile Image URL', validators=[URL(), Optional()])
    diet = SelectField('Diet', choices=[('none', 'None'), ('vegetarian', 'Vegetarian'), ('lacto_vegetarian', 'Lacto-Vegetarian'),
                                                    ('ovo_vegetarian', 'Ovo-Vegetarian'), ('vegan', 'Vegan'), ('pescetarian', 'Pescetarian'),
                                                    ('paleo', 'Paleo'), ('low_fodmap', 'Low FODMAP'), ('whole30', 'Whole30')])
    allergies = StringField('Allergies')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

class UserEditForm(FlaskForm):
    '''Form for editing a user'''
    username = StringField('Username')
    email = StringField('E-mail', validators=[Email(message='Please enter valid email address'), Optional()])
    image_url = StringField('(Optional) Image URL')
    diet = SelectField('Diet', choices=[('none', 'None'), ('vegetarian', 'Vegetarian'), ('lacto_vegetarian', 'Lactor-Vegetarian'),
                                                    ('ovo_vegetarian', 'Ovo-Vegetarian'), ('vegan', 'Vegan'), ('pescetarian', 'Pescetarian'),
                                                    ('paleo', 'Paleo'), ('low_fodmap', 'Low FODMAP'), ('whole30', 'Whole30')])
    dietary_restrictions = StringField('Allergies')

    password = PasswordField('Password', validators=[Length(min=6)])