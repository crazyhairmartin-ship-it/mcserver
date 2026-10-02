// Nightmare fireballs only hurt hostile mobs.
// Nightmares (Ultimate Unicorn Mod) shoot vanilla small fireballs with no owner when they wing-buffet near fire.
// Ownerless small fireballs fizzle out when they'd hit a block (no real fires near builds) or anything that isn't
// a monster (pets, villagers, animals, players). Blaze fireballs have an owner, so they're unaffected.
// Nightmare hoof fire is separately harmless: gentleNightmareFire = true in config/ultimate_unicorn_mod-common.toml.
// Startup script: needs a full restart to change.
let $FriendlySmallFireball = Java.loadClass('net.minecraft.world.entity.projectile.SmallFireball')
let $FriendlyEnemy = Java.loadClass('net.minecraft.world.entity.monster.Enemy')
let $FriendlyEntityHit = Java.loadClass('net.minecraft.world.phys.EntityHitResult')

ForgeEvents.onEvent('net.minecraftforge.event.entity.ProjectileImpactEvent', event => {
  let fireball = event.projectile
  if (!(fireball instanceof $FriendlySmallFireball) || fireball.owner != null) return
  let hit = event.rayTraceResult
  if (hit instanceof $FriendlyEntityHit && hit.entity instanceof $FriendlyEnemy) return
  fireball.discard()
  event.setCanceled(true)
})
