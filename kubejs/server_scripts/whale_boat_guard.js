// Companion to startup_scripts/protect_boats.js: cachalot whales ram their target and delete the boat
// the target is sitting in. protect_boats.js stops whales from picking a boat rider as a target; this
// drops the target if someone boards a boat mid-chase. Checked once a second, only for whales.

let $WhaleGuardBoat = Java.loadClass('net.minecraft.world.entity.vehicle.Boat')

ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % 20 != 0) return

  // Cachalots are overworld ocean mobs. KubeJS 6's getEntities() takes no selector, so filter by type.
  server.overworld().getEntities().forEach(entity => {
    if (entity.type != 'alexsmobs:cachalot_whale') return
    let target = entity.getTarget()
    if (target != null && target.getVehicle() instanceof $WhaleGuardBoat) entity.setTarget(null)
  })
})
