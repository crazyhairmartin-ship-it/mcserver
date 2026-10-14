// Ender Mail's carriers are drawn at 60% size (Pehkui), about as tall as a player, so they look like the village
// post rather than a looming enderman. Set the moment they appear, with no easing, so they never visibly shrink.
// Carriers only live for one delivery, so the size isn't saved (no "persist").
const MAIL_CARRIER_SCALE = 0.6

EntityEvents.spawned('endermail:ender_mailman', event => {
  let entity = event.entity
  if (entity.level.clientSide) return
  let server = event.server
  // the entity isn't in the world yet when this fires; size it on the next tick
  server.scheduleInTicks(1, () => {
    server.runCommandSilent('scale delay set pehkui:base 0 ' + entity.uuid)
    server.runCommandSilent('scale set pehkui:base ' + MAIL_CARRIER_SCALE + ' ' + entity.uuid)
  })
})
