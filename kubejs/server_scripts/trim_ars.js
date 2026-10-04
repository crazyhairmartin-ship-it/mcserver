// Ars Nouveau: spellcasting removed (see startup_scripts/trimmed_items.js). Recipes that make the trimmed items go,
// including every glyph recipe (Scribe's Table recipes are their own type).

ServerEvents.recipes(event => {
  global.TRIMMED_ITEMS
    .filter(itemId => itemId.startsWith('ars_nouveau:'))
    .forEach(itemId => event.remove({ output: itemId }))
  event.remove({ type: 'ars_nouveau:glyph' })
})
