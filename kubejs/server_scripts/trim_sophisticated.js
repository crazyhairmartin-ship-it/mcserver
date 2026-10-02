// Sophisticated Backpacks: upgrades that need power (nothing in this pack generates Forge Energy).
// They're hidden from JEI via global.TRIMMED_ITEMS; their recipes are removed here.

ServerEvents.recipes(event => {
  global.TRIMMED_ITEMS
    .filter(itemId => itemId.startsWith('sophisticatedbackpacks:'))
    .forEach(itemId => event.remove({ output: itemId }))
})
