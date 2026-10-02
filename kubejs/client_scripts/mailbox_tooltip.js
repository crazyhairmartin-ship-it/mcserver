// Shows a mailbox's wood (fotfmail add-on: item NBT BlockStateTag.wood) under its name.
let MAILBOX_WOOD_PLANKS = {}
global.MAILBOX_WOODS.forEach(([wood, planks]) => { MAILBOX_WOOD_PLANKS[wood] = planks })

ItemEvents.tooltip(event => {
  event.addAdvanced('endermail:locker', (item, advanced, text) => {
    let wood = item.nbt ? item.nbt.getCompound('BlockStateTag').getString('wood') : ''
    let planks = MAILBOX_WOOD_PLANKS[wood || 'oak']
    if (!planks) return
    text.add(1, Text.gray(Item.of(planks).hoverName.string.replace(' Planks', '')))
  })
})
