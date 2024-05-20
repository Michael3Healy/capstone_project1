from db_init import db
from model_logic import set_allergies
from food_models import Ingredient, Recipe, Favorites, Allergy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model):
    '''User Class'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, default="/static/images/default-pic.png")

    diet = db.Column(db.Text)

    # Dietary restrictions are text version of allergies for easier display
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
        '''Register user. Hashes password and adds user to system.'''

        # bcrypt.generate_password_hash adds salt, so no need to add it explicitly
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
        db.session.commit()
        
        return user

    @classmethod
    def authenticate(cls, username, password):
        '''Find user with `username` and `password`. If can't find matching user (or if password is wrong), returns False.'''

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False





