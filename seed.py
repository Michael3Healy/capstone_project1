from app import app
from food_models import Recipe, Favorites, Allergy, Ingredient
from db_init import db
from user_model import User

db.drop_all()
db.create_all()

user1 = User.register(email='example@example.com', username='example_user', password='password', 
        diet='vegan', image_url='https://tinyurl.com/29q8o28r', allergies='peanuts')


db.session.add(user1)
db.session.commit()