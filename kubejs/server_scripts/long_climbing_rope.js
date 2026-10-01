// Let's Do Meadow's Climbing Rope: the topmount only hangs 12 blocks of rope (hard-coded).
// Extend it to 127 blocks, stopping at the first block that isn't air or rope.
// Rope segments have no drops (only the topmount does), so a longer rope can't be farmed.

let ROPE_MAX_LENGTH = 127

BlockEvents.placed('meadow:climbing_rope_topmount', event => {
  let level = event.level
  for (let depth = 1; depth <= ROPE_MAX_LENGTH; depth++) {
    let segment = event.block.offset(0, -depth, 0)
    if (segment.y < level.minBuildHeight) break
    if (segment.id == 'meadow:climbing_rope') continue
    if (!segment.blockState.isAir()) break
    segment.set('meadow:climbing_rope')
  }
})
