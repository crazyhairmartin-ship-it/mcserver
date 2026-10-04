// Grappling Hook - Reforged: every hook and upgrade item except the basic grappling hook.
// They're hidden from JEI via global.TRIMMED_ITEMS; their recipes are removed here. The basic hook's upgrades come
// from the Agility skill tree (Long Rope, Hookmaster, Motor Reel, Twin Hooks).

ServerEvents.recipes(event => {
  global.TRIMMED_ITEMS
    .filter(itemId => itemId.startsWith('grapplemod:'))
    .forEach(itemId => event.remove({ output: itemId }))
})
