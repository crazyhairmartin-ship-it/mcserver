// Per-player keep inventory.
// Players listed below keep their inventory, armor, offhand and Curios slots when they die.
// XP is NOT kept. Everyone else drops items into a Gravestone as normal.
// Safety: if saving the inventory fails, nothing is cleared and items drop into a grave like normal.
// Note: KubeJS runs on Rhino, which trips over const/let redeclarations inside try blocks,
// so every variable below has a unique name.

let KEEP_INVENTORY_PLAYERS = [
  'eb12e817-cb4c-4459-9e72-58b460d6e454', // teenytiniestcat
]

let $ListTag = Java.loadClass('net.minecraft.nbt.ListTag')
let $CompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')
let $CuriosApi = Java.loadClass('top.theillusivec4.curios.api.CuriosApi')

let SNAPSHOT_KEY = 'keepInventorySnapshots'
let TAG_COMPOUND = 10

// Snapshots live in the server's saved data so they survive a restart while the player is dead.
function kiSnapshots(server) {
  let serverData = server.persistentData
  if (!serverData.contains(SNAPSHOT_KEY)) serverData.put(SNAPSHOT_KEY, new $CompoundTag())
  return serverData.getCompound(SNAPSHOT_KEY)
}

function kiCurios(player) {
  return $CuriosApi.getCuriosInventory(player).resolve().orElse(null)
}

function kiRestore(player, server) {
  let restoreUuid = String(player.uuid)
  let allSnaps = kiSnapshots(server)
  if (!allSnaps.contains(restoreUuid) || !player.isAlive()) return

  let savedSnap = allSnaps.getCompound(restoreUuid)
  try {
    // Hold on to anything the player got on respawn (e.g. from other mods); load() wipes the inventory.
    let extras = []
    let playerInv = player.inventory
    for (let slot = 0; slot < playerInv.getContainerSize(); slot++) {
      let slotStack = playerInv.getItem(slot)
      if (!slotStack.isEmpty()) extras.push(slotStack.copy())
    }

    playerInv.load(savedSnap.getList('inventory', TAG_COMPOUND))
    let restoreCurios = kiCurios(player)
    if (restoreCurios && savedSnap.contains('curios')) {
      restoreCurios.loadInventory(savedSnap.getList('curios', TAG_COMPOUND))
    }
    allSnaps.remove(restoreUuid)

    extras.forEach(extraStack => player.give(extraStack))
    playerInv.setChanged()
    player.containerMenu.broadcastChanges()
    console.info('[keep_inventory] Restored inventory for ' + player.username)
  } catch (restoreErr) {
    console.error('[keep_inventory] Failed to restore inventory for ' + player.username + ': ' + restoreErr)
  }
}

EntityEvents.death('player', event => {
  let deadPlayer = event.entity
  let deathServer = event.server
  let deathUuid = String(deadPlayer.uuid)
  if (KEEP_INVENTORY_PLAYERS.indexOf(deathUuid) < 0) return

  let deathCurios = null
  let curiosList = null
  try {
    let newSnap = new $CompoundTag()
    let invList = new $ListTag()
    deadPlayer.inventory.save(invList)
    newSnap.put('inventory', invList)

    deathCurios = kiCurios(deadPlayer)
    // saveInventory(true) returns the Curios contents and clears the slots so Curios drops nothing.
    if (deathCurios) {
      curiosList = deathCurios.saveInventory(true)
      newSnap.put('curios', curiosList)
    }

    kiSnapshots(deathServer).put(deathUuid, newSnap)
    deadPlayer.inventory.clearContent()
    console.info('[keep_inventory] Saved inventory for ' + deadPlayer.username)
  } catch (saveErr) {
    // Put Curios back so they drop into the grave with everything else.
    if (deathCurios && curiosList) deathCurios.loadInventory(curiosList)
    kiSnapshots(deathServer).remove(deathUuid)
    console.error('[keep_inventory] Failed to save inventory for ' + deadPlayer.username + ', items drop normally: ' + saveErr)
    return
  }

  // If another mod cancels the death, the player never respawns: give the items straight back.
  deathServer.scheduleInTicks(40, () => {
    let onlinePlayer = deathServer.getPlayer(deadPlayer.uuid)
    if (onlinePlayer) kiRestore(onlinePlayer, deathServer)
  })
})

PlayerEvents.respawned(event => kiRestore(event.player, event.server))

// Covers a restart or disconnect between dying and respawning.
PlayerEvents.loggedIn(event => kiRestore(event.player, event.server))
