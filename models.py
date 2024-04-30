from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import re
from pdb import set_trace

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect db to Flask app"""
    db.init_app(app)

class User(db.Model):
    '''User Class'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, default="/static/images/default-pic.png")

    diet = db.Column(db.Text)

    dietary_restrictions = db.Column(db.Text)

    allergies = db.relationship('Ingredient', backref='users', secondary='allergies', cascade='all, delete')

    recipes = db.relationship('Recipe', backref='users', secondary='favorite_recipes', cascade='all, delete')

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'image_url': self.image_url,
            'diet': self.diet,
            'dietary_restrictions': self.dietary_restrictions,
            'recipes': [recipe.id for recipe in self.recipes],
            'allergies': [allergy.id for allergy in self.allergies]
        }

    @classmethod
    def register(cls, username, email, password, image_url, diet, allergies):
        """Register user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            diet=diet,
            dietary_restrictions=''
        )
        set_allergies(allergies, user)
        
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`. If can't find matching user (or if password is wrong), returns False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Favorites(db.Model):
    '''Tracks users' saved recipes.'''

    __tablename__ = 'favorite_recipes'

    id = db.Column(db.Integer, primary_key=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='cascade'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    in_shopping_cart = db.Column(db.Boolean, default=False)


class Allergy(db.Model):
    '''Tracks ingredients that users are allergic to. Used in "excludeIngredients" parameter of API call'''

    __tablename__ = 'allergies'

    id = db.Column(db.Integer, primary_key=True)

    ingredient_id= db.Column(db.Text, db.ForeignKey('ingredients.id', ondelete='cascade'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)


class Ingredient(db.Model):
    '''Ingredients in the system'''

    __tablename__ = 'ingredients'

    id = db.Column(db.Text, primary_key=True)

class Recipe(db.Model):

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)



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
        db.session.commit()

def add_dietary_restrictions(index, user, allergy):
    '''Add dietary restrictions to user'''
    if index == 0:
        user.dietary_restrictions = allergy
    else:
        user.dietary_restrictions = user.dietary_restrictions + ', ' + allergy
    db.session.commit()