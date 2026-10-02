// Non-hostile mobs inside claimed land never despawn.
// Every 30 seconds, any loaded mob standing in a claimed chunk (Open Parties and Claims) is marked
// persistent, the same thing a name tag does. It then stays even if it later wanders out of the claim.
// Skipped: hostile mobs (anything that's an Enemy), fish, which would otherwise pile up in ponds, and loud bugs
// (KEEP_MOBS_SKIP_TYPES) that would otherwise pile up and buzz forever inside houses.
// (KubeJS's entity.getType() returns the id string, so this checks Java classes instead of mob categories.)

let KEEP_MOBS_INTERVAL_TICKS = 600
let KEEP_MOBS_SKIP_TYPES = ['crittersandcompanions:dragonfly']

let $KeepOpenPAC = Java.loadClass('xaero.pac.common.server.api.OpenPACServerAPI')
let $KeepMob = Java.loadClass('net.minecraft.world.entity.Mob')
let $KeepEnemy = Java.loadClass('net.minecraft.world.entity.monster.Enemy')
let $KeepFish = Java.loadClass('net.minecraft.world.entity.animal.AbstractFish')

ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % KEEP_MOBS_INTERVAL_TICKS != 0) return

  let claims = $KeepOpenPAC.get(server).getServerClaimsManager()
  server.getAllLevels().forEach(level => {
    let dimension = level.dimension
    level.getEntities().forEach(entity => {
      if (!(entity instanceof $KeepMob) || entity.isPersistenceRequired()) return
      if (entity instanceof $KeepEnemy || entity instanceof $KeepFish) return
      if (KEEP_MOBS_SKIP_TYPES.includes(String(entity.type))) return
      if (claims.get(dimension, entity.blockPosition()) != null) entity.setPersistenceRequired()
    })
  })
})
