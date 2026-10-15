// Photo tasks (Camerapture): a quest step completes when the player takes a picture while the step is open and the
// subject is right. A new picture is one that lands in the player's inventory with them as its creator and a fresh
// timestamp; copies (same picture data) never count twice. Subjects (from the generator): an entity type under the
// crosshair or within 8 blocks, or standing in a structure, biome or named place (quest_npcs.js helpers).

let $PhotoAABB = Java.loadClass('net.minecraft.world.phys.AABB')
const PHOTO_FRESH_MS = 2 * 60 * 1000
const PHOTO_NEAR = 8

function photoIsNew(player, item) {
  let nbt = item.nbt
  if (!nbt || String(nbt.getString('creator')) != String(player.username)) return false
  let ts = Number(nbt.getLong('timestamp'))
  if (ts < 100000000000) ts *= 1000   // seconds, not milliseconds
  if (Math.abs(Date.now() - ts) > PHOTO_FRESH_MS) return false
  let seen = npcData(player, 'fqPhotos')
  let key = String(nbt.toString())
  if (seen.contains(key)) return false
  seen.putLong(key, Date.now())
  return true
}

function photoSubjectFits(player, target) {
  if (target.kind == 'biome') return String(player.block.biomeId) == target.biome
  if (target.kind == 'place' || target.kind == 'structure') return npcAtDestination(player, target)
  if (target.kind != 'entity') return false
  try {
    let hit = player.rayTrace(target.distance)
    if (hit && hit.entity && String(hit.entity.type) == target.entity) return true
  } catch (e) {
    // no ray trace here: fall back to nearby
  }
  let box = new $PhotoAABB(player.x - PHOTO_NEAR, player.y - PHOTO_NEAR, player.z - PHOTO_NEAR,
    player.x + PHOTO_NEAR, player.y + PHOTO_NEAR, player.z + PHOTO_NEAR)
  let found = false
  player.level.getEntitiesWithin(box).forEach(e => { if (String(e.type) == target.entity) found = true })
  return found
}

PlayerEvents.inventoryChanged(event => {
  let player = event.player
  let item = event.item
  if (player.level.clientSide || String(item.id) != 'camerapture:picture' || !photoIsNew(player, item)) return
  npcEntries('photo').forEach(ph => {
    if (player.tags.contains(ph.stage) || !questOpen(player, ph) || !photoSubjectFits(player, ph.target)) return
    questAddStage(player, ph.stage)
    player.setStatusMessage(Text.yellow('That\'s the shot. Quest updated.'))
  })
})
