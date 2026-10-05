// Supplementaries quiver: no recipe (hidden via global.TRIMMED_ITEMS; skeletons' quiver chance is 0 in its config).
ServerEvents.recipes(event => {
  event.remove({ output: 'supplementaries:quiver' })
})
