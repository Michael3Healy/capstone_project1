import os
from unittest import TestCase
from models import Allergy, Favorites, Ingredient, Recipe, User, db, connect_db
from pdb import set_trace
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///easy_recipes_test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['Testing'] = True

db.drop_all()
db.create_all()

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test client, add sample data"""

        User.query.delete()
        Allergy.query.delete()
        Favorites.query.delete()
        Ingredient.query.delete()
        Recipe.query.delete()

        self.client = app.test_client()

        self.testuser = User.register(email='test@test.com', username='testuser', password='password',
                        image_url='https://tinyurl.com/29q8o28r', diet='vegan', allergies='peanuts')

        db.session.add(self.testuser)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_user_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/details')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)

    def test_update_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/users/edit', data={'username': 'testuser2'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2', html)

    def test_get_curr_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/users/current')

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, self.testuser.serialize())

    def test_save_recipe(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'/users/{self.testuser.id}/recipes', json={'recipe_id': 1})

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(Favorites.query.count(), 1)

    def test_delete_saved_recipe(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            recipe = Recipe(id=1)
            self.testuser.recipes.append(recipe)
            db.session.commit()
            resp = c.delete(f'/users/{self.testuser.id}/recipes', json={'recipe_id': 1 })

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(Favorites.query.count(), 0)

    def test_add_recipe_to_cart(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp1 = c.post(f'/users/{self.testuser.id}/recipes', json={'recipe_id': 1})
            resp2 = c.patch(f'/users/{self.testuser.id}/cart', json={'recipe_id': 1})

            recipe = Favorites.query.filter(Favorites.user_id==self.testuser.id, Favorites.recipe_id==1).first()

            self.assertEqual(resp2.status_code, 200)
            self.assertEqual(recipe.in_shopping_cart, True)

    def test_valid_registration(self):
        with self.client as c:
            resp = c.post('/register', json={'username': 'testuser2', 'password': 'password', 'email': 'test@example.com',
                                        'image_url': 'https://tinyurl.com/29q8o28r', 'diet': 'vegan', 'allergies': 'peanuts, kiwi'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.count(), 2)
            self.assertIn('testuser2', html)
            self.assertEqual(Allergy.query.count(), 3)
            self.assertEqual(Ingredient.query.count(), 2)

    

            
