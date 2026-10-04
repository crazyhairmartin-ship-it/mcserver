// Grappling Hook - Reforged: only the basic grappling hook stays. Its upgrades come from the Agility skill tree
// (Long Rope, Hookmaster, Motor Reel, Twin Hooks). Trimmed items are hidden from JEI via global.TRIMMED_ITEMS and their
// recipes removed here. The motor/smart/ender/magnet/rocket/double hooks are the same item with different settings,
// so their recipes are removed by id.

ServerEvents.recipes(event => {
  global.TRIMMED_ITEMS
    .filter(itemId => itemId.startsWith('grapplemod:'))
    .forEach(itemId => event.remove({ output: itemId }))
  ;['motorhook', 'doublemotorhook', 'smarthook', 'enderhook', 'magnethook', 'rockethook', 'rocketdoublemotorhook']
    .forEach(recipe => event.remove({ id: `grapplemod:${recipe}` }))
})
