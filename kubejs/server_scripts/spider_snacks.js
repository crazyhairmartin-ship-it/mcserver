// Tamed jumping spiders (Critters & Companions) can be healed with spider eyes or rotten flesh, like feeding a wolf meat.
// Taming, breeding and tempting still only use dragonfly wings (the mod's jumping_spider_food tag is untouched).
let SPIDER_SNACKS = ['minecraft:spider_eye', 'minecraft:rotten_flesh']
let SPIDER_SNACK_HEAL = 8 // health points (4 hearts)

ItemEvents.entityInteracted(event => {
  let spider = event.target
  if (spider.type != 'crittersandcompanions:jumping_spider' || !SPIDER_SNACKS.includes(String(event.item.id))) return
  if (!spider.isTame() || !spider.isOwnedBy(event.player)) return
  event.cancel()
  if (spider.health >= spider.maxHealth) return // full: don't waste the snack

  spider.heal(SPIDER_SNACK_HEAL)
  spider.level.broadcastEntityEvent(spider, 7) // heart particles, as when taming
  spider.playSound('minecraft:entity.generic.eat', 1.0, 1.2)
  if (!event.player.isCreative()) event.item.shrink(1)
})
