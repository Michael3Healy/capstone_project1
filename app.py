import os
from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_mail import Mail, Message
from user_model import User
from db_init import connect_db, db
from food_models import Favorites
from routes.users import users_bp
import requests
from routes.auth import login_required, do_login, do_logout, auth_bp, CURR_USER_KEY
from routes.recipes import recipes_bp

app = Flask(__name__)

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(auth_bp)
app.register_blueprint(recipes_bp, url_prefix='/recipes')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///easy_recipes')

app.secret_key = os.environ.get('SECRET_KEY')
API_KEY = os.environ.get('API_KEY')

# Email Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.app_context().push()

connect_db(app)

# Before each request, add user to Flask global if logged in
@app.before_request
def add_user_to_g():
    '''If logged in, add curr user to Flask global for easier access in templates and view functions.'''

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

@app.route('/')
def home_page():
    '''Renders home page, the place to search for recipes'''
    if not g.user:
        return redirect('/login')
    return render_template('home.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    # Send email to user with shopping cart

    # Get recipes in shopping cart
    shopping_cart = Favorites.query.filter(Favorites.user_id==g.user.id, Favorites.in_shopping_cart==True).all()
    recipe_ids = [recipe.recipe_id for recipe in shopping_cart]
    string_recipe_ids = ','.join(str(id) for id in recipe_ids)
    try:
        resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': string_recipe_ids})
        recipes = resp.json()

        # Render email template and send email
        rendered_template = render_template('users/email_template.html', recipes=recipes)
        msg = Message('Your Shopping Cart', sender="easyrecipes.shopping@gmail.com", recipients=[g.user.email])
        msg.html = rendered_template
        mail.send(msg)
        flash('Email sent!', 'success')
        return redirect(url_for('show_shopping_cart'))
    except requests.exceptions.RequestException as e:
        flash('Could not get recipes', 'danger')
        return redirect(url_for('show_shopping_cart'))