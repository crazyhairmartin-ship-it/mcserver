// Butterfly sightings: Bok's Butterflies rarely win a spawn slot against all the other animal mods,
// so during the day this adds one now and then near players outdoors, as long as fewer than
// SIGHTING_MAX are already around. Species match the biome, using the same lists as the mod's own spawns.
// (Butterflies also don't die of old age now: enable_lifespan = false in config/butterflies-common.toml.)

let SIGHTING_INTERVAL_TICKS = 400 // every 20 seconds per player
let SIGHTING_MAX = 4 // butterflies within SIGHTING_RADIUS before we stop adding more
let SIGHTING_RADIUS = 48

// Checked in order: the first biome tag that matches the spot decides the species.
// fotf:wildlife/* = the vanilla/Forge biome tags plus BoP/Regions Unexplored/taiga biomes that lacked them
// (kubejs/data/fotf/tags/worldgen/biome/wildlife; butterfly and Critters & Companions spawns use them too).
let SIGHTING_SPECIES = [
  ['#fotf:wildlife/jungle', ['morpho', 'glasswing', 'clipper', 'clipperblue', 'clippergreen', 'clipperorange', 'clipperpink', 'clipperpurple']],
  ['#fotf:wildlife/ice', ['ice', 'clearwing-hummingbird']],
  ['#fotf:wildlife/savanna', ['buckeye', 'common-crow', 'peacock-pansy-dry']],
  ['#fotf:wildlife/wetlands', ['admiral', 'cabbage', 'forester', 'hairstreak', 'longwing', 'peacock-pansy-wet']],
  ['#fotf:wildlife/forest', ['admiral', 'bluemoon', 'commander', 'common', 'emperor', 'forester', 'hairstreak', 'peacock', 'rainbow', 'green-skirt-baron']],
  ['#fotf:wildlife/plains', ['buckeye', 'cabbage', 'common', 'commongrassyellow', 'heath', 'monarch', 'peacock', 'rainbow', 'swallowtail']],
  ['#fotf:wildlife/hill', ['chalkhill', 'common-crow', 'common-mime']],
  ['#forge:is_plateau', ['chalkhill', 'common-crow', 'common-mime']],
]

let $SightingHeightmap = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')

function countButterfliesNear(level, x, y, z) {
  let nearby = level.getEntitiesWithin(AABB.of(x - SIGHTING_RADIUS, y - 24, z - SIGHTING_RADIUS, x + SIGHTING_RADIUS, y + 24, z + SIGHTING_RADIUS))
  let count = 0
  nearby.forEach(entity => {
    if (String(entity.type).startsWith('butterflies:')) count++
  })
  return count
}

ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % SIGHTING_INTERVAL_TICKS != 0) return
  let overworld = server.overworld()
  if (!overworld.isDay() || overworld.isRaining()) return

  server.players.forEach(player => {
    if (player.level.dimension != 'minecraft:overworld') return
    if (countButterfliesNear(overworld, player.x, player.y, player.z) >= SIGHTING_MAX) return

    // A random open-air spot 10-24 blocks away, on the ground.
    let angle = Math.random() * Math.PI * 2
    let distance = 10 + Math.random() * 14
    let sx = Math.floor(player.x + Math.cos(angle) * distance)
    let sz = Math.floor(player.z + Math.sin(angle) * distance)
    let sy = overworld.getHeight($SightingHeightmap.MOTION_BLOCKING_NO_LEAVES, sx, sz) + 1
    if (Math.abs(sy - player.y) > 24) return // don't spawn on a far-off cliff or deep below

    // First matching biome wins; runCommandSilent returns how many times the command succeeded.
    for (let i = 0; i < SIGHTING_SPECIES.length; i++) {
      let biomeTag = SIGHTING_SPECIES[i][0]
      let options = SIGHTING_SPECIES[i][1]
      let species = options[Math.floor(Math.random() * options.length)]
      let summoned = server.runCommandSilent(`execute in minecraft:overworld positioned ${sx} ${sy} ${sz} if biome ~ ~ ~ ${biomeTag} run summon butterflies:${species} ~ ~1 ~`)
      if (summoned > 0) break
    }
  })
})
