# Easy Recipes

## A recipe app that allows users to search for recipes based on ingredients and diet, and save recipes to their favorites and shopping cart.

Link to live site: [Easy Recipes](https://easy-recipes-6vwo.onrender.com)

**App Features Include:**

- User authentication
- Ability to search for recipes based on ingredients and diet
- For each recipe, users can favorite, add to shopping cart, and view the recipe details
- Profile page where users can view their favorite recipes and edit their profile, including dietary restrictions
- Shopping cart which compiles all of the ingredients from the recipes added to the cart
- Emails with shopping list sent to user's email

**User Flow:**

1. During registration, users provide basic information and dietary restrictions for use in recipe search.
2. Users browse for recipes based on ingredients and diet, saving favorites.
3. In their profile, users manage favorite recipes and add some to their shopping cart.
4. Users review and email their shopping cart to themselves.

**API Used:**

- [Spoonacular API](https://spoonacular.com/food-api)

**Technologies Used:**
 - Python
 - Flask
 - SQLAlchemy
 - PostgreSQL
 - Jinja
 - WTForms
 - JavaScript
 - Bootstrap
 - Render

**Setup Guide:**
   1. `git clone https://{your-personal-access-token}@github.com/Michael3Healy/capstone_project1.git`
   2. `cd capstone_project1`
   3. `python3 -m venv venv`
   4. `source venv/bin/activate`
   5. `pip install -r requirements.txt`
   6. Retrieve api key from [Spoonacular API](https://spoonacular.com/food-api)
   7. Retrieve app password from your gmail account
        - Go to your google account
        - Click on security
        - Turn on 2-step verification
        - Go to app passwords
        - Retrieve new password
   8. Create .env file with the following:
      - SECRET_KEY = any random string
      - SPOONACULAR_API_KEY = your spoonacular api key
      - MAIL_USERNAME = your email
      - MAIL_PASSWORD = your app password from previous step
      - MAIL_USE_TLS = True
      - MAIL_USE_SSL = False
      - MAIL_PORT = 465
      - MAIL_SERVER = 'smtp.gmail.com'
   9.  In postgres, create database called `easy_recipes`
   10. Run seed.py file
   11. Change all instances of 'https://easy-recipes-6vwo.onrender.com' to 'http://localhost:5000' in script.js
   12. `flask run`


