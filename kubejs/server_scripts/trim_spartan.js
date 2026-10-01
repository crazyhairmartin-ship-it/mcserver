// Spartan Weaponry: weapons for metals no mod in this pack provides (aluminum, bronze, constantan,
// electrum, invar, lead, nickel, platinum, silver, tin; steel only came from Tinkers' trimmed metals).
// They're hidden from JEI via global.TRIMMED_ITEMS; their recipes are removed so nothing references them.

ServerEvents.recipes(event => {
  global.TRIMMED_ITEMS
    .filter(itemId => itemId.startsWith('spartanweaponry:'))
    .forEach(itemId => event.remove({ output: itemId }))
})
