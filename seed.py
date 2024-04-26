from app import app
from models import db, User, Allergy

db.drop_all()
db.create_all()

user1 = User.register(email='example@example.com', username='example_user', password='password', 
        diet='vegan', image_url='https://tinyurl.com/29q8o28r', allergies='peanuts')


db.session.add(user1)
db.session.commit()