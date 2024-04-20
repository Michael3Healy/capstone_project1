from app import app
from models import db, User, Recipe, Ingredient

db.drop_all()
db.create_all()

user1 = User.register(email='example@example.com', username='example_user', password='password', 
        diet='vegan', image_url='https://tinyurl.com/29q8o28r')

recipe1 = Recipe(id=1, recipe_title='Slow Cooker Apple Pork Tenderloin')
recipe2 = Recipe(id=2, recipe_title='Slow Cooker Apple Pork as;dlfkjasdl;k')

ingredient1 = Ingredient(ingredient_title='beef broth')
ingredient2 = Ingredient(ingredient_title='pork tenderloin')
ingredient3 = Ingredient(ingredient_title='apple slicer')
ingredient4 = Ingredient(ingredient_title='green apples')

user1.recipes.append(recipe1)
user1.allergies.append(ingredient2)
recipe1.ingredients.append(ingredient1)
recipe1.ingredients.append(ingredient2)
recipe1.ingredients.append(ingredient3)
recipe1.ingredients.append(ingredient4)

db.session.add_all([user1, recipe1, recipe2, ingredient1, ingredient2, ingredient3, ingredient4])
db.session.commit()