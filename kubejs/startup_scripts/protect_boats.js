// Mobs can't break boats: their projectiles pass through, their explosions don't hurt boats,
// and cachalot whales won't ram anyone who's aboard a boat or ship.
// Covers vanilla boats and chest boats, plus Small Ships (its ships are boats under the hood).
// Players can still break boats: punching, their own arrows/tridents/cannonballs, and TNT they lit.
// Startup script because these are Forge events (boats aren't living, so EntityEvents.hurt never fires for them).

const $Boat = Java.loadClass('net.minecraft.world.entity.vehicle.Boat')
const $Player = Java.loadClass('net.minecraft.world.entity.player.Player')
const $EntityHitResult = Java.loadClass('net.minecraft.world.phys.EntityHitResult')
const $ImpactResult = Java.loadClass('net.minecraftforge.event.entity.ProjectileImpactEvent$ImpactResult')

// Skeleton arrows, blaze/ghast fireballs, modded mob projectiles: fly through the boat instead of hitting it.
ForgeEvents.onEvent('net.minecraftforge.event.entity.ProjectileImpactEvent', event => {
  let hit = event.getRayTraceResult()
  if (!(hit instanceof $EntityHitResult)) return
  if (!(hit.getEntity() instanceof $Boat)) return
  if (event.getProjectile().getOwner() instanceof $Player) return
  event.setImpactResult($ImpactResult.SKIP_ENTITY)
})

// Alex's Mobs cachalot whales ram their target and, if that target is sitting in a boat, delete the boat
// outright (Small Ships galleys included). That can't be intercepted, so whales just never target anyone
// riding a boat or ship: refuse the target when it's picked, and drop it if the target boards mid-chase.
const $Cachalot = Java.loadClass('com.github.alexthe666.alexsmobs.entity.EntityCachalotWhale')

function isAboard(entity) {
  return entity != null && entity.getVehicle() instanceof $Boat
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingChangeTargetEvent', event => {
  if (event.getEntity() instanceof $Cachalot && isAboard(event.getNewTarget())) event.setCanceled(true)
})

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingEvent$LivingTickEvent', event => {
  let whale = event.getEntity()
  if (whale instanceof $Cachalot && isAboard(whale.getTarget())) whale.setTarget(null)
})

// Creepers, ghast fireballs, beds, anything not lit by a player: boats are taken out of the blast.
ForgeEvents.onEvent('net.minecraftforge.event.level.ExplosionEvent$Detonate', event => {
  if (event.getExplosion().getIndirectSourceEntity() instanceof $Player) return
  let it = event.getAffectedEntities().iterator()
  while (it.hasNext()) {
    if (it.next() instanceof $Boat) it.remove()
  }
})
