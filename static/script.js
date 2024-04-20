class RecipeSearch {
	constructor() {
		this.resultsSection = document.querySelector('#search_results');
		this.recipeSection = document.querySelectorAll('.recipe');
		this.recipeSearchInput = document.querySelector('#ingredient_list');
		this.recipeSearchBtn = document.querySelector('#submit_search');
		this.recipes = [];

		// this.recipeSearchBtn.addEventListener('click', this.getSpecificRecipes.bind(this));
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
		this.generateHtmlMarkup();
	}

	async getSpecificRecipes() {
		// Get recipes based on search criteria, or get random recipes

		// If no search criteria has been entered, show random recipes
		if (!this.recipeSearchInput.value) {
			const randomRecipes = await this.getRandomRecipes();
			this.recipes = randomRecipes;
			this.makeRecipes();
			this.generateHtmlMarkup();
		} else {
			const ingredients = this.getIngredients();
			const allRecipes = await axios.get(`http://127.0.0.1:5000/recipes/findByIngredients?ingredients=${ingredients.join(',')}`);
			if (!this.validSearch(allRecipes)) return;
			this.recipes = allRecipes.data;
			this.makeRecipes();
			this.generateHtmlMarkup();
		}
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

	getIngredients() {
		// Retrieves ingredients from input using regular expression

		const regex = /[a-zA-Z]+/g;
		const ingredients = this.recipeSearchInput.value.match(regex);
		return ingredients;
	}

	generateHtmlMarkup() {
		// Generate HTML markup for each recipe

		let allRecipesMarkup = '';
		for (let recipe of this.recipes) {
			const shortenedSummary = recipe.summary.slice(0, 302 - recipe.recipe_title.length) + '...';
			const recipeMarkup = `<div class="col-3 mb-3 recipe">
				<div class="card">
					<img src="${recipe.image}" class="card-img-top">
					<div class="card-body">
						<h5 class="card-title">${recipe.recipe_title}</h5>
						<p class="card-text"></b>${shortenedSummary}</b></p>
						<a href="/recipes/details/${recipe.id}" class="btn btn-primary recipe-link">See Recipe Details</a>
					</div>
				</div>
			</div>`;
			allRecipesMarkup += recipeMarkup;
			console.log(recipeMarkup);
		}
		this.resultsSection.innerHTML = allRecipesMarkup;
	}

	validSearch(allRecipes) {
		// Check if search criteria is valid
		if (!allRecipes.data.length) {
			// If no recipes are found and error message not already shown, show error message
			if (!document.querySelector('.error_msg')) {
				this.showErrorMsg('.search_headers', 'Please enter valid ingredients');
				return false;
			}
			return false;
		}
		// If recipes are found and error message is shown, remove error message
		if (document.querySelector('.error_msg')) {
			document.querySelector('.error_msg').remove();
		}
		return true;
	}

	showErrorMsg(cls, text) {
		const error_msg = document.createElement('p');
		document.querySelector(cls).append(error_msg);
		error_msg.classList.add('text-danger', 'error_msg');
		error_msg.textContent = text;
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

let home = new RecipeSearch();
// home.seedDatabase();
home.getRecipesFromDatabase();
