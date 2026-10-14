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
      ;['fqOffers', 'fqDropped', 'fqEnc', 'fqTimed', 'fqTimedPrompt'].forEach(k => data.remove(k))
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
      let entity = player.level.createEntity(info.entity || 'minecraft:villager')
      entity.setPos(player.x, player.y, player.z)
      npcDress(entity, info.name, info.profession, { Invulnerable: true, NoAI: true, Silent: true })
      entity.addTag('fq_npc')
      entity.addTag('fq_npc.' + id)
      entity.spawn()
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
  let level = player.level
  for (let attempt = 0; attempt < 24; attempt++) {
    let angle = Math.random() * Math.PI * 2
    let dist = minDist + Math.random() * (maxDist - minDist)
    let x = Math.floor(player.x + Math.cos(angle) * dist)
    let z = Math.floor(player.z + Math.sin(angle) * dist)
    for (let dy = 6; dy >= -6; dy--) {
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
    if (enc.then == 'talk') extra.Invulnerable = true
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
  if (enc.then != 'talk' || player.tags.contains(enc.stage)) return
  questSay(player, enc.name, enc.lines)
  questAddStage(player, enc.stage)
  player.tell(Text.yellow('Quest updated.'))
  event.server.scheduleInTicks(100, () => { if (target.isAlive()) target.discard() })
})

// ---- timed challenges ----

function npcStartChallenge(player, stage) {
  let ch = npcEntries('timed').find(g => g.stage == stage)
  if (!ch || player.tags.contains(stage) || !questOpen(player, ch)) {
    player.tell(Text.gray('There\'s no challenge to start right now.'))
    return false
  }
  let rec = new $NpcCompoundTag()
  rec.putLong('until', Date.now() + ch.seconds * 1000)
  rec.putInt('count', 0)
  npcRememberSpot(player, rec)
  if (ch.goal.kind == 'stat') rec.putInt('base', npcStatValue(player, ch.goal.stat))
  npcData(player, 'fqTimed').put(stage, rec)
  if (ch.lines.length) questSay(player, ch.name, ch.lines)
  player.tell(Text.yellow('Go! You have ' + ch.seconds + ' seconds.'))
  if ((ch.no || []).length) player.tell(Text.gray('No ' + ch.no.map(b => NPC_BAN_WORDS[b]).join(', ') + " until it's over."))
  return true
}

function npcChallengeProgress(player, ch, rec) {
  let goal = ch.goal
  if (goal.kind == 'kill') return [rec.getInt('count'), goal.count]
  if (goal.kind == 'stat') return [npcStatValue(player, goal.stat) - rec.getInt('base'), goal.count]
  let box = goal.box
  let inside = String(player.level.dimension) == box.dimension && player.x >= box.min[0] && player.x <= box.max[0]
    && player.y >= box.min[1] && player.y <= box.max[1] && player.z >= box.min[2] && player.z <= box.max[2]
  return [inside ? 1 : 0, 1]
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
      if (broken) {
        npcFailChallenge(player, ch, broken)
        return
      }
      let progress = npcChallengeProgress(player, ch, rec)
      let left = Math.ceil((rec.getLong('until') - now) / 1000)
      if (progress[0] >= progress[1]) {
        running.remove(ch.stage)
        questAddStage(player, ch.stage)
        player.setStatusMessage(Text.green('Challenge complete!'))
        player.tell(Text.yellow('Challenge complete! Quest updated.'))
      } else if (left <= 0) {
        running.remove(ch.stage)
        player.setStatusMessage(Text.red('Out of time!'))
        player.tell(Text.of([Text.red('Out of time. '),
          Text.green('[Try again]').clickRunCommand('/quest challenge ' + ch.stage).hover('Restart the challenge')]))
      } else {
        let label = ch.goal.kind == 'place' ? 'Reach ' + ch.goal.label : progress[0] + ' / ' + progress[1]
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

// ---- shortcuts a challenge switches off (timed "no") ----
// teleport: waystones, warp and return scrolls, warp stones, chorus fruit, and (caught afterwards) any jump of over
// 64 blocks in a second or a change of dimension. mounts: you're taken off whatever you ride. elytra: gliding ends the
// challenge. pearls: ender pearls can't be thrown. Grappling hooks are always allowed.

const NPC_BAN_WORDS = { teleport: 'teleporting', mounts: 'riding', elytra: 'gliding', pearls: 'ender pearls' }
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

// ---- ticking and kills ----

PlayerEvents.tick(event => {
  let player = event.player
  if (player.level.clientSide || player.tickCount % 20 != 0) return
  npcTickChallenges(player)
  if (player.tickCount % 40 == 0) npcTickEncounters(player)
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
  let running = npcData(player, 'fqTimed')
  let type = String(entity.type)
  npcEntries('timed').forEach(ch => {
    if (ch.goal.kind == 'kill' && ch.goal.entity == type && running.contains(ch.stage)) {
      let rec = running.getCompound(ch.stage)
      rec.putInt('count', rec.getInt('count') + 1)
    }
  })
})
