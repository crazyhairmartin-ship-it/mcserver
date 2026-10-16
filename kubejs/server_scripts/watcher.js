// The Watcher (2026-10-16): now and then, at dusk or night out in the wild, a figure that looks like a player stands
// far off, turned toward you. Each one is a wanderer (strolls along the treeline, stops, stares again) or a shifter
// (perfectly still while watched; look away and it's somewhere else, sometimes closer). It carries a lantern that
// really lights its surroundings: an invisible light block at its head, moved with it and removed when it goes.
// Walk toward it or stare at it and it turns and runs; once you lose sight of it,
// it's gone. Ignore it and it fades when you look away. It never attacks, can't be hurt, breaks nothing and drops
// nothing. The model is Player Mobs' player_mob with its AI off (natural spawns are off:
// kubejs/data/player_mobs/forge/biome_modifier). /watcher test (ops) brings one now, ignoring time and place.

// its skin: the account whose skin it wears. Player Mobs looks skins up by account name on each player's game, so
// a skin has to belong to a real account (a MineSkin profile in the NBT is ignored, 2026-10-16)
const WATCHER_SKIN_NAME = '__Herobrine__'
const WATCHER_NAME = 'Herobrine'                   // the name it shows (the skin account stays as above)
const WATCHER_GAP_MIN_MS = 45 * 60 * 1000          // between sightings, per player
const WATCHER_GAP_MAX_MS = 120 * 60 * 1000
const WATCHER_DIST = [40, 60]                      // how far away it appears
const WATCHER_APPROACH = 24                        // closer than this and it leaves
const WATCHER_STARE_SECONDS = 3                    // look right at it this long and it leaves
const WATCHER_IGNORED_SECONDS = 20                 // seen, then out of view this long: it fades
const WATCHER_MAX_SECONDS = 150                    // never stays longer than this
const WATCHER_STEP = 0.11                          // blocks per tick when walking (about a stroll)
const WATCHER_RUN = 0.28                           // blocks per tick when it runs off (about a sprint)
const WATCHER_RUN_MIN = 15                         // it runs at least this far before it can vanish from sight
const WATCHER_RUN_MAX_SECONDS = 20                 // and never longer than this
const WATCHER_LIGHT = 13                           // its lantern's light level (an invisible light block at its head)
const WATCHER_SHIFTS = 4                           // a shifter moves this many times while you look away
const WATCHER_SHIFT_TICKS = 10                     // out of your view this long (half a second) and it moves

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

// the lantern's light: an invisible minecraft:light block in the air at its head, only ever placed in air and only
// ever removed if it's still our light block (so nothing else is touched)
function watcherClearLight(player, d) {
  if (!d.contains('lightAt')) return
  let p = d.getString('lightAt').split(' ')
  player.server.runCommandSilent('execute in minecraft:overworld if block ' + p.join(' ') + ' minecraft:light run setblock '
    + p.join(' ') + ' minecraft:air')
  d.remove('lightAt')
}

function watcherLight(player, w, d) {
  let at = Math.floor(w.x) + ' ' + (Math.floor(w.y) + 1) + ' ' + Math.floor(w.z)
  if (d.getString('lightAt') == at) return
  watcherClearLight(player, d)
  if (player.server.runCommandSilent('execute in minecraft:overworld if block ' + at + ' minecraft:air run setblock ' + at
    + ' minecraft:light[level=' + WATCHER_LIGHT + ']') > 0) d.putString('lightAt', at)
}

// gone without dying: a /kill made it drop its lantern and a head (Player Mobs drops the skin's head on death)
function watcherDiscardAll(player) {
  let tag = 'fq_watcher.' + player.uuid
  player.level.getEntities().forEach(e => { if (e.tags.contains(tag)) e.discard() })
}

function watcherRemove(player, d) {
  watcherClearLight(player, d)
  watcherDiscardAll(player)
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

// can it walk through this block (air, grass, flowers, snow layers: anything without collision)? Water and lava aren't
// passable: it never wades. Grass and flowers counted as walls once, so it never moved (2026-10-16).
function watcherPassable(level, x, y, z) {
  let b = level.getBlock(x, y, z)
  let id = String(b.id)
  if (id.endsWith('air')) return true
  if (id == 'minecraft:water' || id == 'minecraft:lava') return false
  try { return !b.blockState.blocksMotion() } catch (e) { return false }
}

// standing room on the ground near (x, z), around height y: the first solid block from above, with room for a body
function watcherGround(level, x, y, z) {
  for (let dy = 16; dy >= -16; dy--) {
    let below = String(level.getBlock(x, y + dy - 1, z).id)
    if (below == 'minecraft:water' || below == 'minecraft:lava') return null
    if (below.indexOf('leaves') >= 0 || watcherPassable(level, x, y + dy - 1, z)) continue
    if (!watcherPassable(level, x, y + dy, z) || !watcherPassable(level, x, y + dy + 1, z)) return null
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

function watcherSpawn(player, d, mood) {
  let level = player.level
  let yaw = (player.yaw + 90) / 57.29577951308232   // facing direction as an angle in x/z
  for (let attempt = 0; attempt < 12; attempt++) {
    let a = yaw + (Math.random() - 0.5) * 1.6            // within ~45 degrees of where they face
    let dist = WATCHER_DIST[0] + Math.random() * (WATCHER_DIST[1] - WATCHER_DIST[0])
    let x = Math.floor(player.x + Math.cos(a) * dist) + 0.5
    let z = Math.floor(player.z + Math.sin(a) * dist) + 0.5
    let y = watcherGround(level, Math.floor(x), Math.floor(player.y), Math.floor(z))
    if (y == null) continue
    let tag = 'fq_watcher.' + player.uuid
    player.server.runCommandSilent('execute in minecraft:overworld run summon player_mobs:player_mob ' + x + ' ' + y + ' ' + z
      + ' {Username:"' + WATCHER_SKIN_NAME + '",CustomName:'{"text":"' + WATCHER_NAME + '"}',NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:0b,CanPickUpLoot:0b,'
      + 'HandItems:[{id:"minecraft:lantern",Count:1b},{}],HandDropChances:[0f,0f],ArmorDropChances:[0f,0f,0f,0f],'
      + 'DeathLootTable:"minecraft:empty",'
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
    d.putString('mood', mood || (Math.random() < 0.5 ? 'wander' : 'shift'))
    d.putInt('walk', 0)
    d.putInt('pause', 3 + Math.floor(Math.random() * 4))
    d.putInt('shifts', 0)
    return true
  }
  return false
}

// turn toward (tx, tz) or walk a step toward it, following the ground
function watcherFace(player, w, tx, tz) {
  player.server.runCommandSilent('execute as ' + w.uuid + ' at @s run tp @s ~ ~ ~ facing ' + tx + ' ' + (w.y + 1.6) + ' ' + tz)
}

function watcherStep(player, w, d, speed) {
  let ax = d.getDouble('ax'), az = d.getDouble('az')       // walking along this direction
  let nx = w.x + ax * (speed || WATCHER_STEP), nz = w.z + az * (speed || WATCHER_STEP)
  let y = watcherGround(player.level, Math.floor(nx), Math.floor(w.y), Math.floor(nz))
  if (y == null || Math.abs(y - w.y) > 1.2) {             // blocked or a drop: turn a little and try next tick
    let a = Math.atan2(az, ax) + (Math.random() < 0.5 ? 0.6 : -0.6)
    d.putDouble('ax', Math.cos(a))
    d.putDouble('az', Math.sin(a))
    return
  }
  let yaw = Math.atan2(-ax, az) * 57.29577951308232
  player.server.runCommandSilent('tp ' + w.uuid + ' ' + nx + ' ' + y + ' ' + nz + ' ' + yaw + ' 0')
  watcherLight(player, w, d)
}

// a wanderer picks a stroll along the treeline: across the player's view, nudged to keep its distance
function watcherStroll(player, w, d) {
  let dx = w.x - player.x, dz = w.z - player.z
  let dist = Math.sqrt(dx * dx + dz * dz) || 1
  let side = Math.random() < 0.5 ? 1 : -1
  let ox = dx / dist, oz = dz / dist                        // outward from the player
  let bias = dist < 38 ? 0.5 : dist > 58 ? -0.5 : (Math.random() - 0.5) * 0.4
  let ax = -oz * side + ox * bias, az = ox * side + oz * bias
  let len = Math.sqrt(ax * ax + az * az) || 1
  d.putDouble('ax', ax / len)
  d.putDouble('az', az / len)
  d.putInt('walk', Math.floor((3 + Math.random() * 4) / WATCHER_STEP))   // 3-7 blocks
  d.putInt('pause', 3 + Math.floor(Math.random() * 5))
}

// a shifter moves somewhere else in the player's view while they look away (sometimes a little closer)
function watcherShift(player, w, d) {
  let dx = w.x - player.x, dz = w.z - player.z
  let dist = Math.sqrt(dx * dx + dz * dz) || 1
  let bearing = Math.atan2(dz, dx)
  for (let attempt = 0; attempt < 10; attempt++) {
    let a = bearing + (Math.random() < 0.5 ? 1 : -1) * (0.25 + Math.random() * 0.5)   // 15-45 degrees to a side
    let r = Math.max(WATCHER_APPROACH + 4, dist - 5 - Math.random() * 7)                  // 5-12 blocks closer
    let x = Math.floor(player.x + Math.cos(a) * r) + 0.5
    let z = Math.floor(player.z + Math.sin(a) * r) + 0.5
    if ((x - w.x) * (x - w.x) + (z - w.z) * (z - w.z) < 64) continue                    // a move you'd notice
    let y = watcherGround(player.level, Math.floor(x), Math.floor(w.y), Math.floor(z))
    if (y == null) continue
    let ox = w.x, oy = w.y, oz = w.z
    player.server.runCommandSilent('tp ' + w.uuid + ' ' + x + ' ' + y + ' ' + z)
    if (player.hasLineOfSight(w)) {                       // somewhere they'll see it when they look back
      watcherFace(player, w, player.x, player.z)
      watcherLight(player, w, d)
      d.putInt('shifts', d.getInt('shifts') + 1)
      return
    }
    player.server.runCommandSilent('tp ' + w.uuid + ' ' + ox + ' ' + oy + ' ' + oz)
  }
}

// running off: every tick, straight away from where the player is now (with the small side lean it picked), and when
// that's blocked the nearest angles that are still away from them; never back toward the player
const WATCHER_FLEE_TURNS = [0, 0.45, -0.45, 0.9, -0.9, 1.3, -1.3]

function watcherFlee(player, w, d) {
  let away = Math.atan2(w.z - player.z, w.x - player.x) + d.getDouble('lean')
  for (let i = 0; i < WATCHER_FLEE_TURNS.length; i++) {
    let a = away + WATCHER_FLEE_TURNS[i]
    let nx = w.x + Math.cos(a) * WATCHER_RUN, nz = w.z + Math.sin(a) * WATCHER_RUN
    let y = watcherGround(player.level, Math.floor(nx), Math.floor(w.y), Math.floor(nz))
    if (y == null || Math.abs(y - w.y) > 1.2) continue
    let yaw = Math.atan2(-Math.cos(a), Math.sin(a)) * 57.29577951308232
    player.server.runCommandSilent('tp ' + w.uuid + ' ' + nx + ' ' + y + ' ' + nz + ' ' + yaw + ' 0')
    watcherLight(player, w, d)
    d.putInt('stuck', 0)
    return true
  }
  d.putInt('stuck', d.getInt('stuck') + 1)                // no way out this tick
  return false
}

function watcherLeave(player, w, d) {
  d.putDouble('lean', (Math.random() - 0.5) * 0.6)                 // a little to one side, kept while it runs
  d.putString('state', 'leave')
  d.putInt('stuck', 0)
  d.putLong('since', Date.now())
  d.putDouble('fromX', w.x)
  d.putDouble('fromZ', w.z)
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
    if (d.contains('lightAt')) watcherClearLight(player, d)
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
    let ran = Math.sqrt((w.x - d.getDouble('fromX')) * (w.x - d.getDouble('fromX')) + (w.z - d.getDouble('fromZ')) * (w.z - d.getDouble('fromZ')))
    let farEnough = ran >= WATCHER_RUN_MIN
    if (secs > WATCHER_RUN_MAX_SECONDS || (farEnough && !player.hasLineOfSight(w))
      || (farEnough && watcherLookAngle(player, w.x, w.y + 1, w.z) > 70)) {
      watcherRemove(player, d)
      return
    }
    watcherFlee(player, w, d)                            // it runs, always away from the player
    if (d.getInt('stuck') >= 5) watcherRemove(player, d)   // cornered: it simply isn't there any more
    return
  }
  if (d.getInt('walk') > 0) {                              // a wanderer mid-stroll
    watcherStep(player, w, d)
    d.putInt('walk', d.getInt('walk') - 1)
  }
  if (d.getString('mood') == 'shift' && d.getBoolean('seen') && d.getInt('shifts') < WATCHER_SHIFTS) {
    let unseen = watcherLookAngle(player, w.x, w.y + 1.5, w.z) > 70 || !player.hasLineOfSight(w)
    d.putInt('unseen', unseen ? d.getInt('unseen') + 1 : 0)
    if (d.getInt('unseen') >= WATCHER_SHIFT_TICKS) {
      watcherShift(player, w, d)
      d.putInt('unseen', 0)
      d.putInt('away', 0)
      return
    }
  }
  if (!everySecond) return
  // watching: turned toward the player (between a wanderer's strolls)
  if (d.getInt('walk') == 0) watcherFace(player, w, player.x, player.z)
  watcherLight(player, w, d)
  let angle = watcherLookAngle(player, w.x, w.y + 1.5, w.z)
  let visible = player.hasLineOfSight(w)
  if (angle < 50 && visible) d.putBoolean('seen', true)
  d.putInt('stare', angle < 4 && visible ? d.getInt('stare') + 1 : 0)
  d.putInt('away', angle > 80 ? d.getInt('away') + 1 : 0)
  if (dist < WATCHER_APPROACH || d.getInt('stare') >= WATCHER_STARE_SECONDS) {
    d.putInt('walk', 0)
    watcherLeave(player, w, d)
    return
  }
  let mood = d.getString('mood')
  if (mood == 'wander' && d.getInt('walk') == 0) {
    d.putInt('pause', d.getInt('pause') - 1)
    if (d.getInt('pause') <= 0) watcherStroll(player, w, d)
  }
  if ((d.getBoolean('seen') && d.getInt('away') >= WATCHER_IGNORED_SECONDS) || secs > WATCHER_MAX_SECONDS) {
    watcherRemove(player, d)                               // ignored: it's simply not there any more
  }
}

const WATCHER_DEBUG = true   // TEMPORARY (2026-10-16): log state while testing why it didn't react

PlayerEvents.tick(event => {
  let player = event.player
  let tick = player.server.tickCount
  if (WATCHER_DEBUG && tick % 40 == 3) {
    let d = watcherData(player)
    if (d.contains('id')) {
      let w = watcherEntity(player, d)
      console.info('WATCHER ' + player.username + ' spectator=' + player.spectator + ' state=' + d.getString('state')
        + ' mood=' + d.getString('mood') + ' found=' + (w != null)
        + (w ? ' dist=' + Math.round(Math.sqrt((w.x - player.x) * (w.x - player.x) + (w.z - player.z) * (w.z - player.z)))
          + ' angle=' + Math.round(watcherLookAngle(player, w.x, w.y + 1.5, w.z)) + ' los=' + player.hasLineOfSight(w) : '')
        + ' stare=' + d.getInt('stare') + ' away=' + d.getInt('away') + ' walk=' + d.getInt('walk'))
    }
  }
  if (player.level.clientSide || player.isSpectator()) return
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
  let mood = d.getString('lastTest') == 'shift' ? 'wander' : 'shift'   // alternate, so each can be tried
  d.putString('lastTest', mood)
  if (!watcherSpawn(player, d, mood)) {
    player.tell(Text.gray('No spot to stand in view. Face somewhere open and try again.'))
    return 0
  }
  player.tell(Text.gray('Something is watching you. (' + (mood == 'shift' ? 'moves when you look away' : 'wanders') + ')'))
  return 1
}
