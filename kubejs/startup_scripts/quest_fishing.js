// Hands Forge's ItemFishedEvent to the quest scripts (global.fqOnFished in server_scripts/quest_givers.js), which give
// prize fish for open fishing quests. ForgeEvents is only available to startup scripts.
ForgeEvents.onEvent('net.minecraftforge.event.entity.player.ItemFishedEvent', event => {
  if (global.fqOnFished) global.fqOnFished(event.getEntity())
})
