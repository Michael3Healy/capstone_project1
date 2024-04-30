import os
from flask import Flask, render_template, jsonify, request, flash, redirect, session, g, url_for
from functools import wraps
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
from forms import UserAddForm, UserEditForm, LoginForm
from models import db, connect_db, User, Favorites, Allergy, Ingredient, Recipe, set_allergies
import re
from pdb import set_trace
import requests
from secret_info import API_KEY, APP_PASSWORD

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///easy_recipes'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "ejcurbbwornhcbsir")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'easyrecipes.shopping@gmail.com'
app.config['MAIL_PASSWORD'] = APP_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.app_context().push()

connect_db(app)


# Helper Functions

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            flash("Please login first", "danger")
            return redirect("/login")
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


# API Routes requested from the frontend to retrieve info from Spoonacular API

@app.route('/recipes/random')
def get_random_recipes():
    resp = requests.get('https://api.spoonacular.com/recipes/random', params={'apiKey': API_KEY, 'number': 20})
    return jsonify(resp.json())


@app.route('/recipes/complexSearch')
def get_specific_recipes():
    include_ingredients = request.args['includeIngredients']
    exclude_ingredients = request.args['excludeIngredients']
    diet = request.args['diet']
    resp = requests.get('https://api.spoonacular.com/recipes/complexSearch', params={'apiKey': API_KEY, 'includeIngredients': include_ingredients, 
                                                                                'excludeIngredients': exclude_ingredients, 'diet': diet, 'number': 2})
    return jsonify(resp.json())


@app.route('/recipes/<int:recipe_id>/information')
def get_recipe_info(recipe_id):
    resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={'apiKey': API_KEY})
    return jsonify(resp.json())


@app.route('/recipes/info', methods=['POST'])
def get_bulk_recipe_info():
    recipe_ids = ','.join(str(id) for id in request.json.get('ids', []))
    resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': recipe_ids})
    return jsonify(resp.json())


@app.route('/users/current')
def get_current_user():
    if g.user:
        return jsonify(g.user.serialize()), 200
    return jsonify(None)


@app.route('/users/<user_id>/recipes')
def get_saved_recipes(user_id):
    # Get all saved recipes for a user
    user = User.query.get_or_404(user_id)
    recipes = ','.join(str(recipe.id) for recipe in user.recipes)
    resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': recipes})
    return jsonify(resp.json())

@app.route('/users/<user_id>/recipes', methods=['DELETE'])
def delete_saved_recipe(user_id):
    # Delete a saved recipe from user's list of saved recipes
    user = User.query.get_or_404(user_id)
    recipe_id = request.json['recipe_id']
    recipe = Recipe.query.get_or_404(recipe_id)
    user.recipes.remove(recipe)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"Result": "Deleted"}), 200

@app.route('/users/<user_id>/recipes', methods=['POST'])
def save_recipe(user_id):
    # Save a recipe to user's list of saved recipes
    user = User.query.get_or_404(user_id)
    recipe_id = request.json['recipe_id']
    saved_recipe = Recipe(id=recipe_id)
    user.recipes.append(saved_recipe)
    db.session.commit()
    return jsonify({"Result": "Saved"})


@app.route('/users/<user_id>/cart', methods=['PATCH'])
def toggle_cart_status(user_id):
    # Add/remove a recipe from user's shopping cart by toggling status in favorite_recipes table
    user = User.query.get_or_404(user_id)
    cart_item = Favorites.query.filter(Favorites.user_id==user.id, Favorites.recipe_id==request.json['recipe_id']).first()
    if cart_item.in_shopping_cart == False:
        cart_item.in_shopping_cart = True
    else:
        cart_item.in_shopping_cart = False
    db.session.commit()
    return jsonify({"Result": "Added/Removed from cart"}), 200

@app.route('/users/<user_id>/cart', methods=['GET'])
def get_shopping_cart(user_id):
    # Get all recipes in user's shopping cart
    user = User.query.get_or_404(user_id)
    shopping_cart = Favorites.query.filter(Favorites.user_id==user.id, Favorites.in_shopping_cart==True).all()
    recipe_ids = [recipe.recipe_id for recipe in shopping_cart]
    return jsonify(recipe_ids)

# Authentication Routes

@app.route('/register', methods=["GET", "POST"])
def register():
    """Handle user registration. Create new user and add to DB. Redirect to home page.
    If form not valid, render form. If there already is a user with that username: flash message
    and render form again."""

    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.register(username=form.username.data, password=form.password.data, email=form.email.data, image_url=form.image_url.data or User.image_url.default.arg,
                                    diet = form.diet.data, allergies=form.allergies.data)
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


# Home Route

@app.route('/')
def home_page():
    '''Renders home page, the place to search for recipes'''
    return render_template('home.html')


# User Routes

@app.route('/users/details')
@login_required
def get_user_details():
    '''Page giving details on user. Includes diet, allergies, and saved/favorite recipes'''
    return render_template('users/details.html')


@app.route('/users/edit', methods=["GET", "POST"])
@login_required
def edit_user():
    '''Edit user details'''
    form = UserEditForm(obj=g.user)
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.username = form.username.data or g.user.username
            g.user.email = form.email.data or g.user.email
            g.user.image_url = form.image_url.data or url_for('static', filename='images/default-pic.png')
            g.user.diet = form.diet.data
            allergies = form.dietary_restrictions.data
            set_allergies(allergies, g.user)
            
            db.session.commit()
            return redirect(url_for('get_user_details'))
        flash('Incorrect password', 'danger')
    return render_template('users/edit.html', form=form)


@app.route('/users/shopping_cart')
@login_required
def show_shopping_cart():
    '''Show user's shopping cart'''
    shopping_cart = Favorites.query.filter(Favorites.user_id==g.user.id, Favorites.in_shopping_cart==True).all()
    recipe_ids = [recipe.recipe_id for recipe in shopping_cart]
    recipe_ids = ','.join(str(id) for id in recipe_ids)
    resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': recipe_ids})
    recipes = resp.json()
    return render_template('users/shopping_cart.html', recipes=recipes)

@app.route('/send_email', methods=['POST'])
def send_email():
    shopping_cart = Favorites.query.filter(Favorites.user_id==g.user.id, Favorites.in_shopping_cart==True).all()
    recipe_ids = [recipe.recipe_id for recipe in shopping_cart]
    string_recipe_ids = ','.join(str(id) for id in recipe_ids)
    resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': string_recipe_ids})
    recipes = resp.json()
    rendered_template = render_template('users/email_template.html', recipes=recipes)
    msg = Message('Your Shopping Cart',
                    sender="easyrecipes.shopping@gmail.com",
                    recipients=[g.user.email])
    msg.html = rendered_template
    mail.send(msg)
    flash('Email sent!', 'success')
    return redirect(url_for('show_shopping_cart'))

# Recipe Routes

@app.route('/recipes/<int:recipe_id>/details')
def show_recipe_details(recipe_id):
    # Shows details about recipe (instructions, summary, video, etc.)
    resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={'apiKey': API_KEY})
    results = resp.json()
    
    # Get ingredient name, unit, and amount for each ingredient in recipe
    ingredient_results = results["extendedIngredients"]
    ingredients = []
    for ingredient in ingredient_results:
        ingredient_tuple = (ingredient["name"], ingredient["measures"]["us"]["amount"], ingredient["unit"])
        ingredients.append(ingredient_tuple)
    title = results['title']
    prep_time = results['readyInMinutes']
    instructions = results['instructions']
    summary = results['summary']
    image = results['image']
    source_url = results['sourceUrl']

    clean_summary = re.sub('<[^>]+>', '', summary)
    clean_instructions = re.sub('<[^>]+>', '', instructions)

    return render_template('recipes/details.html', ingredients=ingredients, title=title, prep_time=prep_time, instructions=clean_instructions,
                            summary=clean_summary, image=image, source_url=source_url)


    