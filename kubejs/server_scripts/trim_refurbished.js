// Removes the recipes for the trimmed Furniture Refurbished items (list in startup_scripts/trimmed_items.js).
// Pizzas stay craftable: their cheese now comes from Let's Do Meadow (dough already accepts any dough
// through the duplicate groups).

ServerEvents.recipes(event => {
  global.TRIMMED_RECIPES.forEach(recipeId => event.remove({ id: recipeId }))
  event.replaceInput({ input: 'refurbished_furniture:cheese' }, 'refurbished_furniture:cheese', 'meadow:piece_of_cheese')
})
