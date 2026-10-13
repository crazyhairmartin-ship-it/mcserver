// Fairies light up the area around them like a lantern: an invisible light block (level FAIRY_LIGHT_LEVEL) follows
// each Fay's Fairies fairy, and the one behind it is removed. Only air is ever replaced, and only our own light blocks
// are cleared again, so builds are never touched.

const FAIRY_LIGHT_LEVEL = 12
const FAIRY_LIGHT_EVERY = 4   // ticks between updates
if (!global.fairyLights) global.fairyLights = {}

function fairyLightClear(level, spot) {
  if (!spot) return
  let block = level.getBlock(spot.x, spot.y, spot.z)
  if (block.id == 'minecraft:light') block.set('minecraft:air')
}

ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % FAIRY_LIGHT_EVERY != 0) return
  let seen = {}
  server.allLevels.forEach(level => {
    let dim = String(level.dimension)
    level.getEntities().forEach(entity => {
      if (!String(entity.type).startsWith('fays_fairies:') || !entity.alive) return
      let id = String(entity.uuid)
      seen[id] = true
      let x = Math.floor(entity.x), y = Math.floor(entity.y + 0.5), z = Math.floor(entity.z)
      let old = global.fairyLights[id]
      if (old && old.dim == dim && old.x == x && old.y == y && old.z == z) return
      if (old && old.dim == dim) fairyLightClear(level, old)
      let here = level.getBlock(x, y, z)
      if (here.id == 'minecraft:air' || here.id == 'minecraft:cave_air') {
        here.set('minecraft:light', { level: String(FAIRY_LIGHT_LEVEL) })
        global.fairyLights[id] = { dim: dim, x: x, y: y, z: z }
      } else {
        delete global.fairyLights[id]
      }
    })
  })
  // fairies that are gone (died, unloaded, changed dimension): take their light away
  Object.keys(global.fairyLights).forEach(id => {
    if (seen[id]) return
    let spot = global.fairyLights[id]
    server.allLevels.forEach(level => {
      if (String(level.dimension) == spot.dim) fairyLightClear(level, spot)
    })
    delete global.fairyLights[id]
  })
})
