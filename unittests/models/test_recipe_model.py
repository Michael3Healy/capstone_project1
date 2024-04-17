import os
from unittest import TestCase
from pdb import set_trace
from models import db, User, Recipe, Ingredient
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///easy_recipes_test"

from app import app

db.create_all()

class RecipeModelTestCase(TestCase):
    """Test model for recipes"""

    def setUp(self):
        """Delete test model instances from db"""

        User.query.delete()
        Recipe.query.delete()
        Ingredient.query.delete()

    def tearDown(self):
        db.session.rollback()

    def test_recipe_model_relationships(self):
        '''Test if recipe model relationship works'''

        recipe = Recipe(recipe_title='Apple Pork Tenderloin')

        user1 = User.register(email='test@test.com', username='testuser', password='password',
                    image_url='https://tinyurl.com/29q8o28r', diet='vegan')

        user2 = User.register(email='example@example.com', username='exampleuser', password='password',
                    image_url='https://tinyurl.com/29q8o28r', diet='vegan')

        ingredient = Ingredient(ingredient_title='green apples')

        user1.recipes.append(recipe)
        user2.recipes.append(recipe)
        recipe.ingredients.append(ingredient)
        db.session.add_all([recipe, user1, user2, ingredient])
        db.session.commit()

        self.assertEqual(len(recipe.users), 2)
        self.assertEqual(len(recipe.ingredients), 1)
        self.assertEqual(recipe.users[0], user1)
        self.assertEqual(recipe.users[0].username, 'testuser')
        self.assertEqual(recipe.ingredients[0].ingredient_title, 'green apples')


