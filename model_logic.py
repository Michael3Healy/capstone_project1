from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from food_models import Ingredient
import re

def set_allergies(allergies, user):
    '''Add allergies to user. If allergy does not exist, create new ingredient and add to user. If allergy exists, add to user'''
    user.allergies = []
    user.dietary_restrictions = ''

    allergy_pattern = r'[a-zA-Z]+' # regex pattern to extract all words from allergies string
    allergies = re.findall(allergy_pattern, allergies)

    for index, allergy in enumerate(allergies):
        existing_allergy = Ingredient.query.filter(Ingredient.id==allergy).one_or_none()

        if not existing_allergy:
            new_allergy = Ingredient(id=allergy)
            user.allergies.append(new_allergy)
            add_dietary_restrictions(index, user, allergy)
        elif existing_allergy not in user.allergies:
            user.allergies.append(existing_allergy)
            add_dietary_restrictions(index, user, allergy)

def add_dietary_restrictions(index, user, allergy):
    '''Add dietary restrictions to user'''
    if index == 0:
        user.dietary_restrictions = allergy
    else:
        user.dietary_restrictions = user.dietary_restrictions + ', ' + allergy