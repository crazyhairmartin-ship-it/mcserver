// Every cooking pot cooks every pot meal. Farmer's Delight's Cooking Pot and the Let's Do pots (Farm & Charm's Cooking
// Pot, Candlelight's pot and pan, Bakery's small pot, which all share Farm & Charm's recipes) each had their own meals;
// each side's recipes are copied into the other's format. Recipes needing more than 5 ingredients stay Farmer's
// Delight only (the Let's Do pots have fewer slots).
ServerEvents.recipes(event => {
  let toLetsDo = 0, toFarmersDelight = 0, skipped = 0

  event.forEachRecipe({ type: 'farmersdelight:cooking' }, recipe => {
    let r = JSON.parse(String(recipe.json))
    if (!r.ingredients || r.ingredients.length > 5) { skipped++; return }
    event.custom({
      type: 'farm_and_charm:pot_cooking',
      ingredients: r.ingredients,
      container: r.container ? { required: true, item: r.container } : { required: false, item: { item: 'minecraft:bowl' } },
      result: r.result,
      requiresLearning: false
    }).id('kubejs:pot_from_fd/' + String(recipe.getId()).replace(':', '/'))
    toLetsDo++
  })

  event.forEachRecipe({ type: 'farm_and_charm:pot_cooking' }, recipe => {
    let id = String(recipe.getId())
    if (id.startsWith('kubejs:pot_from_fd/')) return            // the copies just made above
    let r = JSON.parse(String(recipe.json))
    if (!r.ingredients || r.ingredients.length > 6) { skipped++; return }
    let out = { type: 'farmersdelight:cooking', ingredients: r.ingredients, result: r.result, cookingtime: 200, experience: 1.0 }
    if (r.container && r.container.required && r.container.item) out.container = r.container.item
    event.custom(out).id('kubejs:pot_from_letsdo/' + id.replace(':', '/'))
    toFarmersDelight++
  })

  console.info(`pots_cook_everything: ${toLetsDo} Farmer's Delight meals copied to the Let's Do pots, ${toFarmersDelight} Let's Do meals copied to the Farmer's Delight pot, ${skipped} skipped`)
})
