// Mobs can't break boats: their projectiles pass through, and their explosions don't hurt boats.
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

// Creepers, ghast fireballs, beds, anything not lit by a player: boats are taken out of the blast.
ForgeEvents.onEvent('net.minecraftforge.event.level.ExplosionEvent$Detonate', event => {
  if (event.getExplosion().getIndirectSourceEntity() instanceof $Player) return
  let it = event.getAffectedEntities().iterator()
  while (it.hasNext()) {
    if (it.next() instanceof $Boat) it.remove()
  }
})
