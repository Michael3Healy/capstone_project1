import os
from unittest import TestCase
from pdb import set_trace
from models import db, User, Recipe, Ingredient
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///easy_recipes_test"

from app import app

db.create_all()

class IngredientModelTestCase(TestCase):
    """Test model for ingredients"""

    def setUp(self):
        """Delete test model instances from db"""

        User.query.delete()
        Recipe.query.delete()
        Ingredient.query.delete()

    def tearDown(self):
        db.session.rollback()

    def test_ingredient_model_relationships(self):
        '''Test if ingredient model relationship works'''

        recipe = Recipe(recipe_title='Apple Pork Tenderloin')

        user1 = User.register(email='test@test.com', username='testuser', password='password',
                    image_url='https://tinyurl.com/29q8o28r', diet='vegan')

        user2 = User.register(email='example@example.com', username='exampleuser', password='password',
                    image_url='https://tinyurl.com/29q8o28r', diet='vegan')

        ingredient = Ingredient(ingredient_title='green apples')

        user1.allergies.append(ingredient)
        user2.allergies.append(ingredient)
        recipe.ingredients.append(ingredient)
        
        db.session.add_all([recipe, user1, user2, ingredient])
        db.session.commit()

        self.assertEqual(len(ingredient.users), 2)
        self.assertEqual(len(ingredient.recipes), 1)
        self.assertEqual(ingredient.users[0], user1)
        self.assertEqual(user1.allergies[0].ingredient_title, 'green apples')


