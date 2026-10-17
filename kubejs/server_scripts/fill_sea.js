// /fillsea [radius] and /fillsea undo (ops; also "!fillsea" in chat, which works without a restart): fills a circle
// around the player with water source blocks up to sea level (surface at Y=62), wherever the column is open to the
// sky from the ground up (caves, buildings and overhangs stay dry). Underground, it floods the cave you stand in
// instead (only the space connected to you). Only air and walk-through plants are replaced.
// Undo removes the last fill's water (only blocks that are still water). Dylan, 2026-10-16.

const FILLSEA_TOP = 62                 // the overworld water surface (sea level 63)
const FILLSEA_DEFAULT = 30
const FILLSEA_MAX = 48
const FILLSEA_LIMIT = 150000            // most blocks in one fill

let $FillHeightmap = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')
let fillSeaUndo = {}                    // player uuid -> [[x, y, z], ...] of the last fill (lost on restart)

function fillSeaReplaceable(block) {
  let id = String(block.id)
  if (id.endsWith('air')) return true
  if (id == 'minecraft:water' || id == 'minecraft:lava' || id.indexOf('waterlogged') >= 0) return false
  try { return !block.blockState.blocksMotion() && !block.blockState.liquid() } catch (e) { return false }
}

global.fillSea = (player, arg) => {
  if (!player) return 0
  if (!player.hasPermissions(2)) { player.tell(Text.red('Only ops can use /fillsea.')); return 0 }
  let level = player.level
  if (String(level.dimension) != 'minecraft:overworld') { player.tell(Text.red('/fillsea only works in the Overworld.')); return 0 }
  let id = String(player.uuid)

  if (arg == 'undo') {
    let list = fillSeaUndo[id]
    if (!list || !list.length) { player.tell(Text.gray('Nothing to undo.')); return 0 }
    let n = 0
    list.forEach(c => {
      let b = level.getBlock(c[0], c[1], c[2])
      if (String(b.id) == 'minecraft:water') { b.set('minecraft:air'); n++ }
    })
    delete fillSeaUndo[id]
    player.tell(Text.green('Removed ' + n + ' water blocks.'))
    return 1
  }

  let r = arg ? parseInt(arg) : FILLSEA_DEFAULT
  if (!(r >= 1 && r <= FILLSEA_MAX)) { player.tell(Text.red('Radius must be 1-' + FILLSEA_MAX + '.')); return 0 }
  let cx = Math.floor(player.x), cz = Math.floor(player.z)
  let placed = []
  // underground (rock overhead): fill the open space connected to where the player stands, within the radius, up to
  // sea level; other caves inside the circle stay dry (Dylan was flooding a cave, 2026-10-17)
  if (level.getHeight($FillHeightmap.MOTION_BLOCKING_NO_LEAVES, cx, cz) > FILLSEA_TOP + 1) {
    let sy = Math.min(Math.floor(player.y), FILLSEA_TOP)
    let seen = {}, queue = [[cx, sy, cz]]
    seen[cx + ',' + sy + ',' + cz] = true
    while (queue.length && placed.length < FILLSEA_LIMIT) {
      let c = queue.pop()
      let b = level.getBlock(c[0], c[1], c[2])
      if (!fillSeaReplaceable(b)) continue
      b.set('minecraft:water')
      placed.push(c)
      ;[[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1], [0, -1, 0], [0, 1, 0]].forEach(dv => {
        let n = [c[0] + dv[0], c[1] + dv[1], c[2] + dv[2]]
        if (n[1] > FILLSEA_TOP || n[1] <= level.minBuildHeight
          || (n[0] - cx) * (n[0] - cx) + (n[2] - cz) * (n[2] - cz) > r * r) return
        let k = n[0] + ',' + n[1] + ',' + n[2]
        if (seen[k]) return
        seen[k] = true
        queue.push(n)
      })
    }
    if (placed.length) fillSeaUndo[id] = placed   // a fill that placed nothing keeps the last undo
    player.tell(placed.length ? Text.green('Flooded ' + placed.length + ' blocks of this cave up to sea level. !fillsea undo takes them out.')
      : Text.gray('Nothing to fill here: you\'re above sea level.'))
    return 1
  }
  for (let x = cx - r; x <= cx + r && placed.length < FILLSEA_LIMIT; x++) {
    for (let z = cz - r; z <= cz + r; z++) {
      if ((x - cx) * (x - cx) + (z - cz) * (z - cz) > r * r) continue
      // open to the sky above sea level: nothing solid (leaves don't count) higher than the water surface
      if (level.getHeight($FillHeightmap.MOTION_BLOCKING_NO_LEAVES, x, z) > FILLSEA_TOP + 1) continue
      for (let y = FILLSEA_TOP; y > level.minBuildHeight; y--) {
        let b = level.getBlock(x, y, z)
        if (!fillSeaReplaceable(b)) break           // reached the ground (or existing water)
        b.set('minecraft:water')
        placed.push([x, y, z])
      }
    }
  }
  if (placed.length) fillSeaUndo[id] = placed   // a fill that placed nothing keeps the last undo
  player.tell(placed.length ? Text.green('Placed ' + placed.length + ' water blocks. /fillsea undo (or !fillsea undo) takes them out.')
    : Text.gray('Nothing to fill here: the ground is at or above sea level, or it\'s all covered.'))
  return 1
}

ServerEvents.commandRegistry(event => {
  let { commands: Commands, arguments: Arguments } = event
  event.register(Commands.literal('fillsea').requires(src => src.hasPermission(2))
    .executes(ctx => global.fillSea(ctx.source.player, null))
    .then(Commands.literal('undo').executes(ctx => global.fillSea(ctx.source.player, 'undo')))
    .then(Commands.argument('radius', Arguments.INTEGER.create(event))
      .executes(ctx => global.fillSea(ctx.source.player, String(Arguments.INTEGER.getResult(ctx, 'radius'))))))
})

// until the next restart registers /fillsea, "!fillsea [radius|undo]" in chat does the same (ops only; not shown in chat)
PlayerEvents.chat(event => {
  let msg = String(event.message).trim()
  if (msg != '!fillsea' && msg.indexOf('!fillsea ') != 0) return
  event.cancel()
  // chat arrives on a background thread and world changes from there silently do nothing, so the request is queued
  // and the server tick (always the main thread) runs it
  fillSeaQueue.push({ uuid: String(event.player.uuid), arg: msg.split(/\s+/)[1] || null })
  console.info('fillsea: queued "' + msg + '" for ' + event.player.username)
})

let fillSeaQueue = []

// /trigger fillsea (built into Minecraft, no restart or chat needed): "/trigger fillsea" fills 30 blocks around you,
// "/trigger fillsea set 20" a radius of 20, "/trigger fillsea set 99" undoes the last fill. Ops only.
ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % 10 != 0) return
  server.runCommandSilent('scoreboard objectives add fillsea trigger')      // once; harmless after that
  server.players.forEach(p => {
    if (!p.hasPermissions(2)) return
    // by name: Native Nicknames makes the scoreboard name the nickname, and a UUID resolves to the real account name
    let name = String(p.username)
    let v = server.runCommandSilent('scoreboard players get ' + name + ' fillsea')
    server.runCommandSilent('scoreboard players enable ' + name + ' fillsea')
    if (!(v > 0)) return
    server.runCommandSilent('scoreboard players set ' + name + ' fillsea 0')
    fillSeaQueue.push({ uuid: String(p.uuid), arg: v == 99 ? 'undo' : v == 1 ? null : String(v) })
  })
})

ServerEvents.tick(event => {
  if (!fillSeaQueue.length) return
  let job = fillSeaQueue.shift()
  let player = null
  event.server.players.forEach(p => { if (String(p.uuid) == job.uuid) player = p })
  if (!player) return
  console.info('fillsea: running for ' + player.username + ' (' + (job.arg || 'default') + ')')
  try {
    global.fillSea(player, job.arg)
  } catch (e) {
    console.error('fillsea failed: ' + e)
    player.tell(Text.red('fillsea failed: ' + e))
  }
})
