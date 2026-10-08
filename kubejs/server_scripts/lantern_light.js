// A lantern in the Curios "Lantern" slot (kubejs/data/fotf/curios; needs a backpack worn, see fotfskills BackpackLantern) lights the area around its wearer: an invisible
// light block follows the player's head, the one behind is removed. Same approach as fairy_light.js: only air is ever
// replaced and only our own light blocks are cleared, so builds are never touched.

const CuriosApi = Java.loadClass('top.theillusivec4.curios.api.CuriosApi')
const BackpackLantern = Java.loadClass('fotfskills.compat.BackpackLantern')
const LANTERN_LEVELS = { 'minecraft:lantern': 15, 'minecraft:soul_lantern': 10, 'meadow:oil_lantern': 14 }
const LANTERN_DEFAULT_LEVEL = 13
const LANTERN_EVERY = 2   // ticks between updates
if (!global.lanternLights) global.lanternLights = {}

function lanternLevelOf(player) {
  if (!BackpackLantern.wearsBackpack(player)) return 0   // the lantern hangs off a backpack (fotfskills)
  let inv = CuriosApi.getCuriosInventory(player).resolve()
  if (!inv.isPresent()) return 0
  let slots = inv.get().getStacksHandler('lantern')
  if (!slots.isPresent()) return 0
  let stacks = slots.get().getStacks()
  for (let i = 0; i < stacks.getSlots(); i++) {
    let stack = stacks.getStackInSlot(i)
    if (stack.isEmpty()) continue
    let lvl = LANTERN_LEVELS[String(stack.id)]
    return lvl ? lvl : LANTERN_DEFAULT_LEVEL
  }
  return 0
}

function lanternLightClear(level, spot) {
  if (!spot) return
  let block = level.getBlock(spot.x, spot.y, spot.z)
  if (block.id == 'minecraft:light') block.set('minecraft:air')
}

ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % LANTERN_EVERY != 0) return
  let seen = {}
  server.players.forEach(player => {
    let id = String(player.uuid)
    let lvl = player.isSpectator() ? 0 : lanternLevelOf(player)
    if (lvl <= 0) return
    seen[id] = true
    let level = player.level
    let dim = String(level.dimension)
    let x = Math.floor(player.x), y = Math.floor(player.y + 1), z = Math.floor(player.z)
    let old = global.lanternLights[id]
    if (old && old.dim == dim && old.x == x && old.y == y && old.z == z && old.lvl == lvl) return
    if (old && old.dim == dim) lanternLightClear(level, old)
    if (old && old.dim != dim) server.allLevels.forEach(l => { if (String(l.dimension) == old.dim) lanternLightClear(l, old) })
    let here = level.getBlock(x, y, z)
    if (here.id == 'minecraft:air' || here.id == 'minecraft:cave_air') {
      here.set('minecraft:light', { level: String(lvl) })
      global.lanternLights[id] = { dim: dim, x: x, y: y, z: z, lvl: lvl }
    } else {
      delete global.lanternLights[id]
    }
  })
  // lantern taken off, player left or changed dimension: take the light away
  Object.keys(global.lanternLights).forEach(id => {
    if (seen[id]) return
    let spot = global.lanternLights[id]
    server.allLevels.forEach(level => {
      if (String(level.dimension) == spot.dim) lanternLightClear(level, spot)
    })
    delete global.lanternLights[id]
  })
})
