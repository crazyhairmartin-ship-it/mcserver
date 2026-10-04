// Drops and pickups of a duplicate item become the group's kept item (the first in global.DUPLICATE_GROUPS), so
// harvests, wild crops, mob drops, fish and chest loot only ever hand out one version.

const KEPT = {}
global.DUPLICATE_GROUPS.forEach(group => {
  group.items.slice(1).forEach(itemId => { KEPT[itemId] = group.items[0] })
})

function keptStack(stack) {
  let kept = KEPT[stack.id]
  return kept ? Item.of(kept, stack.count, stack.nbt) : null
}

// Items dropped into the world (block drops, mob loot, fishing)
EntityEvents.spawned('minecraft:item', event => {
  let converted = keptStack(event.entity.item)
  if (converted) event.entity.item = converted
})

// Anything that reaches a player's inventory another way (chests, trades, other mods)
PlayerEvents.inventoryChanged(event => {
  if (!KEPT[event.item.id]) return
  let inv = event.player.inventory
  for (let i = 0; i < inv.containerSize; i++) {
    let converted = keptStack(inv.getItem(i))
    if (converted) inv.setItem(i, converted)
  }
})
