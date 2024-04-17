import os
from flask import Flask, render_template, jsonify, request, flash, redirect, session, g, url_for
from functools import wraps
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, UserEditForm, LoginForm
from models import db, connect_db, User, Recipe, Ingredient
from pdb import set_trace

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///easy_recipes'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "ejcurbbwornhcbsir")

app.app_context().push()

connect_db(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global for easier access in templates and view functions."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user. Boolean used in view functions to check if logout actually took place"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        return True
    return False


@app.route('/')
def home_page():
    '''Renders home page, the place to search for recipes'''
    return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    """Handle user registration. Create new user and add to DB. Redirect to home page.
    If form not valid, render form. If there already is a user with that username: flash message
    and render form again."""

    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                diet = form.diet.data
            )
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash("Username/email already taken", 'danger')
            return render_template('users/register.html', form=form)

        do_login(user)
        return redirect("/")
    else:
        return render_template('users/register.html', form=form)
        

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    '''Handle user logout'''
    if do_logout():
        flash('Successfully logged out', 'success')
    else:
        flash('Must be logged in first', 'danger')
    return redirect(url_for('login'))


@app.route('/user/details')
@login_required
def user_details():
    '''Page giving details on user. Includes diet, allergies, and saved/favorite recipes'''
    return render_template('users/details.html')

