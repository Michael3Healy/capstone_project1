from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect db to Flask app"""
    db.init_app(app)

class User(db.Model):
    '''User Class'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, default="/static/images/default-pic.png")

    diet = db.Column(db.Text)

    recipes = db.relationship('Recipe', secondary='users_recipes', cascade='all, delete', backref='users')

    allergies = db.relationship('Ingredient', secondary='allergies', cascade='all, delete', backref='users')

    @classmethod
    def register(cls, username, email, password, image_url, diet):
        """Register user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            diet=diet
        )

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

class Users_Recipes(db.Model):
    '''Connects Users to saved/favorite Recipes'''

    __tablename__ = 'users_recipes'

    id = db.Column(db.Integer, primary_key=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

class Recipe(db.Model):
    '''Recipe Class'''

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)

    recipe_title = db.Column(db.Text, nullable=False, unique=True)

    cuisine = db.Column(db.Text)

    ingredients = db.relationship('Ingredient', secondary='recipes_ingredients', cascade='all, delete', backref='recipes')

class Recipes_Ingredients(db.Model):
    '''Connects Recipes to Ingredients. Helpful for tracking which ingredients
    used in which recipes'''

    __tablename__ = 'recipes_ingredients'

    id = db.Column(db.Integer, primary_key=True)

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id', ondelete='CASCADE'))

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'))

class Ingredient(db.Model):
    '''Ingredient Class'''

    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    
    ingredient_title = db.Column(db.Text, nullable=False, unique=True)

class Allergy(db.Model):
    '''Connects Ingredients to Users. Used for tracking allergies'''

    __tablename__ = 'allergies'

    id = db.Column(db.Integer, primary_key=True)

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id', ondelete='CASCADE'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))