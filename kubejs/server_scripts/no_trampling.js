// Farmland never gets trampled: jumping or falling on it (players, pets, mobs) leaves the soil and crops alone.

BlockEvents.farmlandTrampled(event => {
  event.cancel()
})
