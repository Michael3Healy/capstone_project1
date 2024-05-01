class RecipeSearch {
	constructor() {
		this.resultsSection = document.querySelector('#search_results');
		this.recipeSection = document.querySelectorAll('.recipe');
		this.includeIngredientInput = document.querySelector('#ingredient_list_include');
		this.excludeIngredientInput = document.querySelector('#ingredient_list_exclude');
		this.dietInput = document.querySelector('#diet');
		this.recipeSearchBtn = document.querySelector('#submit_search');

		this.recipes = [];

		this.initialize();
	}

	async initialize() {
		// Initialize the page

		if (window.location.pathname === '/') {
			this.recipeSearchBtn.addEventListener('click', this.getSpecificRecipes.bind(this)); // Attach event listener to search button (home page)
			this.curr_user = await User.makeUser(); // Await the creation of the user
		} else if (window.location.pathname === '/users/details') {
			await this.showUserFavorites(); // If on the user favorites page, show user favorites
		}
	}

	addBtnEventListeners() {
		// Add event listeners to favorite and shopping cart buttons

		this.favoriteBtns = document.querySelectorAll('.favorite-btn');
		this.favoriteBtns.forEach(button => {
			if (this.curr_user === 'Not logged in') {
				button.disabled = true;
			} else {
				button.addEventListener('click', this.curr_user.toggleFavorite.bind(this.curr_user));
			}
		});
		this.cartBtns = document.querySelectorAll('.cart-btn');
		this.cartBtns.forEach(button => {
			button.addEventListener('click', this.curr_user.toggleCart.bind(this.curr_user));
		});
	}

	showLoadingView(section) {
		// Show loading spinner

		document.querySelector(section).innerHTML = '';
		const loadingSpinner = document.createElement('i');
		loadingSpinner.classList.add('fa-solid', 'fa-spinner', 'fa-spin-pulse');
		document.querySelector(section).append(loadingSpinner);
		document.querySelector('body').classList.add('hide-scroll');
	}

	hideLoadingView() {
		// Hide loading spinner

		document.querySelector('.fa-spinner').remove();
		document.querySelector('body').classList.remove('hide-scroll');
	}

	async showUserFavorites() {
		// Show user's favorite recipes

		this.showLoadingView('#user_favorites');
		if (!this.curr_user) {
			this.curr_user = await User.makeUser();
		}
		if (this.curr_user === 'Not logged in') {
			window.location.replace('/login');
			return;
		}
		await this.curr_user.getRecipes();
		this.recipes = this.curr_user.recipes;
		const userFavoritesSection = document.querySelector('#user_favorites');
		this.makeRecipes();
		this.hideLoadingView();
		this.generateHtmlMarkup(userFavoritesSection);
	}

	async getSpecificRecipes() {
		// Get recipes based on search criteria, or get random recipes

		// If no search criteria has been entered, show random recipes
		if (this.inputsEmpty()) {
			const randomRecipes = await this.getRandomRecipes();
			this.recipes = randomRecipes;
			this.makeRecipes();
			this.generateHtmlMarkup(this.resultsSection);
		} else {
			// Otherwise, show recipes based on the ingredients and diet entered
			const ingredients = this.getIngredients();
			const diet = this.dietInput.value;

			// Make include ingredients and exclude ingredients into strings for URL
			if (ingredients[0]) {
				ingredients[0] = ingredients[0].join(',');
			}
			if (ingredients[1]) {
				ingredients[1] = ingredients[1].join(',');
			}
			const allRecipes = await axios.get(`https://easy-recipes-6vwo.onrender.com/recipes/complexSearch?includeIngredients=${ingredients[0]}&excludeIngredients=${ingredients[1]}&diet=${diet}`);
			if (!this.validSearch(allRecipes)) return;
			this.recipes = allRecipes.data.results;

			// Must get additional recipe info for each recipe because complexSearch only returns basic info
			await this.getBulkRecipeInfo();

			// Make each recipe an instance of Recipe class
			this.makeRecipes();

			// Generate HTML markup for each recipe
			this.generateHtmlMarkup(this.resultsSection);
		}
	}

	inputsEmpty() {
		// Check if input fields are empty

		if (!this.includeIngredientInput.value && !this.excludeIngredientInput.value && this.dietInput.value === 'none') {
			return true;
		}
		return false;
	}

	async getRandomRecipes() {
		// Retrieve list of random recipes

		try {
			const response = await axios.get('https://easy-recipes-6vwo.onrender.com/recipes/random');
			const randomRecipes = response.data.recipes;
			return randomRecipes;
		} catch (error) {
			console.error('Error fetching random recipes:', error);
		}
	}

	makeRecipes() {
		// Turn each recipe into instance of Recipe class

		const recipeInstances = [];

		for (let recipe of this.recipes) {
			const recipeInstance = new Recipe(recipe.id, recipe.title, recipe.cuisines, recipe.summary, recipe.instructions, recipe.sourceUrl, recipe.readyInMinutes, recipe.image);
			recipeInstances.push(recipeInstance);
		}
		this.recipes = recipeInstances;
	}

	async getBulkRecipeInfo() {
		// Get additional info for each recipe

		const recipeIds = this.recipes.map(recipe => recipe.id);
		const response = await axios.post('https://easy-recipes-6vwo.onrender.com/recipes/info', { ids: recipeIds });
		const recipesInfo = response.data;
		this.recipes = recipesInfo;
	}

	getIngredients() {
		// Retrieves ingredients from input using regular expression

		const regex = /[a-zA-Z]+/g;
		const includeIngredients = this.includeIngredientInput.value.match(regex);
		const excludeIngredients = this.excludeIngredientInput.value.match(regex);
		return [includeIngredients, excludeIngredients];
	}

	getBtnMarkup(recipe) {
		// Generate HTML markup for favorite and shopping cart buttons

		let favBtnClass, favoriteToggle;
		if (this.curr_user instanceof User) {
			favoriteToggle = this.curr_user.favoriteRecipeIds.includes(recipe.id) ? 'Unfavorite' : 'Favorite';
			favBtnClass = this.curr_user.favoriteRecipeIds.includes(recipe.id) ? 'btn-danger' : 'btn-success';
		} else {
			favoriteToggle = 'Favorite';
			favBtnClass = 'btn-success';
		}
		let cartBtnMarkup = '';
			if (window.location.pathname === '/users/details') {
				const cartIconClass = this.curr_user.shoppingCart.includes(recipe.id) ? 'cart-item' : '';
				cartBtnMarkup = `<button type="button" class="btn btn-info cart-btn" data-recipe-id="${recipe.id}"><i class="fa-solid fa-cart-shopping ${cartIconClass}"></i></button>`;
			}
		return [favoriteToggle, favBtnClass, cartBtnMarkup];
	}

	generateHtmlMarkup(section) {
		// Generate HTML markup for each recipe

		this.hideErrorMsg(); // Hide error message if it exists
		let allRecipesMarkup = '';
		for (let recipe of this.recipes) {
			const shortenedSummary = recipe.summary.slice(0, 302 - recipe.title.length) + '...';

			// Change favorite/cart button text and color based on whether recipe is in user's favorites/cart
			let btnMarkup = this.getBtnMarkup(recipe);
			const favoriteToggle = btnMarkup[0];
			const favBtnClass = btnMarkup[1];
			const cartBtnMarkup = btnMarkup[2];	

			// Generate HTML markup for each recipe
			const recipeMarkup = `<div class="col-lg-3 col-md-4 col-sm-6 mt-3 recipe"> \
				<div class="card"> \
					<img src="${recipe.image}" class="card-img-top" alt="Image of Recipe"> \
					<div class="card-body"> \
						<h5 class="card-title">${recipe.title}</h5> \
						<p class="card-text"></b>${shortenedSummary}</b></p> \
						<a href="/recipes/${recipe.id}/details" class="btn btn-primary recipe-link-user">Details</a> \
						<button type="button" class="btn ${favBtnClass} favorite-btn" data-recipe-id="${recipe.id}">${favoriteToggle}</button>
						${cartBtnMarkup}
					</div> \
				</div> \
			</div>`;
			allRecipesMarkup += recipeMarkup;
		}
		section.innerHTML = allRecipesMarkup;

		// Padding added here so there is no visible div when no recipes are found
		if (section.innerHTML !== '') {
			section.classList.add('pb-3')
		}
		this.addBtnEventListeners();
		allPages.generateFruitMarkup();
	}

	validSearch(allRecipes) {
		// Check if search criteria is valid
		if (!allRecipes.data.results.length) {
			// If no recipes are found and error message not already shown, show error message
			if (!document.querySelector('.error_msg')) {
				this.showErrorMsg('.search_headers', 'No recipes found. Please try again.');
				this.resultsSection.innerHTML = '';
				return false;
			}
			return false;
		}
		return true;
	}

	hideErrorMsg() {
		if (document.querySelector('.error_msg')) {
			document.querySelector('.error_msg').remove();
		}
	}

	showErrorMsg(section, text) {

		// If error message already exists, remove it
		if (document.querySelector('.error_msg')) {
			document.querySelector('.error_msg').remove();
		}
		const error_msg = document.createElement('p');
		document.querySelector(section).append(error_msg);
		error_msg.classList.add('text-danger', 'error_msg');
		error_msg.innerText = text;
	}
}

class Recipe {
	constructor(id, title, cuisine, summary, instructions, sourceUrl, prepTime, image) {
		this.id = id;
		this.title = title;
		this.cuisine = cuisine;
		this.summary = summary;
		this.instructions = instructions;
		this.sourceUrl = sourceUrl;
		this.prepTime = prepTime;
		this.image = image;
	}

	async getInfo() {
		const response = await axios.get(`https://easy-recipes-6vwo.onrender.com/recipes/${this.id}/information`);
		const recipeInfo = response.data;
		this.title = recipeInfo.title;
		this.cuisine = recipeInfo.cuisines;
		this.summary = recipeInfo.summary;
		this.instructions = recipeInfo.instructions;
		this.sourceUrl = recipeInfo.sourceUrl;
		this.prepTime = recipeInfo.readyInMinutes;
		this.image = recipeInfo.image;
	}
}

class User {
	constructor(id, recipes) {
		this.id = id;
		this.recipes = recipes;
		this.shoppingCart = [];
		this.favoriteRecipeIds = [];
		this.getShoppingCart();
		this.getRecipes();
	}

	async getRecipes() {
		// Retrieves user's favorite recipes from backend

		const response = await axios.get(`https://easy-recipes-6vwo.onrender.com/users/${this.id}/recipes`);
		this.favoriteRecipeIds = response.data.map(recipe => recipe.id);
		this.recipes = response.data;
	}

	async getShoppingCart() {
		// Retrieves user's shopping cart from backend

		const response = await axios.get(`https://easy-recipes-6vwo.onrender.com/users/${this.id}/cart`);
		this.shoppingCart = response.data;
	}

	static async getCurrentUser() {
		// Get current user from backend

		const user = await axios.get(`https://easy-recipes-6vwo.onrender.com/users/current`);
		if (user != {}) {
			return user.data;
		}
		return null;
	}

	static async makeUser() {
		// Create a new user instance

		const user = await User.getCurrentUser();
		if (user) {
			const newUser = new User(user.id, user.recipes);
			newUser.favoriteRecipeIds = user.recipes.map(recipe => recipe.id);
			return newUser;
		} else {
			return 'Not logged in';
		}
	}

	async toggleFavorite(evt) {
		// Toggle favorite status of recipe

		const favoriteBtn = evt.target;
		const recipeId = favoriteBtn.dataset.recipeId;
		if (this.favoriteRecipeIds.includes(parseInt(recipeId))) {
			await this.removeFavorite(recipeId);
			if (window.location.pathname === '/users/details') {
				home.showUserFavorites();
			}
			favoriteBtn.classList.remove('btn-danger');
			favoriteBtn.innerText = 'Favorite';
		} else {
			await this.addFavorite(recipeId);
			favoriteBtn.classList.add('btn-danger');
			favoriteBtn.innerText = 'Unfavorite';
		}
	}

	async removeFavorite(recipeId) {
		// Remove recipe from user's favorites

		await axios.delete(`https://easy-recipes-6vwo.onrender.com/users/${this.id}/recipes`, { data: { recipe_id: recipeId } });
		const indexToRemove = this.favoriteRecipeIds.indexOf(parseInt(recipeId));
		this.favoriteRecipeIds.splice(indexToRemove, 1);
	}

	async addFavorite(recipeId) {
		// Add recipe to user's favorites

		const recipe = new Recipe(recipeId);
		await recipe.getInfo();
		await axios.post(`https://easy-recipes-6vwo.onrender.com/users/${this.id}/recipes`, { recipe_id: recipe.id });
		this.favoriteRecipeIds.push(parseInt(recipeId));
	}

	async toggleCart(evt) {
		// Add recipe to user's shopping cart

		let cartBtn;
		if (evt.target.tagName === 'I') {
			cartBtn = evt.target.parentElement;
		} else {
			cartBtn = evt.target;
		}
		const cartIcon = cartBtn.querySelector('i');
		const recipeId = cartBtn.dataset.recipeId;
		await axios.patch(`https://easy-recipes-6vwo.onrender.com/users/${this.id}/cart`, { recipe_id: recipeId });
		if (this.shoppingCart.includes(parseInt(recipeId))) {
			this.removeFromCart(recipeId);
			cartIcon.classList.remove('cart-item');
		} else {
			this.addToCart(recipeId);
			cartIcon.classList.add('cart-item');
		}
	}

	removeFromCart(recipeId) {
		const indexToRemove = this.shoppingCart.indexOf(parseInt(recipeId));
		this.shoppingCart.splice(indexToRemove, 1);
	}

	addToCart(recipeId) {
		this.shoppingCart.push(parseInt(recipeId));
	}
}

class PageStyle {
	constructor(name) {
		this.name = name;
	}

	generateFruitMarkup() {
		const fruitSectionLeft = document.querySelector('.fruit-left');
		const fruitSectionRight = document.querySelector('.fruit-right');
		let fruitMarkup = '';

		while (fruitSectionLeft.offsetHeight < Math.max(document.body.scrollHeight * 0.98, window.innerHeight * 0.9)) {
			fruitMarkup += `<p><i class="fa-solid fa-lemon fa-2xl" style="color: #FFD43B;"></i></p> \
			<p><i class="fa-solid fa-apple-whole fa-2xl" style="color: #e10505;"></i></p>`;
			fruitSectionLeft.innerHTML = fruitMarkup;
			fruitSectionRight.innerHTML = fruitMarkup;
		}
	}
}

let home = new RecipeSearch();
let allPages = new PageStyle('all');
allPages.generateFruitMarkup();