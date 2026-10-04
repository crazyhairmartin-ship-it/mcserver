// Aquaculture: fillet knives are merged into Farmer's Delight knives (startup_scripts/duplicate_groups.js; both fillet
// fish, since Aquaculture's fillet tag is forge:tools/knives). The wooden and stone fillet knives become the flint knife,
// so their own recipes go (planks shouldn't make a flint knife). The neptunium fillet knife stays.

ServerEvents.recipes(event => {
  event.remove({ id: 'aquaculture:wooden_fillet_knife' })
  event.remove({ id: 'aquaculture:stone_fillet_knife' })
})
