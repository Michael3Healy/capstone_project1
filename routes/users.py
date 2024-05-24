from flask import Blueprint, Flask, render_template, jsonify, request, flash, redirect, session, g, url_for
from food_models import Recipe, Favorites
from forms import UserEditForm
from db_init import db
from user_model import User
import requests
import os
from routes.auth import login_required
from sqlalchemy.exc import IntegrityError
from model_logic import set_allergies

API_KEY = os.environ.get('API_KEY')


users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/current')
def get_current_user():
    if g.user:
        return jsonify(g.user.serialize()), 200
    return jsonify(None), 404

@users_bp.route('/<user_id>/recipes')
def get_saved_recipes(user_id):
    # Get all saved recipes for a user as well as detailed information about each recipe

    user = User.query.get_or_404(user_id)
    recipes = ','.join(str(recipe.id) for recipe in user.recipes)
    try:  
        resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': recipes})
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"Error": "Could not get recipes"}), 500

@users_bp.route('/<user_id>/recipes', methods=['DELETE'])
def delete_saved_recipe(user_id):
    # Delete a saved recipe from user's list of saved recipes

    user = User.query.get_or_404(user_id)
    recipe_id = request.json['recipe_id']
    recipe = Recipe.query.get_or_404(recipe_id)
    user.recipes.remove(recipe)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"Result": "Deleted"}), 200

@users_bp.route('/<user_id>/recipes', methods=['POST'])
def save_recipe(user_id):
    # Save a recipe to user's list of saved recipes

    user = User.query.get_or_404(user_id)
    recipe_id = request.json['recipe_id']
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        recipe = Recipe(id=recipe_id)
    user.recipes.append(recipe)
    db.session.commit()
    return jsonify({"Result": "Saved"})

@users_bp.route('/<user_id>/cart', methods=['PATCH'])
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

@users_bp.route('/<user_id>/cart', methods=['GET'])
def get_shopping_cart(user_id):
    # Get all recipes in user's shopping cart

    user = User.query.get_or_404(user_id)
    shopping_cart = Favorites.query.filter(Favorites.user_id==user.id, Favorites.in_shopping_cart==True).all()
    recipe_ids = [recipe.recipe_id for recipe in shopping_cart]
    return jsonify(recipe_ids)

@users_bp.route('/details')
@login_required
def get_user_details():
    '''Page giving details on user. Includes diet, allergies, and saved/favorite recipes'''
    return render_template('users/details.html')

@users_bp.route('/edit', methods=["GET", "POST"])
@login_required
def edit_user():
    '''Edit user details'''

    form = UserEditForm(obj=g.user)
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            try: 
                # Update user details or keep the same if no input
                g.user.username = form.username.data or g.user.username
                g.user.email = form.email.data or g.user.email
                g.user.image_url = form.image_url.data or url_for('static', filename='images/default-pic.png')
                g.user.diet = form.diet.data
                allergies = form.dietary_restrictions.data
                set_allergies(allergies, g.user)
                db.session.commit()
                return redirect(url_for('users.get_user_details'))
            except IntegrityError:
                db.session.rollback()
                flash("Username/email already taken", 'danger')
                return render_template('users/edit.html', form=form)
        else:
            flash('Incorrect password', 'danger')
    return render_template('users/edit.html', form=form)

@users_bp.route('/shopping_cart')
@login_required
def show_shopping_cart():
    '''Show user's shopping cart'''

    shopping_cart = Favorites.query.filter(Favorites.user_id==g.user.id, Favorites.in_shopping_cart==True).all()
    recipe_ids = [recipe.recipe_id for recipe in shopping_cart]
    recipe_ids = ','.join(str(id) for id in recipe_ids)
    try:
        resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': recipe_ids})
        recipes = resp.json()
        return render_template('users/shopping_cart.html', recipes=recipes)
    except requests.exceptions.RequestException as e:
        flash('Could not get recipes', 'danger')
        return render_template('users/shopping_cart.html', recipes=[])