// Whales can't destroy boats or ships.
// Alex's Mobs cachalot whales ram their target and, if that target is sitting in a boat, delete the boat
// outright (Small Ships galleys included, since its ships are boats under the hood). That can't be
// intercepted, so whales never target anyone riding a boat or ship: the target is refused when it's
// picked (here), and dropped if the target boards mid-chase (server_scripts/whale_boat_guard.js).
// Startup script because this is a Forge event. Angry whales breaking wooden blocks is turned off
// separately in config/alexsmobs.toml (cachalotDestruction = false).

const $Boat = Java.loadClass('net.minecraft.world.entity.vehicle.Boat')
const $Cachalot = Java.loadClass('com.github.alexthe666.alexsmobs.entity.EntityCachalotWhale')

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingChangeTargetEvent', event => {
  let newTarget = event.getNewTarget()
  if (event.getEntity() instanceof $Cachalot && newTarget != null && newTarget.getVehicle() instanceof $Boat) {
    event.setCanceled(true)
  }
})
