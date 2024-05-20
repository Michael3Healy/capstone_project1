from db_init import db

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