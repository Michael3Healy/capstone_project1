from flask import g, flash, redirect
from functools import wraps
from flask import Blueprint, Flask, render_template, jsonify, request, flash, redirect, session, g, url_for
from food_models import Recipe, Favorites
from forms import UserEditForm, UserAddForm, LoginForm
from db_init import db
from user_model import User
import requests
import os
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, template_folder='templates')

CURR_USER_KEY = "curr_user"

# Decorator to require login for certain routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            flash("Please login first", "danger")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Login and Logout Functions to update session
def do_login(user):
    '''Log in user.'''

    session[CURR_USER_KEY] = user.id


def do_logout():
    '''Logout user. Boolean used in view functions to check if logout actually took place'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        return True
    return False

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    '''Handle user registration: Create new user and add to DB. Redirect to home page.'''

    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.register(username=form.username.data, password=form.password.data, email=form.email.data, image_url=form.image_url.data or User.image_url.default.arg,
                                    diet = form.diet.data, allergies=form.allergies.data)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username/email already taken", 'danger')
            return render_template('users/register.html', form=form)
        do_login(user)
        return redirect("/")
    else:
        return render_template('users/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    '''Handle user logout'''

    if do_logout():
        flash('Successfully logged out', 'success')
    else:
        flash('Must be logged in first', 'danger')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    '''Handle user login.'''

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials", 'danger')
    return render_template('users/login.html', form=form)