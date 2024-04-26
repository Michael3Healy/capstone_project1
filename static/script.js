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
		// Check the URL path to determine which page you're on
		if (window.location.pathname === '/') {
			// Attach event listener to search button (home page)
			this.recipeSearchBtn.addEventListener('click', this.getSpecificRecipes.bind(this));
			// Await the creation of the user
			this.curr_user = await User.makeUser();
		} else if (window.location.pathname === '/users/details') {
			// If on the user favorites page, show user favorites
			await this.showUserFavorites();
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
		const loadingSpinner = document.createElement('i');
		loadingSpinner.classList.add('fa-solid', 'fa-spinner', 'fa-spin-pulse');
		document.querySelector(section).append(loadingSpinner);
	}

	hideLoadingView() {
		document.querySelector('.fa-spinner').remove();
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

	async seedDatabase() {
		const randomRecipes = await this.getRandomRecipes();
		this.recipes = randomRecipes;
		this.makeRecipes();
		const serializedRecipes = this.recipes.map(recipe => recipe.serialize());
		axios.post('http://127.0.0.1:5000/recipes/seed', { recipes: serializedRecipes });
	}

	async getRecipesFromDatabase() {
		const response = await axios.get('http://127.0.0.1:5000/users/1/recipes');
		this.recipes = response.data;
		this.generateHtmlMarkup(this.resultsSection);
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
			if (ingredients[0]) {
				ingredients[0] = ingredients[0].join(',');
			}
			if (ingredients[1]) {
				ingredients[1] = ingredients[1].join(',');
			}
			const allRecipes = await axios.get(`http://127.0.0.1:5000/recipes/complexSearch?includeIngredients=${ingredients[0]}&excludeIngredients=${ingredients[1]}&diet=${diet}`);
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
			const response = await axios.get('http://127.0.0.1:5000/recipes/random');
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
		const response = await axios.post('http://127.0.0.1:5000/recipes/info', { ids: recipeIds });
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

	generateHtmlMarkup(section) {
		// Generate HTML markup for each recipe

		let allRecipesMarkup = '';
		for (let recipe of this.recipes) {
			const shortenedSummary = recipe.summary.slice(0, 302 - recipe.title.length) + '...';

			// Change markup based on whether recipe is a favorite or not
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

			// Generate HTML markup for each recipe
			const recipeMarkup = `<div class="col-3 mt-3 recipe"> \
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
		this.addBtnEventListeners();
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

	showErrorMsg(section, text) {
		// Show error message

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
		const response = await axios.get(`http://127.0.0.1:5000/recipes/${this.id}/information`);
		const recipeInfo = response.data;
		this.title = recipeInfo.title;
		this.cuisine = recipeInfo.cuisines;
		this.summary = recipeInfo.summary;
		this.instructions = recipeInfo.instructions;
		this.sourceUrl = recipeInfo.sourceUrl;
		this.prepTime = recipeInfo.readyInMinutes;
		this.image = recipeInfo.image;
	}

	serialize() {
		return {
			id: this.id,
			title: this.title,
			cuisine: this.cuisine,
			summary: this.summary,
			instructions: this.instructions,
			sourceUrl: this.sourceUrl,
			prepTime: this.prepTime,
			image: this.image,
		};
	}
}

class User {
	constructor(id, email, username, image_url, diet, recipes, allergies) {
		this.id = id;
		this.email = email;
		this.username = username;
		this.image_url = image_url;
		this.diet = diet;
		this.recipes = recipes;
		this.allergies = allergies;
		this.shoppingCart = [];

		this.favoriteRecipeIds = [];
		this.getShoppingCart();
		this.getRecipes();
	}

	async getRecipes() {
		// Backend route to retrieve user's favorite recipes
		const response = await axios.get(`http://127.0.0.1:5000/users/${this.id}/recipes`);
		this.favoriteRecipeIds = response.data.map(recipe => recipe.id);
		this.recipes = response.data;
	}

	async getShoppingCart() {
		// Backend route to retrieve user's shopping cart
		const response = await axios.get(`http://127.0.0.1:5000/users/${this.id}/cart`);
		this.shoppingCart = response.data;
	}


	// static getUserIdFromUrl() {
	//     const regex = /\/users\/(\d+)\/details/;
	//     const match = window.location.pathname.match(regex);
	//     if (match && match[1]) {
	//         const id = parseInt(match[1]); // Extract and parse the user ID from the URL
	// 		return id
	//     }
	//     return null;
	// }

	static async getCurrentUser() {
		// Get current user from backend
		const user = await axios.get(`http://127.0.0.1:5000/users/current`);
		if (user != {}) {
			return user.data;
		}
		return null;
	}

	static async makeUser() {
		// Create a new user instance
		const user = await User.getCurrentUser();
		if (user) {
			const newUser = new User(user.id, user.email, user.username, user.image_url, user.diet, user.recipes, user.allergies);
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
		await axios.delete(`http://127.0.0.1:5000/users/${this.id}/recipes`, { data: { recipe_id: recipeId } });
		const indexToRemove = this.favoriteRecipeIds.indexOf(parseInt(recipeId));
		this.favoriteRecipeIds.splice(indexToRemove, 1);
	}

	async addFavorite(recipeId) {
		// Add recipe to user's favorites
		const recipe = new Recipe(recipeId);
		await recipe.getInfo();
		await axios.post(`http://127.0.0.1:5000/users/${this.id}/recipes`, { recipe_id: recipe.id });
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
		await axios.patch(`http://127.0.0.1:5000/users/${this.id}/cart`, { recipe_id: recipeId });
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

let home = new RecipeSearch();
// home.seedDatabase();
// home.getRecipesFromDatabase();
