// Quest givers you can spot, and characters who speak up.
// Markers: every 2 seconds, quest characters and villagers within 16 blocks that have something for you show a small
// burst of particles above their heads, sent to you alone: green for a step of a quest you're on, gold for a new quest.
// Call-outs: walk within 5 blocks of a quest character who has something for you and now and then they call out
// (pack.json "hail" lines, or a default). Never idle chatter. At most one call-out every 10 minutes per player, and
// each character at most once an hour, so chat stays quiet (Dylan and Fionah, 2026-10-15).

let $AmbientAABB = Java.loadClass('net.minecraft.world.phys.AABB')
const AMBIENT_MARK_RANGE = 16
const AMBIENT_TALK_RANGE = 5
const AMBIENT_TALK_GAP_MS = 10 * 60 * 1000
const AMBIENT_CHARACTER_GAP_MS = 60 * 60 * 1000
const AMBIENT_TALK_CHANCE = 0.5
const AMBIENT_HAILS = ['A word?', 'Got a moment?']

// 'talk' (a step of a quest you're on), 'offer' (a new quest) or '' for this villager or character
function ambientStatus(player, target) {
  let givers = questGivers()
  if (givers.some(g => g.type == 'talk' && questMatches(g, target) && questHasAll(player, g.requires)
    && !player.tags.contains(g.stage) && questOpen(player, g))) return 'talk'
  return questOfferFor(player, target) ? 'offer' : ''
}

function ambientMark(player, target, status) {
  let y = target.y + target.eyeHeight + 0.75
  let particle = status == 'talk' ? 'minecraft:happy_villager' : 'minecraft:wax_on'
  player.server.runCommandSilent('execute in ' + player.level.dimension + ' run particle ' + particle + ' '
    + target.x + ' ' + y + ' ' + target.z + ' 0.15 0.2 0.15 0 5 force ' + player.username)
}

function ambientSpeak(player, target, status, now) {
  let gaps = npcData(player, 'fqAmbient')
  if (now - gaps.getLong('_last') < AMBIENT_TALK_GAP_MS) return
  let id = questCharacterId(target)
  if (now - gaps.getLong(id) < AMBIENT_CHARACTER_GAP_MS || Math.random() > AMBIENT_TALK_CHANCE) return
  let info = (global.QUEST_CHARACTERS || {})[id] || {}
  if (!status) return   // only when they have something for you
  let hails = info.hail && info.hail.length ? info.hail : AMBIENT_HAILS
  let line = hails[Math.floor(Math.random() * hails.length)]
  gaps.putLong('_last', now)
  gaps.putLong(id, now)
  questSay(player, String(target.displayName.string), [line])
}

PlayerEvents.tick(event => {
  let player = event.player
  if (player.level.clientSide || player.server.tickCount % 40 != 20 || player.spectator) return
  let r = AMBIENT_MARK_RANGE
  let box = new $AmbientAABB(player.x - r, player.y - r, player.z - r, player.x + r, player.y + r, player.z + r)
  let now = Date.now()
  let closest = null
  player.level.getEntitiesWithin(box).forEach(e => {
    let character = e.tags.contains('fq_npc')
    if (!character && String(e.type) != 'minecraft:villager') return
    if (e.tags.contains('fq_enc')) return
    let status = ambientStatus(player, e)
    if (status) ambientMark(player, e, status)
    if (character) {
      let dx = e.x - player.x, dy = e.y - player.y, dz = e.z - player.z
      let d2 = dx * dx + dy * dy + dz * dz
      if (d2 <= AMBIENT_TALK_RANGE * AMBIENT_TALK_RANGE && (!closest || d2 < closest.d2)) {
        closest = { e: e, status: status, d2: d2 }
      }
    }
  })
  if (closest) ambientSpeak(player, closest.e, closest.status, now)
})
