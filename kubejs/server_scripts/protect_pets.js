// Players can't hurt pets that belong to someone else (melee, arrows, spells, sweep attacks).
// Owners can still hurt their own pets; wild animals are unaffected.
// Works for anything with an owner: wolves, cats, parrots, tamed horses/unicorns, modded pets.

EntityEvents.hurt(event => {
  let attacker = event.source.player // the player behind the damage, including their projectiles
  if (!attacker) return

  let pet = event.entity
  if (typeof pet.getOwnerUUID !== 'function') return
  let ownerUuid = pet.getOwnerUUID()
  if (ownerUuid == null || String(ownerUuid) === String(attacker.uuid)) return

  event.cancel()
  attacker.setStatusMessage(Text.red("That's someone else's pet!"))
})
