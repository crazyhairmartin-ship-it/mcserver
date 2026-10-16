// The Watcher (2026-10-16): now and then, at dusk or night out in the wild, a figure that looks like a player stands
// far off, turned toward you. Walk toward it or stare at it and it turns and walks away; once you lose sight of it,
// it's gone. Ignore it and it fades when you look away. It never attacks, can't be hurt, breaks nothing and drops
// nothing. The model is Player Mobs' player_mob with its AI off (natural spawns are off:
// kubejs/data/player_mobs/forge/biome_modifier). /watcher test (ops) brings one now, ignoring time and place.

const WATCHER_SKINS = ['Herobrine']              // Minecraft usernames whose skins it wears
const WATCHER_GAP_MIN_MS = 45 * 60 * 1000          // between sightings, per player
const WATCHER_GAP_MAX_MS = 120 * 60 * 1000
const WATCHER_DIST = [40, 60]                      // how far away it appears
const WATCHER_APPROACH = 24                        // closer than this and it leaves
const WATCHER_STARE_SECONDS = 3                    // look right at it this long and it leaves
const WATCHER_IGNORED_SECONDS = 20                 // seen, then out of view this long: it fades
const WATCHER_MAX_SECONDS = 150                    // never stays longer than this
const WATCHER_STEP = 0.11                          // blocks per tick when walking away (about a stroll)

let $WatcherUUID = Java.loadClass('java.util.UUID')
let $WatcherCompound = Java.loadClass('net.minecraft.nbt.CompoundTag')
let $WatcherWorld = null
try { $WatcherWorld = Java.loadClass('fotfskills.compat.QuestWorld') } catch (e) { $WatcherWorld = null }

function watcherData(player) {
  let d = player.persistentData
  if (!d.contains('fqWatcher')) d.put('fqWatcher', new $WatcherCompound())
  return d.getCompound('fqWatcher')
}

function watcherEntity(player, d) {
  if (!d.contains('id')) return null
  try { return player.level.getEntity($WatcherUUID.fromString(d.getString('id'))) } catch (e) { return null }
}

function watcherRemove(player, d) {
  player.server.runCommandSilent('kill @e[tag=fq_watcher.' + player.uuid + ']')
  d.remove('id')
  d.remove('state')
  d.putLong('next', Date.now() + WATCHER_GAP_MIN_MS + Math.random() * (WATCHER_GAP_MAX_MS - WATCHER_GAP_MIN_MS))
}

// out in the wild at dusk or night, under the open sky, not in a village
function watcherMoodRight(player) {
  if (String(player.level.dimension) != 'minecraft:overworld' || player.isSleeping() || player.isPassenger()) return false
  let t = player.level.getDayTime() % 24000
  if (t < 12300 || t > 23400) return false
  if (!player.level.canSeeSky(player.blockPosition())) return false
  if ($WatcherWorld && $WatcherWorld.inStructure(player.level, player.x, player.y, player.z, '#minecraft:village')) return false
  return true
}

// standing room on the ground near (x, z), around height y
function watcherGround(level, x, y, z) {
  for (let dy = 16; dy >= -16; dy--) {
    let below = String(level.getBlock(x, y + dy - 1, z).id)
    if (below.endsWith('air') || below.indexOf('leaves') >= 0) continue
    if (below == 'minecraft:water' || below == 'minecraft:lava') return null
    if (!String(level.getBlock(x, y + dy, z).id).endsWith('air') || !String(level.getBlock(x, y + dy + 1, z).id).endsWith('air')) return null
    return y + dy
  }
  return null
}

// the angle (degrees) between where the player looks and the direction to (x, y, z)
function watcherLookAngle(player, x, y, z) {
  let look = player.getLookAngle()
  let dx = x - player.x, dy = y - player.getEyeY(), dz = z - player.z
  let len = Math.sqrt(dx * dx + dy * dy + dz * dz)
  if (len < 0.001) return 0
  let dot = (look.x() * dx + look.y() * dy + look.z() * dz) / len
  return Math.acos(Math.max(-1, Math.min(1, dot))) * 57.29577951308232
}

function watcherSpawn(player, d) {
  let level = player.level
  let yaw = (player.yaw + 90) / 57.29577951308232   // facing direction as an angle in x/z
  for (let attempt = 0; attempt < 12; attempt++) {
    let a = yaw + (Math.random() - 0.5) * 1.6            // within ~45 degrees of where they face
    let dist = WATCHER_DIST[0] + Math.random() * (WATCHER_DIST[1] - WATCHER_DIST[0])
    let x = Math.floor(player.x + Math.cos(a) * dist) + 0.5
    let z = Math.floor(player.z + Math.sin(a) * dist) + 0.5
    let y = watcherGround(level, Math.floor(x), Math.floor(player.y), Math.floor(z))
    if (y == null) continue
    let skin = WATCHER_SKINS[Math.floor(Math.random() * WATCHER_SKINS.length)]
    let tag = 'fq_watcher.' + player.uuid
    player.server.runCommandSilent('execute in minecraft:overworld run summon player_mobs:player_mob ' + x + ' ' + y + ' ' + z
      + ' {Username:"' + skin + '",NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:0b,CanPickUpLoot:0b,'
      + 'Tags:["fq_watcher","' + tag + '"]}')
    let found = null
    level.getEntities().forEach(e => { if (!found && e.tags.contains(tag)) found = e })
    if (!found) return false
    if (!player.hasLineOfSight(found)) {                  // hidden behind something: try another spot
      found.discard()
      continue
    }
    d.putString('id', String(found.uuid))
    d.putString('state', 'watch')
    d.putLong('since', Date.now())
    d.putInt('stare', 0)
    d.putInt('away', 0)
    d.putBoolean('seen', false)
    return true
  }
  return false
}

// turn toward (tx, tz) or walk a step toward it, following the ground
function watcherFace(player, w, tx, tz) {
  player.server.runCommandSilent('execute as ' + w.uuid + ' at @s run tp @s ~ ~ ~ facing ' + tx + ' ' + (w.y + 1.6) + ' ' + tz)
}

function watcherStep(player, w, d) {
  let ax = d.getDouble('ax'), az = d.getDouble('az')       // walking away along this direction
  let nx = w.x + ax * WATCHER_STEP, nz = w.z + az * WATCHER_STEP
  let y = watcherGround(player.level, Math.floor(nx), Math.floor(w.y), Math.floor(nz))
  if (y == null || Math.abs(y - w.y) > 1.2) {             // blocked or a drop: turn a little and try next tick
    let a = Math.atan2(az, ax) + (Math.random() < 0.5 ? 0.6 : -0.6)
    d.putDouble('ax', Math.cos(a))
    d.putDouble('az', Math.sin(a))
    return
  }
  let yaw = Math.atan2(-ax, az) * 57.29577951308232
  player.server.runCommandSilent('tp ' + w.uuid + ' ' + nx + ' ' + y + ' ' + nz + ' ' + yaw + ' 0')
}

function watcherLeave(player, w, d) {
  let dx = w.x - player.x, dz = w.z - player.z
  let len = Math.sqrt(dx * dx + dz * dz) || 1
  let a = Math.atan2(dz / len, dx / len) + (Math.random() - 0.5) * 0.8   // away from the player, a little to one side
  d.putDouble('ax', Math.cos(a))
  d.putDouble('az', Math.sin(a))
  d.putString('state', 'leave')
  d.putLong('since', Date.now())
}

function watcherTick(player, everySecond) {
  let d = watcherData(player)
  let w = watcherEntity(player, d)
  if (d.contains('id') && (!w || !w.isAlive() || String(w.level.dimension) != String(player.level.dimension))) {
    watcherRemove(player, d)
    return
  }
  if (!w) {
    if (!everySecond) return
    if (!d.contains('next')) d.putLong('next', Date.now() + 20 * 60 * 1000 + Math.random() * 40 * 60 * 1000)
    if (Date.now() < d.getLong('next') || !watcherMoodRight(player)) return
    if (!watcherSpawn(player, d)) d.putLong('next', Date.now() + 60 * 1000)   // nowhere to stand: try again soon
    return
  }
  let state = d.getString('state')
  let secs = (Date.now() - d.getLong('since')) / 1000
  let dist = Math.sqrt((w.x - player.x) * (w.x - player.x) + (w.z - player.z) * (w.z - player.z))
  if (state == 'leave') {
    // walks off; gone the moment you can't see it, or after a while regardless
    if (secs > 25 || (secs > 0.5 && !player.hasLineOfSight(w)) || (secs > 12 && watcherLookAngle(player, w.x, w.y + 1, w.z) > 70)) {
      watcherRemove(player, d)
      return
    }
    watcherStep(player, w, d)
    return
  }
  if (!everySecond) return
  // watching: turned toward the player, perfectly still
  watcherFace(player, w, player.x, player.z)
  let angle = watcherLookAngle(player, w.x, w.y + 1.5, w.z)
  let visible = player.hasLineOfSight(w)
  if (angle < 50 && visible) d.putBoolean('seen', true)
  d.putInt('stare', angle < 4 && visible ? d.getInt('stare') + 1 : 0)
  d.putInt('away', angle > 80 ? d.getInt('away') + 1 : 0)
  if (dist < WATCHER_APPROACH || d.getInt('stare') >= WATCHER_STARE_SECONDS) {
    watcherLeave(player, w, d)
  } else if ((d.getBoolean('seen') && d.getInt('away') >= WATCHER_IGNORED_SECONDS) || secs > WATCHER_MAX_SECONDS) {
    watcherRemove(player, d)                               // ignored: it's simply not there any more
  }
}

PlayerEvents.tick(event => {
  let player = event.player
  if (player.level.clientSide || player.spectator) return
  let tick = player.server.tickCount
  watcherTick(player, tick % 20 == 7)
})

PlayerEvents.loggedOut(event => {
  let d = watcherData(event.player)
  if (d.contains('id')) watcherRemove(event.player, d)
})

ServerEvents.commandRegistry(event => {
  let { commands: Commands } = event
  event.register(Commands.literal('watcher').requires(src => src.hasPermission(2))
    .then(Commands.literal('test').executes(ctx => global.watcherTest(ctx.source.player))))
})

// the command calls through global, so `kubejs reload server_scripts` updates it (commands themselves only
// re-register on a restart)
global.watcherTest = player => {
  if (!player) return 0
  let d = watcherData(player)
  if (d.contains('id')) watcherRemove(player, d)
  if (!watcherSpawn(player, d)) {
    player.tell(Text.gray('No spot to stand in view. Face somewhere open and try again.'))
    return 0
  }
  player.tell(Text.gray('Something is watching you.'))
  return 1
}
