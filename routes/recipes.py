from flask import g, flash, redirect
from flask import Blueprint, Flask, render_template, jsonify, request, flash, redirect, session, g, url_for
from food_models import Recipe, Favorites
from forms import UserEditForm, UserAddForm, LoginForm
from db_init import db
from user_model import User
import requests
import os
from sqlalchemy.exc import IntegrityError
from model_logic import set_allergies
import re

recipes_bp = Blueprint('recipes', __name__, template_folder='templates')

API_KEY = os.environ.get('API_KEY')

@recipes_bp.route('/random')
def get_random_recipes():
    # Get 16 random recipes

    try:
        resp = requests.get('https://api.spoonacular.com/recipes/random', params={'apiKey': API_KEY, 'number': 16})
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"Error": "Could not get recipes"}), 500


@recipes_bp.route('/complexSearch')
def get_specific_recipes():
    # Get recipes based on user's search parameters

    include_ingredients = request.args['includeIngredients']
    exclude_ingredients = request.args['excludeIngredients']
    diet = request.args['diet']
    try:
        resp = requests.get('https://api.spoonacular.com/recipes/complexSearch', params={'apiKey': API_KEY, 'includeIngredients': include_ingredients, 
                                                                                'excludeIngredients': exclude_ingredients, 'diet': diet, 'number': 8})
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"Error": "Could not get recipes"}), 500

@recipes_bp.route('/<int:recipe_id>/information')
def get_recipe_info(recipe_id):
    # Get detailed information about a specific recipe
    try:
        resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={'apiKey': API_KEY})
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"Error": "Could not get recipe info"}), 500

@recipes_bp.route('/info', methods=['POST'])
def get_bulk_recipe_info():
    # Get detailed information about multiple recipes

    recipe_ids = ','.join(str(id) for id in request.json.get('ids', []))
    try:
        resp = requests.get('https://api.spoonacular.com/recipes/informationBulk', params={'apiKey': API_KEY, 'ids': recipe_ids})
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"Error": "Could not get recipes info"}), 500

@recipes_bp.route('/<int:recipe_id>/details')
def show_recipe_details(recipe_id):
    # Shows details about recipe (instructions, summary, video, etc.)
    
    try:
        resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={'apiKey': API_KEY})
        results = resp.json()
        title, prep_time, instructions, summary, image, source_url = results['title'], results['readyInMinutes'], results['instructions'], results['summary'], results['image'], results['sourceUrl']
        clean_summary = re.sub('<[^>]+>', '', summary)
        clean_instructions = re.sub('<[^>]+>', '', instructions)

        return render_template('recipes/details.html', title=title, prep_time=prep_time, instructions=clean_instructions,
                                summary=clean_summary, image=image, source_url=source_url)
    except requests.exceptions.RequestException as e:
        flash('Could not get recipe details', 'danger')
        return redirect('/')