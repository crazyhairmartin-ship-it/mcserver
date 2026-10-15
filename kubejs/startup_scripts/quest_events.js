// Hands Forge events to the quest scripts (server_scripts/quest_npcs.js) for "make", "trade" and "sleep" quest tasks.
// ForgeEvents is only available to startup scripts.
function questEventItem(stack) {
  return { id: String(stack.id), count: stack.getCount() }
}
ForgeEvents.onEvent('net.minecraftforge.event.entity.player.PlayerEvent$ItemCraftedEvent', event => {
  if (global.fqOnMade) global.fqOnMade(event.getEntity(), questEventItem(event.getCrafting()), 'craft')
})
ForgeEvents.onEvent('net.minecraftforge.event.entity.player.PlayerEvent$ItemSmeltedEvent', event => {
  if (global.fqOnMade) global.fqOnMade(event.getEntity(), questEventItem(event.getSmelting()), 'smelt')
})
ForgeEvents.onEvent('net.minecraftforge.event.brewing.PlayerBrewedPotionEvent', event => {
  if (global.fqOnMade) global.fqOnMade(event.getEntity(), questEventItem(event.getStack()), 'brew')
})
ForgeEvents.onEvent('net.minecraftforge.event.entity.player.TradeWithVillagerEvent', event => {
  if (global.fqOnTrade) global.fqOnTrade(event.getEntity(), event.getAbstractVillager(), questEventItem(event.getMerchantOffer().getResult()))
})
ForgeEvents.onEvent('net.minecraftforge.event.entity.player.PlayerWakeUpEvent', event => {
  // waking up in the morning, not because something disturbed you
  if (!event.wakeImmediately() && global.fqOnSlept) global.fqOnSlept(event.getEntity())
})
