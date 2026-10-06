// Every stove heats every pot and pan. Each cooking mod keeps its own list of heat sources, and the lists don't
// overlap fully (Farmer's Delight pots ignored the Farm & Charm stove, Bakery and Meadow ignored the Farmer's
// Delight stove, Farm & Charm ignored the HerbalBrews stove), so every stove goes in every list.
ServerEvents.tags('block', event => {
  const stoves = [
    'farmersdelight:stove', 'farm_and_charm:stove', 'herbalbrews:stove', '#candlelight:stoves',
    'meadow:stove_tiles', 'meadow:stove_tiles_wood', 'meadow:stove_tiles_lid'
  ]
  const heatLists = [
    'farmersdelight:heat_sources', 'forge:allows_cooking', 'c:allows_cooking', 'farm_and_charm:allows_cooking',
    'candlelight:allows_cooking', 'herbalbrews:allows_cooking', 'meadow:allows_cooking', 'bakery:allows_cooking'
  ]
  heatLists.forEach(tag => event.add(tag, stoves))
})
