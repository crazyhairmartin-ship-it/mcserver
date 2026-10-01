// Simply Swords: the iron, gold, diamond and netherite weapons are gone (uncraftable, hidden from JEI,
// and no longer in loot: standardLootTableWeight = 0 in config/simplyswords/loot.toml).
// Runic weapons and the unique legendary weapons stay.

ServerEvents.recipes(event => {
  global.SIMPLYSWORDS_WEAPONS.forEach(weapon => {
    ['iron', 'gold', 'diamond', 'netherite'].forEach(material => event.remove({ output: `simplyswords:${material}_${weapon}` }))
  })
})
