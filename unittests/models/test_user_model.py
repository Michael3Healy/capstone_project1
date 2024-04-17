import os
from unittest import TestCase
from pdb import set_trace
from models import db, User, Recipe, Ingredient
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///easy_recipes_test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test model for users"""

    def setUp(self):
        """Delete test model instances from db"""

        User.query.delete()
        Recipe.query.delete()
        Ingredient.query.delete()

    def tearDown(self):
        db.session.rollback()

    def test_user_model_relationships(self):
        '''Test if user model relationships work (recipes, allergies)'''

        user = User(email='test@test.com', username='testuser', password='password')

        recipe = Recipe(recipe_title='Apple Pork Tenderloin')

        ingredient1 = Ingredient(ingredient_title='green apples')

        ingredient2 = Ingredient(ingredient_title='pork tenderloin')

        user.recipes.append(recipe)
        user.allergies.append(ingredient1)
        user.allergies.append(ingredient2)

        db.session.add_all([user, recipe, ingredient1, ingredient2])
        db.session.commit()

        self.assertEqual(len(user.recipes), 1)
        self.assertEqual(len(user.allergies), 2)


    def test_valid_registration(self):
        '''Test if User.register creates user with valid inputs'''

        valid_user = User.register(email='test@test.com', username='testuser', password='password',
                    image_url='https://tinyurl.com/29q8o28r', diet='vegan')
        
        db.session.add(valid_user)
        db.session.commit()

        self.assertIsNotNone(valid_user)

    def test_invalid_registration(self):
        '''Test if User.register creates user with invalid input (null email)'''

        invalid_user = User.register(
            email=None,
            username='noemailuser',
            password="failed_email",
            image_url='https://tinyurl.com/29q8o28r',
            diet='vegan'
        )
        db.session.add(invalid_user)

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_authentication(self):
        '''Test if User.authenticate correctly returns a user or False'''

        valid_user = User.register(email='test@test.com', username='testuser', password='password',
                    image_url='https://tinyurl.com/29q8o28r', diet='vegan')
        db.session.add(valid_user)

        auth_check_valid = User.authenticate('testuser', 'password')
        auth_check_invalid_username = User.authenticate('invalid_username', 'password')
        auth_check_invalid_password = User.authenticate('testuser', 'invalid_password')

        self.assertEqual(auth_check_valid, valid_user)
        self.assertFalse(auth_check_invalid_username)
        self.assertFalse(auth_check_invalid_password)