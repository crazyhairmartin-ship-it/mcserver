// Hands Iron's Spells' SpellOnCastEvent to the quest scripts (global.fqOnCast in server_scripts/quest_npcs.js), for
// "cast" quest tasks. ForgeEvents is only available to startup scripts.
ForgeEvents.onEvent('io.redspace.ironsspellbooks.api.events.SpellOnCastEvent', event => {
  let player = event.getEntity()
  if (!player || player.level.clientSide || !global.fqOnCast) return
  global.fqOnCast(player, String(event.getSpellId()), String(event.getSchoolType().getId()))
})
