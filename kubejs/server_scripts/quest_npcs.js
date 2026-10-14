// Quest characters, encounters and timed challenges (data from quest_givers.generated.js; helpers like questOpen,
// questSay and questAddStage live in quest_givers.js).
//
// - /questnpc place <id> (ops): puts the named character from tools/quests/src/pack.json "characters" where you stand,
//   facing your way. It stays put, never despawns and can't be hurt; a plain right-click talks to it.
//   /questnpc remove <id> removes it again; /questnpc list shows the characters.
// - Encounters ("encounter" tasks): when a quest reaches the step, the character or mob appears near the player (if the
//   step's conditions fit: dimension, biome, height). Talking to it, or defeating it, completes the step. It leaves
//   after a while if ignored and comes back later; it's removed once the step is done.
// - Timed challenges ("timed" tasks): when a quest reaches the step, the player gets a clickable [Start]. The timer
//   and progress show on the action bar; reaching the goal in time completes the step, otherwise they can retry.

let $NpcCompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')
let $NpcUUID = Java.loadClass('java.util.UUID')
let $NpcStats = Java.loadClass('net.minecraft.stats.Stats')
let $NpcResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')

const NPC_ENCOUNTER_RETRY_MS = 2 * 60 * 1000    // after an encounter leaves or is lost, wait before bringing it back
const NPC_CHALLENGE_PROMPT_MS = 5 * 60 * 1000   // remind about an unstarted challenge at most this often

function npcData(player, key) {
  let data = player.persistentData
  if (!data.contains(key)) data.put(key, new $NpcCompoundTag())
  return data.getCompound(key)
}

function npcEntries(type) {
  return (global.QUEST_GIVERS || []).filter(g => g.type == type)
}

function npcEntryByStage(stage) {
  return (global.QUEST_GIVERS || []).find(g => g.stage == stage)
}

// Turn a freshly created entity into a quest character: name, profession, no despawning, can't be hurt.
function npcDress(entity, name, profession, extra) {
  let nbt = { CustomName: JSON.stringify({ text: name }), CustomNameVisible: true, PersistenceRequired: true }
  if (profession) nbt.VillagerData = { profession: profession, level: 5, type: 'minecraft:plains' }
  Object.keys(extra || {}).forEach(k => { nbt[k] = extra[k] })
  entity.mergeNbt(nbt)
}

function npcStatValue(player, stat) {
  try {
    return player.stats.getValue($NpcStats.CUSTOM.get(new $NpcResourceLocation(stat)))
  } catch (e) {
    console.warn('quest_npcs: unknown stat ' + stat + ': ' + e)
    return 0
  }
}

// ---- /questnpc and /quest challenge ----

ServerEvents.commandRegistry(event => {
  let { commands: Commands, arguments: Arguments } = event
  // /questreset <player> (ops): back to a fresh start for testing: FTB progress, quest tags, offers, encounters,
  // challenges and quest drops all cleared
  event.register(Commands.literal('questreset')
    .requires(src => src.hasPermission(2))
    .then(Commands.argument('player', Arguments.PLAYER.create(event)).executes(ctx => {
      let target = Arguments.PLAYER.getResult(ctx, 'player')
      let server = ctx.source.server
      server.runCommandSilent('ftbquests change_progress ' + target.username + ' reset 1')
      let tags = []
      target.tags.forEach(t => { if (String(t).indexOf('fq.') == 0) tags.push(String(t)) })
      tags.forEach(t => target.removeTag(t))
      let data = target.persistentData
      ;['fqOffers', 'fqDropped', 'fqEnc', 'fqTimed', 'fqTimedPrompt', 'fqBuild', 'fqPhotos', 'fqTame', 'fqBreed', 'fqWaystones', 'fqAmbient', 'fqCast', 'fqSpellKill', 'fqSpawn', 'fqMine'].forEach(k => data.remove(k))
      server.runCommandSilent('kill @e[tag=fq_owner.' + target.uuid + ']')
      ctx.source.sendSystemMessage(Text.green('Reset ' + target.username + "'s quests (" + tags.length + ' quest tags).'))
      return 1
    })))
  event.register(Commands.literal('questnpc')
    .requires(src => src.hasPermission(2))
    .then(Commands.literal('place').then(Commands.argument('id', Arguments.STRING.create(event)).executes(ctx => {
      let player = ctx.source.player
      let id = Arguments.STRING.getResult(ctx, 'id')
      let info = (global.QUEST_CHARACTERS || {})[id]
      if (!player || !info) {
        ctx.source.sendSystemMessage(Text.red('No character "' + id + '" (tools/quests/src/pack.json "characters")'))
        return 0
      }
      // placing again moves the character: the old one (in loaded chunks) goes first
      ctx.source.server.runCommandSilent('kill @e[tag=fq_npc.' + id + ']')
      // /summon builds the mob from its data in one step. createEntity + mergeNbt reads a mob's data before it's in
      // the world, which some mobs can't do (Ender Mail's carrier crashes saving itself), so characters are summoned
      let nbt = { CustomName: JSON.stringify({ text: info.name }), CustomNameVisible: true, PersistenceRequired: true,
        Invulnerable: true, NoAI: true, Silent: true, Tags: ['fq_npc', 'fq_npc.' + id] }
      if (info.profession) nbt.VillagerData = { profession: info.profession, level: 5, type: 'minecraft:plains' }
      let summoned = ctx.source.server.runCommandSilent('execute in ' + player.level.dimension + ' run summon '
        + (info.entity || 'minecraft:villager') + ' ' + player.x + ' ' + player.y + ' ' + player.z + ' ' + JSON.stringify(nbt))
      if (!summoned) {
        player.tell(Text.red('Could not summon ' + info.name + ' (' + (info.entity || 'minecraft:villager') + '). See the server log.'))
        return 0
      }
      let entity = { uuid: '@e[tag=fq_npc.' + id + ',limit=1]' }   // the commands below only need a target
      // face the way the player faces: /tp sets the body and head rotation (KubeJS can't reach setYRot here)
      ctx.source.server.runCommandSilent('tp ' + entity.uuid + ' ' + player.x + ' ' + player.y + ' ' + player.z
        + ' ' + player.yaw + ' 0')
      // pack.json "equip": {"head", "chest", "legs", "feet", "mainhand", "offhand": item id}; script-made mobs skip their
      // natural spawn gear (Iron's priests come without their armour)
      Object.keys(info.equip || {}).forEach(slot => {
        let where = (slot == 'mainhand' || slot == 'offhand') ? 'weapon.' + slot : 'armor.' + slot
        ctx.source.server.runCommandSilent('item replace entity ' + entity.uuid + ' ' + where + ' with ' + info.equip[slot])
      })
      if (info.equip) ctx.source.server.runCommandSilent('data merge entity ' + entity.uuid
        + ' {ArmorDropChances:[0f,0f,0f,0f],HandDropChances:[0f,0f]}')
      // pack.json "scale": Pehkui size (Dagna is short). Pehkui doesn't save base scale unless told to persist.
      // The change eases in on the entity's next ticks (nothing ticks while the server is empty).
      if (info.scale) {
        ctx.source.server.runCommandSilent('scale set pehkui:base ' + info.scale + ' ' + entity.uuid)
        ctx.source.server.runCommandSilent('scale persist set pehkui:base true ' + entity.uuid)
      }
      player.tell(Text.green('Placed ' + info.name + '. Place again to move them.'))
      return 1
    })))
    .then(Commands.literal('remove').then(Commands.argument('id', Arguments.STRING.create(event)).executes(ctx => {
      let id = Arguments.STRING.getResult(ctx, 'id')
      ctx.source.server.runCommandSilent('kill @e[tag=fq_npc.' + id + ']')
      ctx.source.sendSystemMessage(Text.of('Removed every "' + id + '" character in loaded chunks.'))
      return 1
    })))
    .then(Commands.literal('list').executes(ctx => {
      let chars = global.QUEST_CHARACTERS || {}
      let ids = Object.keys(chars).filter(k => k.indexOf('_') != 0)
      let msg = ids.length ? ids.map(k => k + ' (' + chars[k].name + ')').join(', ') : 'No characters yet.'
      ctx.source.sendSystemMessage(Text.of(msg))
      return 1
    })))
  event.register(Commands.literal('quest')
    .then(Commands.literal('challenge').then(Commands.argument('stage', Arguments.STRING.create(event))
      .executes(ctx => {
        let player = ctx.source.player
        if (!player) return 0
        return npcStartChallenge(player, Arguments.STRING.getResult(ctx, 'stage')) ? 1 : 0
      }))))
})

// ---- encounters ----

function npcFindSpot(player, minDist, maxDist) {
  return npcFindSpotAround(player, player.x, player.z, minDist, maxDist)
}

// a standing spot (air at feet and head, solid ground, not liquid) minDist-maxDist from (cx, cz), near the player's height
function npcFindSpotAround(player, cx, cz, minDist, maxDist) {
  let level = player.level
  for (let attempt = 0; attempt < 24; attempt++) {
    let angle = Math.random() * 6.283185307179586   // 2 pi (Rhino here has no Math.PI)
    let dist = minDist + Math.random() * (maxDist - minDist)
    let x = Math.floor(cx + Math.cos(angle) * dist)
    let z = Math.floor(cz + Math.sin(angle) * dist)
    let reach = maxDist > 20 ? 14 : 6   // farther spots need more height range on uneven ground
    for (let dy = reach; dy >= -reach; dy--) {
      let y = Math.floor(player.y) + dy
      let feet = level.getBlock(x, y, z)
      let head = level.getBlock(x, y + 1, z)
      let ground = level.getBlock(x, y - 1, z)
      let gid = String(ground.id)
      if (String(feet.id).endsWith('air') && String(head.id).endsWith('air') && !gid.endsWith('air')
        && gid != 'minecraft:water' && gid != 'minecraft:lava') {
        return { x: x + 0.5, y: y, z: z + 0.5 }
      }
    }
  }
  return null
}

// Quest mobs to fight are tougher and bigger than wild ones: boost = {health, damage, speed: multipliers, scale: a
// number or [min, max]} from the generator. Applied with attribute modifiers (mobs without an attribute just skip it),
// then healed to the new maximum, then sized with Pehkui (no easing, so they never visibly grow).
const NPC_BOOST_IDS = { health: '6f9a1d3e-0b1a-4c5e-9f1e-1a2b3c4d5e01', damage: '6f9a1d3e-0b1a-4c5e-9f1e-1a2b3c4d5e02',
  speed: '6f9a1d3e-0b1a-4c5e-9f1e-1a2b3c4d5e03' }
const NPC_BOOST_ATTRS = { health: 'minecraft:generic.max_health', damage: 'minecraft:generic.attack_damage',
  speed: 'minecraft:generic.movement_speed' }

function npcBoost(server, selector, boost) {
  if (!boost) return
  let run = cmd => server.runCommandSilent('execute as ' + selector + ' run ' + cmd)
  Object.keys(NPC_BOOST_ATTRS).forEach(k => {
    let m = Number(boost[k] || 1)
    if (m != 1) run('attribute @s ' + NPC_BOOST_ATTRS[k] + ' modifier add ' + NPC_BOOST_IDS[k] + ' fq_quest_' + k + ' '
      + (m - 1) + ' multiply_base')
  })
  run('data merge entity @s {Health:100000f}')
  let sc = boost.scale
  if (sc && typeof sc == 'object') sc = Number(sc[0]) + Math.random() * (Number(sc[1]) - Number(sc[0]))
  if (sc && Number(sc) != 1) {
    run('scale delay set pehkui:base 0 @s')
    run('scale set pehkui:base ' + Number(sc).toFixed(2) + ' @s')
  }
}

function npcConditionsMet(player, where) {
  if (where.dimension && String(player.level.dimension) != where.dimension) return false
  if (where.below_y != null && player.y >= where.below_y) return false
  if (where.above_y != null && player.y <= where.above_y) return false
  if (where.biomes && where.biomes.length && where.biomes.indexOf(String(player.block.biomeId)) < 0) return false
  return true
}

function npcEntity(player, uuidText) {
  if (!uuidText) return null
  try {
    return player.level.getEntity($NpcUUID.fromString(uuidText))
  } catch (e) {
    return null
  }
}

function npcTickEncounters(player) {
  let state = npcData(player, 'fqEnc')
  let now = Date.now()
  npcEntries('encounter').forEach(enc => {
    let rec = state.contains(enc.stage) ? state.getCompound(enc.stage) : null
    let entity = rec ? npcEntity(player, String(rec.getString('uuid'))) : null
    if (player.tags.contains(enc.stage)) {
      if (entity) entity.discard()
      if (rec) state.remove(enc.stage)
      return
    }
    if (entity && entity.isAlive()) {
      if (now > rec.getLong('until')) {
        entity.discard()
        rec.putString('uuid', '')
        rec.putLong('retry', now + NPC_ENCOUNTER_RETRY_MS)
        player.tell(Text.gray(enc.name + ' has gone. Maybe they\'ll be back.'))
      }
      return
    }
    if (rec && now < rec.getLong('retry')) return
    if (!questOpen(player, enc) || !npcConditionsMet(player, enc.where)) return
    let spot = npcFindSpot(player, enc.distance[0], enc.distance[1])
    if (!spot) return
    let spawned = player.level.createEntity(enc.entity)
    spawned.setPos(spot.x, spot.y, spot.z)
    let extra = {}
    if (enc.then == 'talk' || enc.then == 'escort') extra.Invulnerable = true
    if (enc.then == 'escort') extra.NoAI = true   // they follow by hopping to your side (npcTickEscorts), not wandering
    if (enc.health) {
      extra.Attributes = [{ Name: 'minecraft:generic.max_health', Base: enc.health }]
      extra.Health = enc.health
    }
    if (enc.glow) extra.Glowing = true
    npcDress(spawned, enc.name, enc.profession, extra)
    spawned.addTag('fq_enc')
    spawned.addTag('fq_enc.' + enc.stage)
    spawned.addTag('fq_owner.' + String(player.uuid))
    spawned.spawn()
    if (enc.then == 'kill') npcBoost(player.server, String(spawned.uuid), enc.boost)
    let newRec = new $NpcCompoundTag()
    newRec.putString('uuid', String(spawned.uuid))
    newRec.putLong('until', now + enc.minutes * 60 * 1000)
    newRec.putLong('retry', 0)
    state.put(enc.stage, newRec)
    if (enc.arrive) player.tell(Text.italic(enc.arrive).gray())
  })
}

function npcEncounterStage(entity) {
  let found = ''
  entity.tags.forEach(tag => {
    let t = String(tag)
    if (t.indexOf('fq_enc.') == 0) found = t.substring(7)
  })
  return found
}

ItemEvents.entityInteracted(event => {
  let { player, target } = event
  if (String(event.hand) != 'MAIN_HAND' || player.level.clientSide || !target.tags.contains('fq_enc')) return
  event.cancel()
  let enc = npcEntryByStage(npcEncounterStage(target))
  if (!enc) return
  if (!target.tags.contains('fq_owner.' + String(player.uuid))) {
    player.tell(Text.gray(enc.name + ' isn\'t looking for you.'))
    return
  }
  if (enc.then == 'escort' && !player.tags.contains(enc.stage)) {
    let rec = npcData(player, 'fqEnc').getCompound(enc.stage)
    if (!rec.getBoolean('escorting')) {
      questSay(player, enc.name, enc.lines)
      rec.putBoolean('escorting', true)
      player.tell(Text.yellow('Take ' + enc.name + ' to ' + (enc.to ? enc.to.label : 'safety') + ". They'll keep up."))
    }
    return
  }
  if (enc.then != 'talk' || player.tags.contains(enc.stage)) return
  questSay(player, enc.name, enc.lines)
  questAddStage(player, enc.stage)
  player.tell(Text.yellow('Quest updated.'))
  event.server.scheduleInTicks(100, () => { if (target.isAlive()) target.discard() })
})

// ---- timed challenges ----
// Goals: kill a number of a mob, raise a statistic, reach a place or a structure, or hold the spot where you started
// (stay within "radius" until the time is up; leaving fails). "waves" spawn mobs around the player (or the held spot)
// every "every" seconds while it runs; they're removed when it ends.

let $NpcQuestWorld = null
try {
  $NpcQuestWorld = Java.loadClass('fotfskills.compat.QuestWorld')
} catch (e) {
  console.warn('quest_npcs: fotfskills QuestWorld not found; structure goals, escorts to structures and build tasks won\'t work')
}

function npcInStructure(level, x, y, z, structures) {
  if (!$NpcQuestWorld) return false
  return structures.some(s => $NpcQuestWorld.inStructure(level, x, y, z, s))
}

function npcInBox(entity, box) {
  return String(entity.level.dimension) == box.dimension && entity.x >= box.min[0] && entity.x <= box.max[0]
    && entity.y >= box.min[1] && entity.y <= box.max[1] && entity.z >= box.min[2] && entity.z <= box.max[2]
}

// has the entity reached a destination ({kind: place, box} or {kind: structure, structures})?
function npcAtDestination(entity, dest) {
  if (dest.kind == 'place') return npcInBox(entity, dest.box)
  return npcInStructure(entity.level, entity.x, entity.y, entity.z, dest.structures)
}

function npcStartChallenge(player, stage) {
  let ch = npcEntries('timed').find(g => g.stage == stage)
  if (!ch || player.tags.contains(stage) || !questOpen(player, ch)) {
    player.tell(Text.gray('There\'s no challenge to start right now.'))
    return false
  }
  let rec = new $NpcCompoundTag()
  rec.putLong('start', Date.now())
  rec.putLong('until', Date.now() + ch.seconds * 1000)
  rec.putInt('count', 0)
  npcRememberSpot(player, rec)
  rec.putDouble('hx', player.x)
  rec.putDouble('hy', player.y)
  rec.putDouble('hz', player.z)
  if (ch.goal.kind == 'stat') rec.putInt('base', npcStatValue(player, ch.goal.stat))
  npcData(player, 'fqTimed').put(stage, rec)
  if (ch.lines.length) questSay(player, ch.name, ch.lines)
  player.tell(Text.yellow('Go! You have ' + ch.seconds + ' seconds.'))
  if (ch.goal.kind == 'hold') player.tell(Text.gray('Hold this spot: stay within ' + ch.goal.radius + ' blocks.'))
  if ((ch.no || []).length) player.tell(Text.gray('No ' + ch.no.map(b => NPC_BAN_WORDS[b]).join(', ') + " until it's over."))
  return true
}

function npcChallengeProgress(player, ch, rec) {
  let goal = ch.goal
  if (goal.kind == 'kill') return [rec.getInt('count'), goal.count]
  if (goal.kind == 'stat') return [npcStatValue(player, goal.stat) - rec.getInt('base'), goal.count]
  if (goal.kind == 'hold') return [0, 1]   // done when the time runs out (npcTickChallenges)
  // "away": the destination only counts this far from where the timer started (the next village, not this one)
  let far = !goal.away || npcHoldDistance(player, rec) >= goal.away
  return [far && npcAtDestination(player, goal) ? 1 : 0, 1]
}

function npcHoldDistance(player, rec) {
  let dx = player.x - rec.getDouble('hx'), dz = player.z - rec.getDouble('hz')
  return Math.sqrt(dx * dx + dz * dz)
}

function npcSpawnWaves(player, ch, rec) {
  let waves = ch.waves || []
  if (!waves.length) return
  let elapsed = (Date.now() - rec.getLong('start')) / 1000
  let cx = ch.goal.kind == 'hold' ? rec.getDouble('hx') : player.x
  let cz = ch.goal.kind == 'hold' ? rec.getDouble('hz') : player.z
  waves.forEach((w, i) => {
    let rounds = rec.getInt('w' + i)
    if (elapsed < rounds * w.every) return
    rec.putInt('w' + i, rounds + 1)
    for (let n = 0; n < w.count; n++) {
      let spot = npcFindSpotAround(player, cx, cz, 10, 16)
      if (!spot) continue
      player.server.runCommandSilent('execute in ' + player.level.dimension + ' run summon ' + w.entity + ' '
        + spot.x + ' ' + spot.y + ' ' + spot.z + ' {Tags:["fq_wave","fq_wave.' + player.uuid + '"]}')
    }
  })
}

function npcClearWaves(player) {
  player.server.runCommandSilent('kill @e[tag=fq_wave.' + player.uuid + ']')
}

function npcFinishChallenge(player, ch, won) {
  npcData(player, 'fqTimed').remove(ch.stage)
  npcClearWaves(player)
  if (won) {
    questAddStage(player, ch.stage)
    player.setStatusMessage(Text.green('Challenge complete!'))
    player.tell(Text.yellow('Challenge complete! Quest updated.'))
  } else {
    player.setStatusMessage(Text.red('Out of time!'))
    player.tell(Text.of([Text.red('Out of time. '),
      Text.green('[Try again]').clickRunCommand('/quest challenge ' + ch.stage).hover('Restart the challenge')]))
  }
}

function npcTickChallenges(player) {
  let running = npcData(player, 'fqTimed')
  let prompted = npcData(player, 'fqTimedPrompt')
  let now = Date.now()
  npcEntries('timed').forEach(ch => {
    if (player.tags.contains(ch.stage)) {
      if (running.contains(ch.stage)) running.remove(ch.stage)
      return
    }
    if (running.contains(ch.stage)) {
      let rec = running.getCompound(ch.stage)
      let broken = npcBrokenBan(player, ch, rec)
      if (!broken && ch.goal.kind == 'hold' && npcHoldDistance(player, rec) > ch.goal.radius) broken = 'You left the spot.'
      if (broken) {
        npcFailChallenge(player, ch, broken)
        return
      }
      let progress = npcChallengeProgress(player, ch, rec)
      let left = Math.ceil((rec.getLong('until') - now) / 1000)
      if (progress[0] >= progress[1]) {
        npcFinishChallenge(player, ch, true)
      } else if (left <= 0) {
        npcFinishChallenge(player, ch, ch.goal.kind == 'hold')
      } else {
        npcSpawnWaves(player, ch, rec)
        let label = ch.goal.kind == 'hold' ? 'Hold on'
          : (ch.goal.kind == 'place' || ch.goal.kind == 'structure') ? 'Reach ' + ch.goal.label
          : progress[0] + ' / ' + progress[1]
        player.setStatusMessage(Text.of([Text.gold(left + 's  '), Text.white(label)]))
      }
      return
    }
    if (now - prompted.getLong(ch.stage) < NPC_CHALLENGE_PROMPT_MS || !questOpen(player, ch)) return
    prompted.putLong(ch.stage, now)
    player.tell(Text.of([Text.gold('A challenge is ready. '),
      Text.green('[' + ch.start + ']').clickRunCommand('/quest challenge ' + ch.stage).hover('Start the timer')]))
  })
}

// ---- escorts (encounter "then": "escort") ----
// Talk to them and they come along: they keep up with you (a short hop to your side whenever you're more than a few
// blocks ahead) until they reach the destination, then thank you and the step is done.

function npcTickEscorts(player) {
  let state = npcData(player, 'fqEnc')
  npcEntries('encounter').forEach(enc => {
    if (enc.then != 'escort' || !state.contains(enc.stage) || player.tags.contains(enc.stage)) return
    let rec = state.getCompound(enc.stage)
    if (!rec.getBoolean('escorting')) return
    let entity = npcEntity(player, String(rec.getString('uuid')))
    if (!entity || !entity.isAlive()) {
      rec.putBoolean('escorting', false)   // lost (unloaded, other dimension): they turn up again and wait to be asked
      return
    }
    rec.putLong('until', Date.now() + enc.minutes * 60 * 1000)
    if (enc.to && npcAtDestination(entity, enc.to)) {
      if (enc.thanks && enc.thanks.length) questSay(player, enc.name, enc.thanks)
      questAddStage(player, enc.stage)
      player.tell(Text.yellow('Quest updated.'))
      player.server.scheduleInTicks(100, () => { if (entity.isAlive()) entity.discard() })
      state.remove(enc.stage)
      return
    }
    let dx = entity.x - player.x, dz = entity.z - player.z
    let dist = Math.sqrt(dx * dx + dz * dz)
    if (dist > 3.5) {
      let k = dist > 0.01 ? 2 / dist : 0
      player.server.runCommandSilent('execute in ' + player.level.dimension + ' run tp ' + entity.uuid + ' '
        + (player.x + dx * k) + ' ' + player.y + ' ' + (player.z + dz * k) + ' facing entity ' + player.uuid)
    }
  })
}

// ---- build tasks ----
// Only blocks the player places while the step is open count (so blocks already standing there never do): each
// placement is remembered, and every 5 seconds the remembered blocks still standing within "radius" of the player
// are counted against the list. Breaking one takes it off the count.

const NPC_BUILD_MAX = 512   // remembered placements per build step

function npcBlockMatches(block, key) {
  if (key.charAt(0) == '#') return block.hasTag(key.substring(1))
  return String(block.id) == key
}

BlockEvents.placed(event => {
  let player = event.player
  if (!player || player.level.clientSide) return
  let open = npcEntries('build').filter(b => !player.tags.contains(b.stage) && questOpen(player, b)
    && b.keys.some(k => npcBlockMatches(event.block, k)))
  if (!open.length) return
  let all = npcData(player, 'fqBuild')
  let spot = String(player.level.dimension) + '|' + event.block.x + '|' + event.block.y + '|' + event.block.z
  open.forEach(b => {
    let placed = all.contains(b.stage) ? all.getCompound(b.stage) : new $NpcCompoundTag()
    if (placed.allKeys.size() < NPC_BUILD_MAX) placed.putBoolean(spot, true)
    all.put(b.stage, placed)
  })
})

let $NpcQuestAreas = null
try {
  $NpcQuestAreas = Java.loadClass('fotfskills.compat.QuestAreas')
} catch (e) {
  $NpcQuestAreas = null
}

function npcTickBuilds(player) {
  let all = npcData(player, 'fqBuild')
  // the blocks open build steps need may be placed even in protected areas (fotfskills QuestAreas)
  if ($NpcQuestAreas) {
    let keys = []
    npcEntries('build').forEach(b => {
      if (!player.tags.contains(b.stage) && questOpen(player, b)) b.keys.forEach(k => { if (keys.indexOf(k) < 0) keys.push(k) })
    })
    $NpcQuestAreas.setAllowed(String(player.uuid), keys)
  }
  npcEntries('build').forEach(b => {
    if (player.tags.contains(b.stage)) {
      if (all.contains(b.stage)) all.remove(b.stage)
      return
    }
    if (!all.contains(b.stage) || !questOpen(player, b)) return
    let placed = all.getCompound(b.stage)
    let counts = b.keys.map(() => 0)
    let dim = String(player.level.dimension)
    let gone = []
    placed.allKeys.forEach(spot => {
      let p = String(spot).split('|')
      if (p[0] != dim) return
      let x = Number(p[1]), y = Number(p[2]), z = Number(p[3])
      let dx = x + 0.5 - player.x, dy = y + 0.5 - player.y, dz = z + 0.5 - player.z
      if (dx * dx + dy * dy + dz * dz > b.radius * b.radius) return
      let block = player.level.getBlock(x, y, z)
      let hit = false
      b.keys.forEach((k, i) => { if (npcBlockMatches(block, k)) { counts[i]++; hit = true } })
      if (!hit) gone.push(String(spot))
    })
    gone.forEach(spot => placed.remove(spot))
    for (let i = 0; i < b.counts.length; i++) {
      if (counts[i] < b.counts[i]) return
    }
    all.remove(b.stage)
    questAddStage(player, b.stage)
    player.tell(Text.yellow('That looks right. Quest updated.'))
  })
}

// ---- tame and breed tasks ----
// tame: every 5 seconds, animals of the listed kinds within 24 blocks that belong to the player are noted. Those
// already theirs when the step opened are ignored; each new one counts. Works for any mod's pet that saves its owner
// as "Owner" or "OwnerUUID" (vanilla tameables and horses, and most modded pets).
// breed: Forge's baby event (startup_scripts/quest_breeding.js) counts babies the player bred while the step is open.

let $NpcAABB = Java.loadClass('net.minecraft.world.phys.AABB')
const NPC_TAME_RANGE = 24

function npcOwnerOf(entity) {
  let nbt = entity.nbt
  if (!nbt) return ''
  try {
    if (nbt.hasUUID('Owner')) return String(nbt.getUUID('Owner'))
  } catch (e) {
    // not a UUID here
  }
  return String(nbt.getString('Owner') || nbt.getString('OwnerUUID') || '')
}

function npcTickTames(player) {
  let open = npcEntries('tame').filter(t => !player.tags.contains(t.stage) && questOpen(player, t))
  if (!open.length) return
  let me = String(player.uuid)
  let r = NPC_TAME_RANGE
  let box = new $NpcAABB(player.x - r, player.y - r, player.z - r, player.x + r, player.y + r, player.z + r)
  let owned = []
  player.level.getEntitiesWithin(box).forEach(e => {
    let type = String(e.type)
    if (open.some(t => t.entities.indexOf(type) >= 0) && npcOwnerOf(e) == me) owned.push({ type: type, id: String(e.uuid) })
  })
  let all = npcData(player, 'fqTame')
  open.forEach(t => {
    let first = !all.contains(t.stage)
    let rec = first ? new $NpcCompoundTag() : all.getCompound(t.stage)
    owned.forEach(o => {
      if (t.entities.indexOf(o.type) >= 0 && !rec.contains(o.id)) rec.putInt(o.id, first ? 0 : 1)
    })
    all.put(t.stage, rec)
    let count = 0
    rec.allKeys.forEach(k => { if (rec.getInt(k) == 1) count++ })
    if (count >= t.count) {
      all.remove(t.stage)
      questAddStage(player, t.stage)
      player.tell(Text.yellow('Tamed. Quest updated.'))
    }
  })
}

global.fqOnBred = (player, child) => {
  if (!player || player.level.clientSide) return
  let type = String(child.type)
  let counts = npcData(player, 'fqBreed')
  npcEntries('breed').forEach(b => {
    if (player.tags.contains(b.stage) || b.entities.indexOf(type) < 0 || !questOpen(player, b)) return
    let n = counts.getInt(b.stage) + 1
    if (n >= b.count) {
      counts.remove(b.stage)
      questAddStage(player, b.stage)
      player.tell(Text.yellow('Bred. Quest updated.'))
    } else {
      counts.putInt(b.stage, n)
    }
  })
}

// ---- spawned enemies (kill tasks with "spawn") ----
// Reach the quest's place while its kill step is open and the enemies come: a wave around you, and another about 15
// seconds after the last one falls, until FTB Quests counts the kills done. The fight is anchored where it started;
// wander more than 48 blocks from there (or finish) and any leftovers vanish. Kills count as normal FTB kills, so
// friends nearby share them (SharedKillHooks).

const NPC_SPAWN_GAP_MS = 15 * 1000
const NPC_SPAWN_LEASH = 48

function npcTaskDone(player, taskHex) {
  if (!$QuestFile || !$QuestFile.INSTANCE) return false
  try {
    let file = $QuestFile.INSTANCE
    let data = file['getOrCreateTeamData(net.minecraft.world.entity.Entity)'](player)
    let task = file.getTask($QuestLong.parseLong(taskHex, 16))
    return task != null && data.isCompleted(task)
  } catch (e) {
    return false
  }
}

function npcSpawnTag(player, sp) {
  return 'fq_spawn.' + String(player.uuid).substring(0, 8) + '.' + sp.task_id
}

function npcTickSpawns(player) {
  let state = npcData(player, 'fqSpawn')
  let server = player.server
  let now = Date.now()
  npcEntries('spawn').forEach(sp => {
    let tag = npcSpawnTag(player, sp)
    let active = !player.tags.contains(sp.stage) && questOpen(player, sp) && !npcTaskDone(player, sp.task_id)
    let rec = state.contains(sp.stage) ? state.getCompound(sp.stage) : null
    if (rec) {
      let dx = player.x - rec.getDouble('x'), dz = player.z - rec.getDouble('z')
      let away = rec.getString('dim') != String(player.level.dimension) || dx * dx + dz * dz > NPC_SPAWN_LEASH * NPC_SPAWN_LEASH
      if (!active || away) {
        server.runCommandSilent('kill @e[tag=' + tag + ']')
        state.remove(sp.stage)
        return
      }
    } else if (!active || !npcAtDestination(player, sp.at)) {
      return
    }
    if (!rec) {
      rec = new $NpcCompoundTag()
      rec.putString('dim', String(player.level.dimension))
      rec.putDouble('x', player.x)
      rec.putDouble('z', player.z)
      rec.putLong('next', 0)
      state.put(sp.stage, rec)
      if (sp.name) player.tell(Text.italic((sp.name) + '... here they come.').gray())
    }
    if (now < rec.getLong('next') || server.runCommandSilent('execute if entity @e[tag=' + tag + ']') > 0) return
    // "ensure" (bosses): the structure's own is fought if it's still there; one is only brought in if it's gone
    if (sp.ensure && server.runCommandSilent('execute as ' + player.uuid + ' at @s if entity @e[type=' + sp.entity
      + ',distance=..64]') > 0) {
      rec.putLong('next', now + NPC_SPAWN_GAP_MS)
      return
    }
    let nbt = { Tags: [tag, 'fq_new'] }
    if (sp.name) nbt.CustomName = JSON.stringify({ text: sp.name })
    if (sp.glow) nbt.Glowing = true
    if (sp.health) {
      nbt.Attributes = [{ Name: 'minecraft:generic.max_health', Base: sp.health }]
      nbt.Health = sp.health
    }
    for (let i = 0; i < sp.wave; i++) {
      let spot = npcFindSpot(player, 16, 28)
      if (!spot) continue
      server.runCommandSilent('execute in ' + player.level.dimension + ' run summon ' + sp.entity + ' ' + spot.x + ' '
        + spot.y + ' ' + spot.z + ' ' + JSON.stringify(nbt))
      npcBoost(server, '@e[tag=fq_new]', sp.boost)
      server.runCommandSilent('tag @e[tag=fq_new] remove fq_new')
    }
    rec.putLong('next', now + NPC_SPAWN_GAP_MS)
  })
}

// ---- spellkill tasks ----
// A kill counts when one of Iron's Spells' schools landed the killing blow (its damage types' message ids).

const NPC_SPELL_DAMAGE = { fire_magic: 'fire', fire_field: 'fire', ice_magic: 'ice', lightning_magic: 'lightning',
  holy_magic: 'holy', ender_magic: 'ender', dragon_breath_pool: 'ender', blood_magic: 'blood', heartstop: 'blood',
  blood_cauldron: 'blood', evocation_magic: 'evocation', nature_magic: 'nature', poison_cloud: 'nature',
  eldritch_magic: 'eldritch' }

function npcCountSpellKill(player, entity, source) {
  let msg = ''
  try { msg = String(source.getType()) } catch (e) { msg = '' }
  let school = NPC_SPELL_DAMAGE[msg]
  if (!school) return
  let type = String(entity.type)
  let counts = npcData(player, 'fqSpellKill')
  npcEntries('spellkill').forEach(k => {
    if (player.tags.contains(k.stage) || (k.school != 'any' && k.school != school)
      || (k.entities.length && k.entities.indexOf(type) < 0) || !questOpen(player, k)) return
    let n = counts.getInt(k.stage) + 1
    if (n >= k.count) {
      counts.remove(k.stage)
      questAddStage(player, k.stage)
      player.tell(Text.yellow('Quest updated.'))
    } else {
      counts.putInt(k.stage, n)
      player.setStatusMessage(Text.gray(n + ' / ' + k.count))
    }
  })
}

// ---- cast tasks ----
// Iron's Spells casts (startup_scripts/quest_casting.js) count toward open "cast" steps: any spell, one spell, or a
// school's spells.

global.fqOnCast = (player, spellId, school) => {
  let counts = npcData(player, 'fqCast')
  npcEntries('cast').forEach(c => {
    if (player.tags.contains(c.stage) || (c.spell && c.spell != spellId) || (c.school && c.school != school)
      || !questOpen(player, c)) return
    let n = counts.getInt(c.stage) + 1
    if (n >= c.count) {
      counts.remove(c.stage)
      questAddStage(player, c.stage)
      player.tell(Text.yellow('Quest updated.'))
    } else {
      counts.putInt(c.stage, n)
      if (c.count >= 10 && n % Math.max(1, Math.floor(c.count / 10)) == 0) player.setStatusMessage(Text.gray('Spells cast: ' + n + ' / ' + c.count))
    }
  })
}

// ---- mine, skill_level and stats tasks ----
// mine: blocks broken while the step is open (Ultimine breaks each block, so they all count).
// skill_level: a Pufferfish skill tree's level (checked every 5 seconds). stats: the lifetime sum of several vanilla
// statistics (checked every 5 seconds), for milestones like distance travelled on foot.

let $NpcSkillsAPI = null
try {
  $NpcSkillsAPI = Java.loadClass('net.puffish.skillsmod.api.SkillsAPI')
} catch (e) {
  console.warn("quest_npcs: Pufferfish's Skills not found; skill_level tasks won't work")
}

BlockEvents.broken(event => {
  let player = event.player
  if (!player || player.level.clientSide) return
  let counts = null
  npcEntries('mine').forEach(m => {
    if (player.tags.contains(m.stage) || (m.keys.length && !m.keys.some(k => npcBlockMatches(event.block, k)))
      || !questOpen(player, m)) return
    if (!counts) counts = npcData(player, 'fqMine')
    let n = counts.getInt(m.stage) + 1
    if (n >= m.count) {
      counts.remove(m.stage)
      questAddStage(player, m.stage)
      player.tell(Text.yellow('Quest updated.'))
    } else {
      counts.putInt(m.stage, n)
      if (m.count >= 50 && n % Math.floor(m.count / 10) == 0) player.setStatusMessage(Text.gray(n + ' / ' + m.count))
    }
  })
})

function npcSkillLevel(player, tree) {
  if (!$NpcSkillsAPI) return 0
  let best = 0
  $NpcSkillsAPI.streamCategories().toList().forEach(cat => {
    if (tree != 'any' && String(cat.getId()) != 'puffish_skills:' + tree) return
    let xp = cat.getExperience()
    if (xp.isPresent()) best = Math.max(best, xp.get().getLevel(player))
  })
  return best
}

function npcTickMilestones(player) {
  npcEntries('skill_level').forEach(k => {
    if (player.tags.contains(k.stage) || !questOpen(player, k) || npcSkillLevel(player, k.tree) < k.level) return
    questAddStage(player, k.stage)
    player.tell(Text.yellow('Milestone reached. Quest updated.'))
  })
  npcEntries('stats').forEach(k => {
    if (player.tags.contains(k.stage) || !questOpen(player, k)) return
    let sum = 0
    k.stats.forEach(st => { sum += npcStatValue(player, st) })
    if (sum < k.count) return
    questAddStage(player, k.stage)
    player.tell(Text.yellow('Milestone reached. Quest updated.'))
  })
}

// ---- waystones tasks ----
// Every 5 seconds: how many waystones the player has attuned (Waystones' own list), optionally only wild ones. The
// count when the step opened is the baseline; the step is done when that many more have been attuned.

let $NpcPlayerWaystones = null
try {
  $NpcPlayerWaystones = Java.loadClass('net.blay09.mods.waystones.core.PlayerWaystoneManager')
} catch (e) {
  console.warn("quest_npcs: Waystones not found; waystones tasks won't work")
}

function npcWaystoneCount(player, wild) {
  let n = 0
  $NpcPlayerWaystones.getWaystones(player).forEach(w => {
    if (!wild || String(w.getOrigin()) == 'WILDERNESS') n++
  })
  return n
}

function npcTickWaystones(player) {
  if (!$NpcPlayerWaystones) return
  let bases = npcData(player, 'fqWaystones')
  npcEntries('waystones').forEach(t => {
    if (player.tags.contains(t.stage)) {
      if (bases.contains(t.stage)) bases.remove(t.stage)
      return
    }
    if (!questOpen(player, t)) return
    let now = npcWaystoneCount(player, t.wild)
    if (t.total) {
      if (now >= t.count) {
        questAddStage(player, t.stage)
        player.tell(Text.yellow('Milestone reached. Quest updated.'))
      }
      return
    }
    if (!bases.contains(t.stage)) {
      bases.putInt(t.stage, now)
      return
    }
    if (now - bases.getInt(t.stage) >= t.count) {
      bases.remove(t.stage)
      questAddStage(player, t.stage)
      player.tell(Text.yellow('Route marked. Quest updated.'))
    }
  })
}

// ---- shortcuts a challenge switches off (timed "no") ----
// teleport: waystones, warp and return scrolls, warp stones, chorus fruit, and (caught afterwards) any jump of over
// 64 blocks in a second or a change of dimension. mounts: you're taken off whatever you ride. elytra: gliding ends the
// challenge. pearls: ender pearls can't be thrown. Grappling hooks are always allowed.

const NPC_BAN_WORDS = { teleport: 'teleporting', mounts: 'riding', elytra: 'gliding', pearls: 'ender pearls',
  hurt: 'getting hit' }
const NPC_TELEPORT_ITEMS = ['waystones:warp_scroll', 'waystones:bound_scroll', 'waystones:return_scroll',
  'waystones:warp_stone', 'minecraft:chorus_fruit']
const NPC_TELEPORT_DISTANCE = 64

// the bans of every challenge this player has running: { teleport: challenge, ... }
function npcBans(player) {
  let running = npcData(player, 'fqTimed')
  let bans = {}
  npcEntries('timed').forEach(ch => {
    if (running.contains(ch.stage)) (ch.no || []).forEach(b => { bans[b] = ch })
  })
  return bans
}

function npcItemBan(id) {
  if (NPC_TELEPORT_ITEMS.indexOf(id) >= 0) return 'teleport'
  if (id == 'minecraft:ender_pearl') return 'pearls'
  return null
}

function npcRememberSpot(player, rec) {
  rec.putString('dim', String(player.level.dimension))
  rec.putDouble('x', player.x)
  rec.putDouble('y', player.y)
  rec.putDouble('z', player.z)
}

// checked once a second while the challenge runs; returns why it failed, or null
function npcBrokenBan(player, ch, rec) {
  let no = ch.no || []
  if (!no.length) return null
  let server = player.server
  if (no.indexOf('mounts') >= 0
    && server.runCommandSilent('execute as ' + player.uuid + ' on vehicle run ride ' + player.uuid + ' dismount') > 0) {
    player.setStatusMessage(Text.red('No riding during this challenge'))
  }
  if (no.indexOf('elytra') >= 0
    && server.runCommandSilent('execute as ' + player.uuid + ' if entity @s[nbt={FallFlying:1b}]') > 0) {
    return 'No gliding in this challenge.'
  }
  if (no.indexOf('teleport') >= 0) {
    let dx = player.x - rec.getDouble('x'), dy = player.y - rec.getDouble('y'), dz = player.z - rec.getDouble('z')
    if (rec.getString('dim') != String(player.level.dimension)
      || dx * dx + dy * dy + dz * dz > NPC_TELEPORT_DISTANCE * NPC_TELEPORT_DISTANCE) {
      return 'No teleporting in this challenge.'
    }
  }
  npcRememberSpot(player, rec)
  return null
}

function npcFailChallenge(player, ch, why) {
  npcData(player, 'fqTimed').remove(ch.stage)
  npcClearWaves(player)
  player.setStatusMessage(Text.red('Challenge failed'))
  player.tell(Text.of([Text.red(why + ' '),
    Text.green('[Try again]').clickRunCommand('/quest challenge ' + ch.stage).hover('Restart the challenge')]))
}

ItemEvents.rightClicked(event => {
  let player = event.player
  if (!player || player.level.clientSide) return
  let ban = npcItemBan(String(event.item.id))
  if (ban && npcBans(player)[ban]) {
    player.setStatusMessage(Text.red('No ' + NPC_BAN_WORDS[ban] + ' during this challenge'))
    event.cancel()
  }
})

BlockEvents.rightClicked(event => {
  let player = event.player
  if (!player || player.level.clientSide || String(event.block.id).indexOf('waystones:') != 0) return
  if (npcBans(player).teleport) {
    player.setStatusMessage(Text.red('No teleporting during this challenge'))
    event.cancel()
  }
})

// hurt: taking damage from any creature fails a stealth challenge
EntityEvents.hurt('minecraft:player', event => {
  let player = event.entity
  if (player.level.clientSide) return
  let attacker = null
  try { attacker = event.source.actual } catch (e) { attacker = null }
  if (!attacker || attacker.isPlayer()) return
  let ch = npcBans(player).hurt
  if (ch) npcFailChallenge(player, ch, 'You were caught.')
})

// ---- ticking and kills ----

PlayerEvents.tick(event => {
  let player = event.player
  if (player.level.clientSide || player.tickCount % 20 != 0) return
  npcTickChallenges(player)
  npcTickEscorts(player)
  if (player.tickCount % 40 == 0) npcTickEncounters(player)
  if (player.tickCount % 40 == 10) npcTickSpawns(player)
  if (player.tickCount % 100 == 0) npcTickBuilds(player)
  if (player.tickCount % 100 == 50) npcTickTames(player)
  if (player.tickCount % 100 == 75) npcTickWaystones(player)
  if (player.tickCount % 100 == 25) npcTickMilestones(player)
})

EntityEvents.death(event => {
  let { entity, source } = event
  if (entity.level.clientSide) return
  // a defeated encounter completes its owner's step (whoever landed the last hit)
  if (entity.tags.contains('fq_enc')) {
    let enc = npcEntryByStage(npcEncounterStage(entity))
    if (enc && enc.then == 'kill') {
      let owner = null
      event.server.players.forEach(p => { if (entity.tags.contains('fq_owner.' + String(p.uuid))) owner = p })
      if (owner && !owner.tags.contains(enc.stage)) {
        questAddStage(owner, enc.stage)
        owner.tell(Text.yellow(enc.name + ' is defeated. Quest updated.'))
      }
    }
  }
  // kills for running timed challenges
  let player = source.player
  if (!player) return
  npcCountSpellKill(player, entity, source)
  let running = npcData(player, 'fqTimed')
  let type = String(entity.type)
  npcEntries('timed').forEach(ch => {
    if (ch.goal.kind == 'kill' && ch.goal.entity == type && running.contains(ch.stage)) {
      let rec = running.getCompound(ch.stage)
      rec.putInt('count', rec.getInt('count') + 1)
    }
  })
})
