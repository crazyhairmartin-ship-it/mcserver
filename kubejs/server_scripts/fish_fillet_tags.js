// Aquaculture's raw fish fillet counts as raw fish wherever a recipe takes "any raw fish": Farmer's Delight cooking
// (forge:raw_fishes), Let's Do cat food (farm_and_charm:raw_fishes -> c:raw_fishes), fish oil and the fish bag
// (minecraft:fishes). Safe from loops: Aquaculture fillets fish from its own fish list, not from these tags.

ServerEvents.tags('item', event => {
  for (const tag of ['forge:raw_fishes', 'c:raw_fishes', 'c:raw_fish', 'minecraft:fishes']) {
    event.add(tag, 'aquaculture:fish_fillet_raw')
  }
})
