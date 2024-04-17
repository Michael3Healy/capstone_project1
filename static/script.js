class RecipeSearch {
	constructor() {
		this.resultsSection = document.querySelector('#search_results');
		this.recipeSection = document.querySelectorAll('.recipe');
        this.recipeSearchInput = document.querySelector
        this.recipes = getSpecificRecipes()
	}

    async getSpecificRecipes() {
        // Get recipes based on search criteria, or get random recipes

        // If no search criteria has been entered, show random recipes
        if (!this.recipeSearchInput.value()) {
            const allRecipes = await this.getRandomRecipes()
            return allRecipes
        } else {
            const allRecipes = await axios.get('https://api.spoonacular.com/recipes/findByIngredients' 'How do I keep apikey secret?')
        }
        
    }

    async getRandomRecipes() {
        // Retrieve list of random recipes

    }

    makeRecipes() {
        // Turn each recipe into instance of Recipe class

        for (let recipe of )
    }

    async getIngredients() {
        // Retrieves ingredients from input using regular expression

        const regex = /[a-zA-Z]+/g
        const ingredients = this.recipeSearchInput.value().match(regex)
        return ingredients
    }

    
}

class Recipe {
	constructor(title, cuisine) {
		this.title = title;
		this.cuisine = cuisine;
	}
}
