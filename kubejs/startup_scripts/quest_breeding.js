// Hands Forge's BabyEntitySpawnEvent to the quest scripts (global.fqOnBred in server_scripts/quest_npcs.js), for
// "breed" quest tasks. ForgeEvents is only available to startup scripts.
ForgeEvents.onEvent('net.minecraftforge.event.entity.living.BabyEntitySpawnEvent', event => {
  let player = event.getCausedByPlayer()
  if (player && event.getChild() && global.fqOnBred) global.fqOnBred(player, event.getChild())
})
