// Tinkers' Construct is kept only for its slime islands: every Tinkers recipe is removed except the ones
// that make island items (slime wood planks/doors/etc., slime blocks, congealed slime).
// Kept items: global.TINKERS_KEEP (startup_scripts/trimmed_items.js). New cobalt ore and slime crystal
// geodes are switched off in kubejs/data/tconstruct/forge/biome_modifier/.

ServerEvents.recipes(event => {
  event.remove({ mod: 'tconstruct', not: global.TINKERS_KEEP.map(keepId => ({ output: keepId })) })
})
